#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Clear installed project-local skills from one or more agent target dirs.

Usage:
  scripts/clear-skills.sh [options] [skill-name ...]

Options:
  --project PATH       Target project root (default: current directory)
  --manifest PATH      Manifest file (repeatable). If omitted, auto-uses:
                      <project>/.agents/skills.core.txt + skills.task.txt (if present)
  --targets LIST       Comma-separated targets: codex,claude,cursor,agents
                      (default: codex)
  --codex-home PATH    Codex home for codex target (default: <project>/.codex)
  --all                Remove all installed skills under selected targets
  --yes                Skip confirmation prompt
  --dry-run            Print what would be removed, do not delete
  -h, --help           Show this help

Behavior:
  - If skill names are passed as args, manifest is ignored.
  - Without args and without --all, reads merged manifest list.
  - Manifest supports blank lines and lines starting with '#'.

Examples:
  scripts/clear-skills.sh --project /path/to/app
  scripts/clear-skills.sh --project /path/to/app --targets codex,claude --all --yes
  scripts/clear-skills.sh --project /path/to/app react-best-practices
EOF
}

PROJECT_DIR="$(pwd)"
CODEX_HOME=""
TARGETS_CSV="codex"
REMOVE_ALL=0
ASSUME_YES=0
DRY_RUN=0
declare -a MANIFEST_PATHS=()
declare -a TARGETS=()
declare -a CLI_SKILLS=()

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

while (($# > 0)); do
  case "$1" in
    --project)
      PROJECT_DIR="$2"
      shift 2
      ;;
    --manifest)
      MANIFEST_PATHS+=("$2")
      shift 2
      ;;
    --targets)
      TARGETS_CSV="$2"
      shift 2
      ;;
    --codex-home)
      CODEX_HOME="$2"
      shift 2
      ;;
    --all)
      REMOVE_ALL=1
      shift
      ;;
    --yes)
      ASSUME_YES=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
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
if [[ -z "${CODEX_HOME}" ]]; then
  CODEX_HOME="${PROJECT_DIR}/.codex"
fi
parse_targets "${TARGETS_CSV}"

declare -a SELECTED_SKILLS=()
if ((REMOVE_ALL == 1)); then
  :
elif ((${#CLI_SKILLS[@]} > 0)); then
  SELECTED_SKILLS=("${CLI_SKILLS[@]}")
else
  if ((${#MANIFEST_PATHS[@]} == 0)); then
    [[ -f "${PROJECT_DIR}/.agents/skills.core.txt" ]] && MANIFEST_PATHS+=("${PROJECT_DIR}/.agents/skills.core.txt")
    [[ -f "${PROJECT_DIR}/.agents/skills.task.txt" ]] && MANIFEST_PATHS+=("${PROJECT_DIR}/.agents/skills.task.txt")
  fi

  if ((${#MANIFEST_PATHS[@]} == 0)); then
    echo "No manifest found." >&2
    echo "Expected one of:" >&2
    echo "  ${PROJECT_DIR}/.agents/skills.core.txt" >&2
    echo "  ${PROJECT_DIR}/.agents/skills.task.txt" >&2
    echo "Pass skill names as args, use --all, or use --manifest." >&2
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
      if ((${#SELECTED_SKILLS[@]} == 0)) || ! contains "${line}" "${SELECTED_SKILLS[@]}"; then
        SELECTED_SKILLS+=("${line}")
      fi
    done < "${manifest}"
  done
fi

declare -a REMOVALS=()
if ((REMOVE_ALL == 1)); then
  for target in "${TARGETS[@]}"; do
    root="$(dest_for_target "$target")"
    [[ -d "${root}" ]] || continue
    while IFS= read -r skill; do
      [[ -n "$skill" ]] || continue
      REMOVALS+=("${target}:${skill}")
    done < <(find "${root}" -mindepth 1 -maxdepth 1 \( -type d -o -type l \) -exec basename {} \; | sort)
  done
else
  if ((${#SELECTED_SKILLS[@]} == 0)); then
    echo "No skills selected for removal."
    exit 0
  fi
  for target in "${TARGETS[@]}"; do
    root="$(dest_for_target "$target")"
    [[ -d "${root}" ]] || continue
    for skill in "${SELECTED_SKILLS[@]}"; do
      path="${root}/${skill}"
      if [[ -d "${path}" || -L "${path}" ]]; then
        REMOVALS+=("${target}:${skill}")
      fi
    done
  done
fi

if ((${#REMOVALS[@]} == 0)); then
  echo "No matching installed skills found for selected targets."
  exit 0
fi

printf 'Skills selected for removal (%d):\n' "${#REMOVALS[@]}"
printf '  - %s\n' "${REMOVALS[@]}"

if ((ASSUME_YES == 0)); then
  read -r -p "Remove these entries? [y/N] " reply
  case "${reply}" in
    y|Y|yes|YES) ;;
    *)
      echo "Aborted."
      exit 0
      ;;
  esac
fi

if ((DRY_RUN == 1)); then
  echo "Dry run only. No files removed."
  exit 0
fi

for entry in "${REMOVALS[@]}"; do
  target="${entry%%:*}"
  skill="${entry#*:}"
  root="$(dest_for_target "$target")"
  path="${root}/${skill}"
  if [[ -d "${path}" || -L "${path}" ]]; then
    rm -rf "${path}"
  fi
done

echo "Removed ${#REMOVALS[@]} entries from selected targets."
echo "Done. Restart your agent tools in ${PROJECT_DIR} to refresh loaded skills."
