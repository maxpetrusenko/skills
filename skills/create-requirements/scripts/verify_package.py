#!/usr/bin/env python3
"""Verify a research-led requirements package is complete enough to review."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_FILES = [
    "brainlift.md",
    "requirements-research.md",
    "requirements-prd.md",
    "requirements-presearch.md",
    "requirements-spec.md",
    "requirements-ui-flows.md",
    "requirements-traceability.json",
    "requirements.md",
    "requirements.pdf",
    "requirements-review.md",
]

BANNED_TEXT = [
    "{{",
    "}}",
    "Generated Product Requirements",
    "x-hiring-system",
    "SixSourceHardGate",
    "WarmPathGraph",
    "ApprovalConsumeOnce",
    "FundingLane in x-hiring-system-test-runner",
]

REQUIRED_REQUIREMENTS_SECTIONS = [
    "## Background",
    "## Brainlift Summary",
    "## Comparable-Product Research",
    "## Product Thesis",
    "## Presearch Decision Matrix",
    "## MVP Requirements",
    "## Core Product Requirements",
    "## UI Flows",
    "## Technical Architecture",
    "## Acceptance Test Plan",
    "## Traceability Appendix",
]

REQUIRED_REVIEW_FIELDS = [
    "Rating:",
    "Verdict:",
    "Independent reviewer:",
    "Reviewer context:",
    "Authoring context:",
    "Artifacts reviewed:",
    "Evidence read:",
    "Comparable sources:",
    "Hard caps checked:",
    "Verification commands:",
]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", help="Directory containing the generated requirements package.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    package_dir = Path(args.package_dir).expanduser().resolve()
    failures: list[str] = []

    if not package_dir.is_dir():
        sys.stderr.write(f"Package directory does not exist: {package_dir}\n")
        return 2

    for filename in REQUIRED_FILES:
        path = package_dir / filename
        if not path.is_file():
            failures.append(f"missing required artifact: {filename}")
        elif path.stat().st_size == 0:
            failures.append(f"empty required artifact: {filename}")

    for path in list(package_dir.glob("*.md")) + list(package_dir.glob("*.json")) + list(package_dir.glob("*.txt")):
        scan_text_file(path, failures)

    requirements_md = package_dir / "requirements.md"
    if requirements_md.is_file():
        validate_requirements_md(requirements_md, failures)

    traceability = package_dir / "requirements-traceability.json"
    traceability_ids: set[str] = set()
    if traceability.is_file():
        traceability_ids = validate_traceability(traceability, failures)
    if requirements_md.is_file() and traceability_ids:
        validate_traceability_ids_in_requirements(requirements_md, traceability_ids, failures)

    review = package_dir / "requirements-review.md"
    if review.is_file():
        validate_review(review, failures)

    pdf = package_dir / "requirements.pdf"
    if pdf.is_file() and pdf.stat().st_size < 10_000:
        failures.append("requirements.pdf is unexpectedly small")
    if pdf.is_file():
        scan_pdf_text(pdf, failures)

    if failures:
        sys.stderr.write("Requirements package verification failed:\n")
        for failure in failures:
            sys.stderr.write(f"- {failure}\n")
        return 1

    print(f"Requirements package verification passed: {package_dir}")
    return 0


def scan_text_file(path: Path, failures: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        failures.append(f"cannot read {path.name}: {exc}")
        return
    for token in BANNED_TEXT:
        if token in text:
            failures.append(f"{path.name} contains banned token: {token}")


def scan_pdf_text(path: Path, failures: list[str]) -> None:
    if shutil.which("pdftotext") is None:
        failures.append("pdftotext is unavailable; cannot verify requirements.pdf text")
        return
    try:
        proc = subprocess.run(
            ["pdftotext", str(path), "-"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        failures.append(f"cannot extract text from requirements.pdf: {exc}")
        return
    for token in BANNED_TEXT:
        if token in proc.stdout:
            failures.append(f"requirements.pdf contains banned token: {token}")


def validate_requirements_md(path: Path, failures: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        failures.append(f"cannot read requirements.md: {exc}")
        return
    for section in REQUIRED_REQUIREMENTS_SECTIONS:
        if section not in text:
            failures.append(f"requirements.md missing required section: {section}")


def validate_traceability(path: Path, failures: list[str]) -> set[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"requirements-traceability.json is invalid JSON: {exc}")
        return set()

    if not isinstance(data, list) or not data:
        failures.append("requirements-traceability.json must be a non-empty list")
        return set()

    required_keys = {
        "id",
        "requirement",
        "source_evidence",
        "research_influence",
        "acceptance_tests",
        "gaps_or_risks",
    }
    ids: set[str] = set()
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            failures.append(f"traceability item {index} must be an object")
            continue
        missing = sorted(required_keys - item.keys())
        if missing:
            failures.append(f"traceability item {index} missing keys: {', '.join(missing)}")
        req_id = item.get("id")
        if not isinstance(req_id, str) or not re.match(r"^[A-Z]+-[0-9]{3}$", req_id):
            failures.append(f"traceability item {index} has invalid id: {req_id!r}")
        elif req_id in ids:
            failures.append(f"duplicate requirement id: {req_id}")
        else:
            ids.add(req_id)
        for key in ("source_evidence", "research_influence", "acceptance_tests"):
            value = item.get(key)
            if not isinstance(value, list) or not value:
                failures.append(f"traceability item {req_id or index} requires non-empty {key}")
    return ids


def validate_traceability_ids_in_requirements(path: Path, traceability_ids: set[str], failures: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        failures.append(f"cannot read requirements.md: {exc}")
        return
    missing = sorted(req_id for req_id in traceability_ids if req_id not in text)
    if missing:
        failures.append(f"requirements.md missing traceability ids: {', '.join(missing)}")


def validate_review(path: Path, failures: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        failures.append(f"cannot read requirements-review.md: {exc}")
        return
    if not re.search(r"\bindependent\b", text, re.I):
        failures.append("requirements-review.md must document independent review")
    for field in REQUIRED_REVIEW_FIELDS:
        if field not in text:
            failures.append(f"requirements-review.md missing field: {field}")
    author_match = re.search(r"Authoring context:\s*(.+)", text, re.I)
    reviewer_match = re.search(r"Reviewer context:\s*(.+)", text, re.I)
    if author_match and reviewer_match and author_match.group(1).strip() == reviewer_match.group(1).strip():
        failures.append("requirements-review.md reviewer context must differ from authoring context")
    score_match = re.search(r"(?:rating|score)\s*[:=-]\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*10", text, re.I)
    if not score_match:
        failures.append("requirements-review.md must include Rating: N/10")
        return
    score = float(score_match.group(1))
    if score < 9.0:
        failures.append(f"requirements-review.md score is below 9.0: {score}/10")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
