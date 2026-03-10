#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Load skills from this registry into one or more project-local agent skill dirs.

Usage:
  scripts/load-skills.sh [options] [skill-name ...]

Options:
  --project PATH       Target project root (default: current directory)
  --skills-repo PATH   Skills registry root (default: parent of this script)
  --manifest PATH      Manifest file (repeatable). If omitted, auto-uses:
                      <project>/.agents/skills.core.txt + skills.task.txt (if present)
  --lockfile PATH      Skill lock file path (default: <project>/.agents/skills.lock.json)
  --require-lock       Require lockfile and enforce requested skills are pinned in it
  --strict-manifest    Require explicit --manifest when not passing skill args
  --targets LIST       Comma-separated targets: codex,claude,cursor,agents
                      (default: codex)
  --codex-home PATH    Codex home for codex target (default: <project>/.codex)
  --require-domain-coverage
                      Fail if @domains declares uncovered domains
  --ensure-gitignore   Ensure target .gitignore contains .claude/, .codex/, .agents/
  --force              Overwrite already-installed skills in destination
  --symlink            Symlink skills instead of copying with rsync
  -h, --help           Show this help

Behavior:
  - If skill names are passed as args, manifest is ignored.
  - Manifest supports blank lines and lines starting with '#'.
  - Destinations:
    codex  -> <codex-home>/skills
    claude -> <project>/.claude/skills
    cursor -> <project>/.cursor/skills
    agents -> <project>/.agents/skills

Examples:
  scripts/load-skills.sh --project /path/to/app
  scripts/load-skills.sh --project /path/to/app --targets codex,claude,cursor
  scripts/load-skills.sh --project /path/to/app react-best-practices e2e-testing
EOF
}

PROJECT_DIR="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_REPO="$(cd "${SCRIPT_DIR}/.." && pwd)"
CODEX_HOME=""
FORCE=0
USE_SYMLINK=0
STRICT_MANIFEST=0
REQUIRE_DOMAIN_COVERAGE=0
ENSURE_GITIGNORE=0
TARGETS_CSV="codex"
LOCKFILE_PATH=""
REQUIRE_LOCK=0
declare -a MANIFEST_PATHS=()
declare -a TARGETS=()
declare -a CLI_SKILLS=()
declare -a DECLARED_DOMAINS=()
declare -a LOCKED_SKILLS=()
declare -a INVALID_LOCK_ENTRIES=()

contains() {
  local needle="$1"
  shift
  local item
  for item in "$@"; do
    [[ "$item" == "$needle" ]] && return 0
  done
  return 1
}

trim() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

resolve_skill_src() {
  local repo_root="$1"
  local skill="$2"

  if [[ -d "${repo_root}/skills/${skill}" ]]; then
    printf '%s' "${repo_root}/skills/${skill}"
    return 0
  fi

  if [[ -d "${repo_root}/${skill}" ]]; then
    printf '%s' "${repo_root}/${skill}"
    return 0
  fi

  printf '%s' "${repo_root}/skills/${skill}"
}

parse_targets() {
  local csv="$1"
  local old_ifs="$IFS"
  IFS=',' read -r -a TARGETS <<< "$csv"
  IFS="$old_ifs"

  local t
  for i in "${!TARGETS[@]}"; do
    t="$(trim "${TARGETS[$i]}")"
    TARGETS[$i]="$t"
  done

  if ((${#TARGETS[@]} == 0)); then
    echo "No targets provided." >&2
    exit 1
  fi

  for t in "${TARGETS[@]}"; do
    case "$t" in
      codex|claude|cursor|agents) ;;
      *)
        echo "Invalid target: $t" >&2
        echo "Valid targets: codex, claude, cursor, agents" >&2
        exit 1
        ;;
    esac
  done
}

doc_url_for_domain() {
  local domain="$1"
  case "$domain" in
    llamaindex) printf '%s' "https://docs.llamaindex.ai" ;;
    qdrant) printf '%s' "https://qdrant.tech/documentation" ;;
    firebase) printf '%s' "https://firebase.google.com/docs" ;;
    supabase) printf '%s' "https://supabase.com/docs" ;;
    konva) printf '%s' "https://konvajs.org/docs/" ;;
    fastapi) printf '%s' "https://fastapi.tiangolo.com/" ;;
    *)
      return 1
      ;;
  esac
}

