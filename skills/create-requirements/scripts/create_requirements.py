#!/usr/bin/env python3
"""Create requirements.pdf from local project and optional GitHub evidence."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {
    ".cache",
    ".claude",
    ".codex",
    ".cursor",
    ".git",
    ".gbrain",
    ".hermes",
    ".next",
    ".openclaw",
    ".venv",
    "Library",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

SOURCE_PATTERNS = [
    re.compile(r"(^|/).*requirements[^/]*\.pdf$", re.I),
    re.compile(r"(^|/)(docs/)?requirements[^/]*\.(md|txt)$", re.I),
    re.compile(r"(^|/)(docs/)?prd[^/]*\.(md|txt)$", re.I),
    re.compile(r"(^|/)(docs/)?product[-_ ]?requirements[^/]*\.(md|txt)$", re.I),
    re.compile(r"(^|/)(docs/)?spec[^/]*\.(md|txt)$", re.I),
    re.compile(r"(^|/)(docs/)?brief[^/]*\.(md|txt)$", re.I),
    re.compile(r"(^|/)assignment[^/]*\.(md|txt)$", re.I),
    re.compile(r"(^|/)(docs/)?tasks?[^/]*\.(md|txt)$", re.I),
    re.compile(r"(^|/)PRESEARCH\.(md|txt)$", re.I),
    re.compile(r"(^|/)PLAN\.(md|txt)$", re.I),
    re.compile(r"(^|/)TODO\.(md|txt)$", re.I),
    re.compile(r"(^|/)README\.(md|txt)$", re.I),
    re.compile(r"(^|/)CHANGELOG\.(md|txt)$", re.I),
]

REQUIREMENT_RE = re.compile(
    r"(☐|☑|□|■|\[[ xX]\]|\bmust\b|\bshould\b|\bshall\b|\bneed(?:s|ed)?\b|"
    r"\brequir(?:e|es|ed|ement|ements)\b|\bacceptance\b|\bcriteria\b|"
    r"\buser story\b|\bfeature\b|\bconstraint\b|\bnon-goal\b|\bship\b|"
    r"\blaunch\b|\bdeploy\b|\bcomplete\b|\bdone\b)",
    re.I,
)
COMPLETE_RE = re.compile(r"\b(shipped|complete|completed|done|launched|deployed|released)\b", re.I)
ACTIVE_RE = re.compile(r"\b(wip|blocked|in progress|todo|backlog|remaining)\b", re.I)


@dataclass
class Requirement:
    text: str
    source: str
    line: int | None = None


@dataclass
class Project:
    name: str
    source: str
    kind: str
    status: str = "unknown"
    updated_at: str = ""
    description: str = ""
    requirement_sources: list[str] = field(default_factory=list)
    requirements: list[Requirement] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    canonical_requirements_pdf: str = ""


def run_json(cmd: list[str]) -> object | None:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def is_requirement_source(path: Path | str) -> bool:
    rel = str(path).replace(os.sep, "/")
    if rel.lower().endswith("requirements.txt"):
        return False
    return any(pattern.search(rel) for pattern in SOURCE_PATTERNS)


def iter_project_dirs(root: Path, max_depth: int) -> Iterable[Path]:
    root = root.expanduser().resolve()
    if not root.exists():
        return
    stack = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        if current.name in SKIP_DIRS or current.name.startswith("."):
            continue
        if (current / ".git").is_dir():
            yield current
            continue
        if current != root and iter_candidate_files(current):
            yield current
            continue
        if depth >= max_depth:
            continue
        try:
            children = sorted(p for p in current.iterdir() if p.is_dir())
        except OSError:
            continue
        for child in reversed(children):
            stack.append((child, depth + 1))


def iter_candidate_files(project_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(project_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        rel_dir = Path(dirpath).relative_to(project_dir)
        if len(rel_dir.parts) > 3:
            dirnames[:] = []
            continue
        for filename in filenames:
            path = Path(dirpath) / filename
            rel = path.relative_to(project_dir)
            if is_requirement_source(rel):
                candidates.append(path)
    return sorted(candidates, key=lambda p: (source_rank(p.name), str(p)))


def find_canonical_requirements_pdf(project_dir: Path) -> Path | None:
    candidates = [
        path
        for path in iter_candidate_files(project_dir)
        if path.suffix.lower() == ".pdf" and "requirement" in path.name.lower()
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda p: (
            len(p.relative_to(project_dir).parts),
            source_rank(p.name),
            str(p.relative_to(project_dir)).lower(),
        ),
    )[0]


def source_rank(name: str) -> int:
    lower = name.lower()
    if "requirement" in lower or "prd" in lower or "spec" in lower:
        return 0
    if "task" in lower or "plan" in lower or "presearch" in lower:
        return 1
    if "readme" in lower:
        return 2
    return 3


def clean_line(line: str) -> str:
    line = re.sub(r"\s+", " ", line.strip())
    line = re.sub(r"^#{1,6}\s*", "", line)
    return line[:600]


def extract_requirements(text: str, source: str, max_lines: int) -> tuple[list[Requirement], list[str], str]:
    requirements: list[Requirement] = []
    evidence: list[str] = []
    checked = 0
    unchecked = 0
    complete_hits = 0
    active_hits = 0
    in_code_block = False

    for line_no, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if raw.lstrip().startswith("#"):
            continue
        if in_code_block or looks_like_code(raw):
            continue
        line = clean_line(raw)
        if not line or len(line) < 4:
            continue
        if "[x]" in line.lower():
            checked += 1
        if "[ ]" in line.lower():
            unchecked += 1
        if COMPLETE_RE.search(line):
            complete_hits += 1
        if ACTIVE_RE.search(line):
            active_hits += 1
        if is_pdf_source(source) and len(requirements) < max_lines and is_meaningful_pdf_line(line):
            requirements.append(Requirement(line, source, line_no))
        elif REQUIREMENT_RE.search(line) and len(requirements) < max_lines:
            requirements.append(Requirement(line, source, line_no))

    if checked or unchecked:
        evidence.append(f"task list: {checked} checked, {unchecked} unchecked")
    if complete_hits:
        evidence.append(f"completion language hits: {complete_hits}")
    if active_hits:
        evidence.append(f"active/blocker language hits: {active_hits}")

    status = "unknown"
    if checked and checked >= max(1, unchecked * 2):
        status = "completed"
    elif unchecked > checked or active_hits > complete_hits:
        status = "active"
    elif complete_hits > active_hits and complete_hits > 0:
        status = "completed"
    return requirements, evidence, status


def is_pdf_source(source: str) -> bool:
    return source.lower().endswith(".pdf")


def is_meaningful_pdf_line(line: str) -> bool:
    if len(line) < 4:
        return False
    if set(line) <= {"_", "-", " ", "\t"}:
        return False
    return True


def looks_like_code(raw: str) -> bool:
    line = raw.strip()
    if not line:
        return False
    if re.match(r"^(const|let|var|import|export|from|def|class)\b", line):
        return True
    if re.match(r"^[A-Za-z_][\w.]*\s*=\s*require\(", line):
        return True
    if line.endswith(";") and ("(" in line or "=" in line):
        return True
    return False


def read_text(path: Path, max_bytes: int = 160_000) -> str:
    if path.suffix.lower() == ".pdf":
        return read_pdf_text(path)
    try:
        data = path.read_bytes()[:max_bytes]
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")


def read_pdf_text(path: Path) -> str:
    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout
    except (OSError, subprocess.CalledProcessError):
        return ""


def scan_local_project(path: Path, max_lines_per_file: int) -> Project:
    project = Project(name=path.name, source=str(path), kind="local")
    files = iter_candidate_files(path)
    canonical_pdf = find_canonical_requirements_pdf(path)
    if canonical_pdf:
        project.canonical_requirements_pdf = str(canonical_pdf)
    if not files:
        project.gaps.append("No requirement-like source files found.")
    for file_path in files[:16]:
        rel = str(file_path.relative_to(path))
        text = read_text(file_path)
        source_limit = max(max_lines_per_file, 260) if file_path.suffix.lower() == ".pdf" else max_lines_per_file
        reqs, evidence, status = extract_requirements(text, rel, source_limit)
        if reqs:
            project.requirement_sources.append(rel)
            project.requirements.extend(reqs)
        project.evidence.extend(f"{rel}: {item}" for item in evidence)
        project.status = merge_status(project.status, status)
    if not project.requirements:
        project.gaps.append("No requirement lines extracted.")
    if project.status == "unknown":
        project.gaps.append("No completion evidence found.")
    return project


def merge_status(current: str, incoming: str) -> str:
    order = {"completed": 3, "active": 2, "blocked": 2, "unknown": 1}
    if order.get(incoming, 0) > order.get(current, 0):
        return incoming
    return current


def gh_owner() -> str | None:
    data = run_json(["gh", "api", "user"])
    if isinstance(data, dict):
        login = data.get("login")
        if isinstance(login, str):
            return login
    return None


def gh_read_file(repo: str, path: str) -> str:
    data = run_json(["gh", "api", f"repos/{repo}/contents/{path}"])
    if not isinstance(data, dict) or data.get("encoding") != "base64":
        return ""
    content = data.get("content")
    if not isinstance(content, str):
        return ""
    try:
        data = base64.b64decode(content)
        if path.lower().endswith(".pdf"):
            with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
                tmp.write(data)
                tmp.flush()
                return read_pdf_text(Path(tmp.name))
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def gh_candidate_paths(repo: str, branch: str, limit: int = 8) -> list[str]:
    tree = run_json(["gh", "api", f"repos/{repo}/git/trees/{branch}?recursive=1"])
    if not isinstance(tree, dict):
        return []
    entries = tree.get("tree")
    if not isinstance(entries, list):
        return []
    paths: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("type") != "blob":
            continue
        path = entry.get("path")
        size = entry.get("size")
        if not isinstance(path, str):
            continue
        if any(part in SKIP_DIRS for part in Path(path).parts):
            continue
        if isinstance(size, int) and size > 180_000:
            continue
        if len(Path(path).parts) > 4:
            continue
        if is_requirement_source(path):
            paths.append(path)
    return sorted(paths, key=lambda p: (source_rank(Path(p).name), p))[:limit]


def scan_github(owner: str, limit: int, max_lines_per_file: int) -> list[Project]:
    fields = "nameWithOwner,description,url,isArchived,isPrivate,updatedAt,pushedAt,defaultBranchRef"
    data = run_json(["gh", "repo", "list", owner, "--limit", str(limit), "--json", fields])
    if not isinstance(data, list):
        return []
    projects: list[Project] = []
    for repo in data:
        if not isinstance(repo, dict):
            continue
        name = str(repo.get("nameWithOwner") or "")
        if not name:
            continue
        project = Project(
            name=name,
            source=str(repo.get("url") or name),
            kind="github",
            updated_at=str(repo.get("updatedAt") or repo.get("pushedAt") or ""),
            description=str(repo.get("description") or ""),
        )
        if repo.get("isArchived"):
            project.status = "completed"
            project.evidence.append("GitHub repo is archived.")
        default_branch = "HEAD"
        default_ref = repo.get("defaultBranchRef")
        if isinstance(default_ref, dict) and isinstance(default_ref.get("name"), str):
            default_branch = default_ref["name"]
        candidate_paths = gh_candidate_paths(name, default_branch)
        for candidate in candidate_paths:
            text = gh_read_file(name, candidate)
            if not text:
                continue
            reqs, evidence, status = extract_requirements(text, candidate, max_lines_per_file)
            if reqs:
                project.requirement_sources.append(candidate)
                project.requirements.extend(reqs)
            project.evidence.extend(f"{candidate}: {item}" for item in evidence)
            project.status = merge_status(project.status, status)
            if len(project.requirement_sources) >= 6:
                break
        if not project.requirements:
            project.gaps.append("No readable GitHub requirement docs found.")
        if project.status == "unknown":
            project.gaps.append("No GitHub completion evidence found.")
        projects.append(project)
    return projects


def dedupe_projects(projects: list[Project]) -> list[Project]:
    seen: set[str] = set()
    output: list[Project] = []
    for project in projects:
        key = project.name.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(project)
    return output


def render_markdown(projects: list[Project], args: argparse.Namespace) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    completed = sum(1 for p in projects if p.status == "completed")
    with_reqs = sum(1 for p in projects if p.requirements)
    lines = [
        "# Requirements Audit",
        "",
        f"Generated: {now}",
        f"Projects scanned: {len(projects)}",
        f"Projects with requirements: {with_reqs}",
        f"Projects with completed evidence: {completed}",
        f"Local root: {args.projects_root}",
        f"GitHub included: {'yes' if args.github else 'no'}",
        "",
        "## Summary",
        "",
        "| Project | Kind | Status | Requirements | Sources |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for project in projects:
        lines.append(
            f"| {escape_md(project.name)} | {project.kind} | {project.status} | "
            f"{len(project.requirements)} | {len(project.requirement_sources)} |"
        )

    for project in projects:
        lines.extend(["", f"## {project.name}", ""])
        lines.append(f"- Source: `{project.source}`")
        lines.append(f"- Kind: {project.kind}")
        lines.append(f"- Status: {project.status}")
        if project.updated_at:
            lines.append(f"- Updated: {project.updated_at}")
        if project.description:
            lines.append(f"- Description: {project.description}")
        if project.requirement_sources:
            lines.append(f"- Requirement sources: {', '.join(project.requirement_sources)}")
        if project.evidence:
            lines.append("- Evidence:")
            for item in project.evidence[:8]:
                lines.append(f"  - {item}")
        if project.gaps:
            lines.append("- Gaps:")
            for item in project.gaps[:8]:
                lines.append(f"  - {item}")
        lines.append("")
        lines.append("### Requirements")
        if not project.requirements:
            lines.append("")
            lines.append("No requirement lines extracted.")
        else:
            for req in project.requirements[: args.max_requirements_per_project]:
                src = req.source if req.line is None else f"{req.source}:{req.line}"
                lines.append(f"- {normalize_requirement_text(req.text)} [{src}]")
    lines.append("")
    return "\n".join(lines)


def escape_md(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def write_minimal_pdf(text: str, output: Path) -> None:
    pages = paginate(text)
    objects: list[str] = []
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    page_refs = " ".join(f"{3 + i * 2} 0 R" for i in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{page_refs}] /Count {len(pages)} >>")
    for index, page in enumerate(pages):
        page_obj = 3 + index * 2
        content_obj = page_obj + 1
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            f"/Contents {content_obj} 0 R >>"
        )
        stream = pdf_text_stream(page)
        objects.append(f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}\nendstream")

    parts = ["%PDF-1.4\n"]
    offsets = [0]
    for idx, obj in enumerate(objects, 1):
        offsets.append(sum(len(part.encode("latin-1")) for part in parts))
        parts.append(f"{idx} 0 obj\n{obj}\nendobj\n")
    xref_offset = sum(len(part.encode("latin-1")) for part in parts)
    parts.append(f"xref\n0 {len(objects) + 1}\n")
    parts.append("0000000000 65535 f \n")
    for offset in offsets[1:]:
        parts.append(f"{offset:010d} 00000 n \n")
    parts.append(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )
    output.write_bytes("".join(parts).encode("latin-1", errors="replace"))


def paginate(text: str) -> list[list[str]]:
    wrapped: list[str] = []
    for raw in text.splitlines():
        clean = raw.encode("latin-1", errors="replace").decode("latin-1")
        if not clean:
            wrapped.append("")
            continue
        width = 86 if not clean.startswith("#") else 72
        wrapped.extend(textwrap.wrap(clean, width=width, replace_whitespace=False) or [""])
    pages: list[list[str]] = []
    page_size = 54
    for i in range(0, len(wrapped), page_size):
        pages.append(wrapped[i : i + page_size])
    return pages or [["Requirements Audit"]]


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf_text_stream(lines: list[str]) -> str:
    stream = ["BT", "/F1 10 Tf", "14 TL", "50 750 Td"]
    first = True
    for line in lines:
        if first:
            first = False
        else:
            stream.append("T*")
        stream.append(f"({pdf_escape(line)}) Tj")
    stream.append("ET")
    return "\n".join(stream)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects-root", default=".")
    parser.add_argument("--output", default="requirements-audit.pdf")
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--max-projects", type=int, default=120)
    parser.add_argument("--max-lines-per-file", type=int, default=80)
    parser.add_argument("--max-requirements-per-project", type=int, default=60)
    parser.add_argument("--github-owner", default="")
    parser.add_argument("--github-limit", type=int, default=120)
    parser.add_argument("--completed-only", action="store_true")
    parser.add_argument(
        "--output-mode",
        choices=("audit",),
        default="audit",
        help="Only audit mode is supported. Final requirements.md/pdf must be authored by the agent workflow.",
    )
    parser.add_argument("--github", dest="github", action="store_true", default=False)
    parser.add_argument("--no-github", dest="github", action="store_false")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    output = Path(args.output).expanduser().resolve()
    final_names = {"requirements.pdf", "requirements.md", "requirements.json"}
    derived_names = {output.name.casefold(), output.with_suffix(".md").name.casefold(), output.with_suffix(".json").name.casefold()}
    if derived_names & final_names:
        sys.stderr.write(
            "Refusing to write final requirements artifact names from the audit collector. "
            "Use requirements-audit.pdf or another *-audit.* name.\n"
        )
        return 2
    output.parent.mkdir(parents=True, exist_ok=True)

    root = Path(args.projects_root)
    local_projects = [
        scan_local_project(path, args.max_lines_per_file)
        for path in list(iter_project_dirs(root, args.max_depth))[: args.max_projects]
    ]

    github_projects: list[Project] = []
    if args.github:
        owner = args.github_owner or gh_owner()
        if owner:
            github_projects = scan_github(owner, args.github_limit, args.max_lines_per_file)
        else:
            sys.stderr.write("GitHub skipped: gh is unavailable or unauthenticated.\n")

    projects = dedupe_projects(local_projects + github_projects)
    if args.completed_only:
        projects = [project for project in projects if project.status == "completed"]
    projects.sort(key=lambda p: (p.status != "completed", p.kind, p.name.lower()))

    markdown = render_markdown(projects, args)
    json_output = output.with_suffix(".json")
    md_output = output.with_suffix(".md")
    md_output.write_text(markdown, encoding="utf-8")
    json_output.write_text(
        json.dumps([project_to_dict(p) for p in projects], indent=2),
        encoding="utf-8",
    )
    write_pdf(markdown, output)
    print(f"Wrote audit {output}")
    print(f"Wrote {md_output}")
    print(f"Wrote {json_output}")
    print(f"Projects: {len(projects)}")
    return 0


def project_to_dict(project: Project) -> dict[str, object]:
    data = asdict(project)
    data["requirements"] = [
        {"text": normalize_requirement_text(req.text), "source": req.source, "line": req.line}
        for req in project.requirements
    ]
    return data


def normalize_requirement_text(text: str) -> str:
    text = re.sub(r"^\s*[-*]\s*", "", text.strip())
    text = re.sub(r"^\s*\[[ xX]\]\s*", "", text)
    return text


def write_pdf(text: str, output: Path) -> None:
    try:
        write_reportlab_pdf(text, output)
    except Exception as exc:
        sys.stderr.write(f"ReportLab PDF renderer failed, using minimal fallback: {exc}\n")
        write_minimal_pdf(text, output)


def write_reportlab_pdf(text: str, output: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReqTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReqHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0F766E"),
            spaceBefore=12,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReqBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#111827"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReqSmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#4B5563"),
        )
    )

    doc = SimpleDocTemplate(
        str(output),
        pagesize=LETTER,
        leftMargin=0.62 * inch,
        rightMargin=0.62 * inch,
        topMargin=0.58 * inch,
        bottomMargin=0.58 * inch,
        title="Requirements Audit",
        author="create-requirements",
    )
    story = []
    table_rows: list[list[str]] = []
    in_table = False

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if table_rows:
                story.append(make_table(table_rows, styles, Paragraph, Table, TableStyle, colors))
                table_rows = []
                in_table = False
            story.append(Spacer(1, 4))
            continue
        if line.startswith("|"):
            parts = [cell.strip() for cell in line.strip("|").split("|")]
            if parts and not all(set(cell) <= {"-", ":", " "} for cell in parts):
                table_rows.append(parts)
                in_table = True
            continue
        if in_table and table_rows:
            story.append(make_table(table_rows, styles, Paragraph, Table, TableStyle, colors))
            table_rows = []
            in_table = False

        if line.startswith("# "):
            story.append(Paragraph(html_escape(line[2:]), styles["ReqTitle"]))
        elif line.startswith("## "):
            story.append(Paragraph(html_escape(line[3:]), styles["ReqHeading"]))
        elif line.startswith("### "):
            story.append(Paragraph(f"<b>{html_escape(line[4:])}</b>", styles["ReqBody"]))
        elif line.startswith("- "):
            story.append(Paragraph(f"&bull; {html_escape(line[2:])}", styles["ReqBody"]))
        else:
            story.append(Paragraph(html_escape(line), styles["ReqBody"]))

    if table_rows:
        story.append(make_table(table_rows, styles, Paragraph, Table, TableStyle, colors))
    doc.build(story)


def make_table(rows, styles, paragraph_cls, table_cls, table_style_cls, colors_mod):
    formatted = [[paragraph_cls(html_escape(cell), styles["ReqSmall"]) for cell in row] for row in rows]
    table = table_cls(formatted, repeatRows=1)
    table.setStyle(
        table_style_cls(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors_mod.HexColor("#E0F2F1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors_mod.HexColor("#0F172A")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors_mod.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("`", "")
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