domain_covered_by_skill() {
  local domain="$1"
  local skill="$2"
  local skill_lc
  skill_lc="$(printf '%s' "$skill" | tr '[:upper:]' '[:lower:]')"

  # Direct token match is stricter than substring matching.
  local normalized
  normalized="$(printf '%s' "$skill_lc" | tr '_/' '--')"
  old_ifs="$IFS"
  IFS='-' read -r -a skill_tokens <<< "$normalized"
  IFS="$old_ifs"
  for token in "${skill_tokens[@]}"; do
    [[ -z "$token" ]] && continue
    if [[ "$token" == "$domain" ]]; then
      return 0
    fi
  done

  # Keep a small alias map for common stacks with no exact skill names.
  if [[ "$skill_lc" == "$domain"-* ]]; then
    return 0
  fi

  case "$domain" in
    llamaindex)
      [[ "$skill_lc" == rag-* || "$skill_lc" == *embedding* || "$skill_lc" == *similarity-search* || "$skill_lc" == *vector-index* || "$skill_lc" == *hybrid-search* ]]
      return
      ;;
    qdrant)
      [[ "$skill_lc" == *vector-index* || "$skill_lc" == *similarity-search* || "$skill_lc" == *hybrid-search* ]]
      return
      ;;
    firebase)
      [[ "$skill_lc" == *auth* || "$skill_lc" == *security* ]]
      return
      ;;
    *)
      return 1
      ;;
  esac
}

dest_for_target() {
  local target="$1"
  case "$target" in
    codex) printf '%s' "${CODEX_HOME}/skills" ;;
    claude) printf '%s' "${PROJECT_DIR}/.claude/skills" ;;
    cursor) printf '%s' "${PROJECT_DIR}/.cursor/skills" ;;
    agents) printf '%s' "${PROJECT_DIR}/.agents/skills" ;;
    *)
      echo "Unknown target: $target" >&2
      exit 1
      ;;
  esac
}

load_lockfile_entries() {
  local lockfile="$1"
  python3 - "$lockfile" <<'PY'
import json
import sys
from pathlib import Path

lockfile = Path(sys.argv[1])
obj = json.loads(lockfile.read_text(encoding="utf-8"))
skills = obj.get("skills", [])
if not isinstance(skills, list):
    print("ERROR\tLockfile key 'skills' must be an array", flush=True)
    raise SystemExit(2)

for item in skills:
    if not isinstance(item, dict):
        print("ERROR\tLockfile skill entry must be an object", flush=True)
        raise SystemExit(2)
    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        print("ERROR\tLockfile skill entry missing non-empty 'name'", flush=True)
        raise SystemExit(2)
    source = item.get("source", "local")
    if not isinstance(source, str) or not source.strip():
        source = "local"
    rev = item.get("rev", "")
    if rev is None:
        rev = ""
    if not isinstance(rev, str):
        rev = str(rev)
    allow_scripts = item.get("allowScripts", False)
    allow_scripts = "true" if bool(allow_scripts) else "false"
    print(f"{name}\t{source}\t{rev}\t{allow_scripts}", flush=True)
PY
}

while (($# > 0)); do
  case "$1" in
    --project)
      PROJECT_DIR="$2"
      shift 2
      ;;
    --skills-repo)
      SKILLS_REPO="$2"
      shift 2
      ;;
    --manifest)
      MANIFEST_PATHS+=("$2")
      shift 2
      ;;
    --lockfile)
      LOCKFILE_PATH="$2"
      shift 2
      ;;
    --require-lock)
      REQUIRE_LOCK=1
      shift
      ;;
    --strict-manifest)
      STRICT_MANIFEST=1
      shift
      ;;
    --targets)
      TARGETS_CSV="$2"
      shift 2
      ;;
    --codex-home)
      CODEX_HOME="$2"
      shift 2
      ;;
    --require-domain-coverage)
      REQUIRE_DOMAIN_COVERAGE=1
      shift
      ;;
    --ensure-gitignore)
      ENSURE_GITIGNORE=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --symlink)
      USE_SYMLINK=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      CLI_SKILLS+=("$1")
      shift
      ;;
  esac
done

PROJECT_DIR="$(cd "${PROJECT_DIR}" && pwd)"
SKILLS_REPO="$(cd "${SKILLS_REPO}" && pwd)"
if [[ -z "${CODEX_HOME}" ]]; then
  CODEX_HOME="${PROJECT_DIR}/.codex"
fi
if [[ -z "${LOCKFILE_PATH}" ]]; then
  LOCKFILE_PATH="${PROJECT_DIR}/.agents/skills.lock.json"
fi
parse_targets "${TARGETS_CSV}"

if ((ENSURE_GITIGNORE == 1)); then
  gitignore_path="${PROJECT_DIR}/.gitignore"
  touch "${gitignore_path}"
  for entry in ".claude/" ".codex/" ".agents/"; do
    if ! grep -Fxq "${entry}" "${gitignore_path}"; then
      printf '%s\n' "${entry}" >> "${gitignore_path}"
    fi
  done
fi

for target in "${TARGETS[@]}"; do
  mkdir -p "$(dest_for_target "$target")"
done

declare -a SKILLS=()
if ((${#CLI_SKILLS[@]} > 0)); then
  SKILLS=("${CLI_SKILLS[@]}")
else
  if ((${#MANIFEST_PATHS[@]} == 0)); then
    if ((STRICT_MANIFEST == 1)); then
      echo "--strict-manifest requires explicit --manifest when no skill args are passed." >&2
      exit 1
    fi
    [[ -f "${PROJECT_DIR}/.agents/skills.core.txt" ]] && MANIFEST_PATHS+=("${PROJECT_DIR}/.agents/skills.core.txt")
    [[ -f "${PROJECT_DIR}/.agents/skills.task.txt" ]] && MANIFEST_PATHS+=("${PROJECT_DIR}/.agents/skills.task.txt")
  fi

  if ((${#MANIFEST_PATHS[@]} == 0)); then
    echo "No manifest found." >&2
    echo "Expected one of:" >&2
    echo "  ${PROJECT_DIR}/.agents/skills.core.txt" >&2
    echo "  ${PROJECT_DIR}/.agents/skills.task.txt" >&2
    echo "Pass skill names as args or use --manifest." >&2
    exit 1
  fi

  for manifest in "${MANIFEST_PATHS[@]}"; do
    if [[ ! -f "${manifest}" ]]; then
      echo "Manifest not found: ${manifest}" >&2
      exit 1
    fi
    while IFS= read -r line || [[ -n "$line" ]]; do
      line="$(trim "$line")"
      [[ -z "${line}" ]] && continue
      [[ "${line}" == \#* ]] && continue
      if [[ "${line}" == @domains:* ]]; then
        domains_csv="$(trim "${line#@domains:}")"
        if [[ -n "${domains_csv}" ]]; then
          old_ifs="$IFS"
          IFS=',' read -r -a parsed_domains <<< "${domains_csv}"
          IFS="$old_ifs"
          for domain in "${parsed_domains[@]}"; do
            domain="$(trim "$domain")"
            domain="$(printf '%s' "$domain" | tr '[:upper:]' '[:lower:]')"
            [[ -z "${domain}" ]] && continue
            if ((${#DECLARED_DOMAINS[@]} == 0)) || ! contains "${domain}" "${DECLARED_DOMAINS[@]}"; then
              DECLARED_DOMAINS+=("${domain}")
            fi
          done
        fi
        continue
      fi
      if ((${#SKILLS[@]} == 0)) || ! contains "${line}" "${SKILLS[@]}"; then
        SKILLS+=("${line}")
      fi
    done < "${manifest}"
  done
fi

if ((${#SKILLS[@]} == 0)); then
  echo "No skills requested."
  exit 0
fi

if ((REQUIRE_LOCK == 1)); then
  if [[ ! -f "${LOCKFILE_PATH}" ]]; then
    echo "Lockfile required but not found: ${LOCKFILE_PATH}" >&2
    exit 1
  fi

  while IFS=$'\t' read -r lock_name lock_source lock_rev lock_allow_scripts; do
    [[ -n "${lock_name}" ]] || continue
    if [[ "${lock_name}" == ERROR ]]; then
      echo "Invalid lockfile: ${lock_source}" >&2
      exit 1
    fi
    LOCKED_SKILLS+=("${lock_name}")

    source_lc="$(printf '%s' "${lock_source}" | tr '[:upper:]' '[:lower:]')"
    if [[ "${source_lc}" != "local" ]]; then
      if [[ ! "${lock_rev}" =~ ^[0-9a-f]{40}$ ]]; then
        INVALID_LOCK_ENTRIES+=("${lock_name} (source=${lock_source}, rev='${lock_rev}')")
      fi
    fi
  done < <(load_lockfile_entries "${LOCKFILE_PATH}")

  if ((${#INVALID_LOCK_ENTRIES[@]} > 0)); then
    echo "Lockfile validation failed. Non-local sources must use a full 40-char SHA in 'rev'." >&2
    printf '  - %s\n' "${INVALID_LOCK_ENTRIES[@]}" >&2
    exit 1
  fi

  declare -a UNLOCKED_REQUESTS=()
  for skill in "${SKILLS[@]}"; do
    if ! contains "${skill}" "${LOCKED_SKILLS[@]}"; then
      UNLOCKED_REQUESTS+=("${skill}")
    fi
  done
  if ((${#UNLOCKED_REQUESTS[@]} > 0)); then
    echo "Requested skills are not pinned in lockfile: ${LOCKFILE_PATH}" >&2
    printf '  - %s\n' "${UNLOCKED_REQUESTS[@]}" >&2
    exit 1
  fi
fi

declare -a MISSING_SKILLS=()
declare -a INVALID_SKILLS=()
for skill in "${SKILLS[@]}"; do
  src="$(resolve_skill_src "${SKILLS_REPO}" "${skill}")"
  if [[ ! -d "${src}" ]]; then
    MISSING_SKILLS+=("${skill}")
    continue
  fi
  if [[ ! -f "${src}/SKILL.md" ]]; then
    INVALID_SKILLS+=("${skill}")
  fi
done

if ((${#MISSING_SKILLS[@]} > 0 || ${#INVALID_SKILLS[@]} > 0)); then
  echo "Skill preflight failed." >&2
  if ((${#MISSING_SKILLS[@]} > 0)); then
    printf 'Missing skills in registry (%d):\n' "${#MISSING_SKILLS[@]}" >&2
    printf '  - %s\n' "${MISSING_SKILLS[@]}" >&2
  fi
  if ((${#INVALID_SKILLS[@]} > 0)); then
    printf 'Invalid skills (SKILL.md missing) (%d):\n' "${#INVALID_SKILLS[@]}" >&2
    printf '  - %s\n' "${INVALID_SKILLS[@]}" >&2
  fi
  echo "Install or fix the listed skills in ${SKILLS_REPO}, then rerun load-skills.sh." >&2
  echo "Tip: review external skills with the AGENTS.md security gate before adding them." >&2
  exit 1
fi

declare -a UNCOVERED_DOMAINS=()
if ((${#DECLARED_DOMAINS[@]} > 0)); then
  for domain in "${DECLARED_DOMAINS[@]}"; do
    covered=0
    for skill in "${SKILLS[@]}"; do
      if domain_covered_by_skill "${domain}" "${skill}"; then
        covered=1
        break
      fi
    done
    if ((covered == 0)); then
      UNCOVERED_DOMAINS+=("${domain}")
    fi
  done

  if ((${#UNCOVERED_DOMAINS[@]} > 0)); then
    printf 'Potentially uncovered declared domains (%d):\n' "${#UNCOVERED_DOMAINS[@]}"
    printf '  - %s\n' "${UNCOVERED_DOMAINS[@]}"
    echo "Review requirements and add matching skills or proceed with official docs for gaps."
    for domain in "${UNCOVERED_DOMAINS[@]}"; do
      if url="$(doc_url_for_domain "${domain}")"; then
        echo "  ${domain}: ${url}"
      fi
    done
    if ((REQUIRE_DOMAIN_COVERAGE == 1)); then
      echo "--require-domain-coverage is enabled; aborting due to uncovered declared domains." >&2
      exit 1
    fi
  fi
fi

declare -a INSTALLED=()
declare -a SKIPPED=()
for skill in "${SKILLS[@]}"; do
  src="$(resolve_skill_src "${SKILLS_REPO}" "${skill}")"

  for target in "${TARGETS[@]}"; do
    root="$(dest_for_target "$target")"
    dst="${root}/${skill}"
    target_key="${target}"

    if [[ -e "${dst}" || -L "${dst}" ]]; then
      if ((FORCE == 0)); then
        SKIPPED+=("${target_key}:${skill}")
        continue
      fi
      rm -rf "${dst}"
    fi

    mkdir -p "$(dirname "${dst}")"
    if ((USE_SYMLINK == 1)); then
      ln -s "${src}" "${dst}"
    else
      rsync -a "${src}/" "${dst}/"
    fi
    INSTALLED+=("${target_key}:${skill}")
  done
done

if ((${#INSTALLED[@]} > 0)); then
  printf 'Installed entries (%d):\n' "${#INSTALLED[@]}"
  printf '  - %s\n' "${INSTALLED[@]}"
fi
if ((${#SKIPPED[@]} > 0)); then
  printf 'Skipped existing entries (%d):\n' "${#SKIPPED[@]}"
  printf '  - %s\n' "${SKIPPED[@]}"
  echo "Use --force to overwrite skipped skills."
fi

echo "Done. Skills were installed into project-local directories under: ${PROJECT_DIR}"
echo "Restart the agent session for that project (open the session in ${PROJECT_DIR}) to load updated skills."
