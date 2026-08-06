#!/usr/bin/env python3
"""Validate Cursor Agent SKILL.md files in this repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / ".cursor" / "skills"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
DESC_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("missing YAML frontmatter (--- ... ---)")
    block = match.group(1)
    name_match = NAME_RE.search(block)
    desc_match = DESC_RE.search(block)
    if not name_match:
        raise ValueError("frontmatter missing name")
    if not desc_match:
        raise ValueError("frontmatter missing description")
    return {
        "name": name_match.group(1).strip().strip("\"'"),
        "description": desc_match.group(1).strip().strip("\"'"),
    }


def main() -> int:
    if not SKILLS_ROOT.is_dir():
        print(f"ERROR: skills root not found: {SKILLS_ROOT}", file=sys.stderr)
        return 1

    skill_files = sorted(SKILLS_ROOT.rglob("SKILL.md"))
    if not skill_files:
        print(f"ERROR: no SKILL.md files under {SKILLS_ROOT}", file=sys.stderr)
        return 1

    errors: list[str] = []
    skills: list[tuple[str, str, Path]] = []

    for path in skill_files:
        rel = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
            meta = parse_frontmatter(text)
            if len(text.strip()) < 80:
                raise ValueError("skill body too short")
            skills.append((meta["name"], meta["description"], rel))
        except Exception as exc:  # noqa: BLE001 - collect all validation errors
            errors.append(f"{rel}: {exc}")

    print(f"Skills root: {SKILLS_ROOT}")
    print(f"Found SKILL.md files: {len(skill_files)}")
    print()
    for name, description, rel in skills:
        print(f"OK  {name}")
        print(f"    path: {rel}")
        print(f"    desc: {description[:120]}{'…' if len(description) > 120 else ''}")
        print()

    # Smoke-check optional patent tooling dependency.
    try:
        import docx  # type: ignore

        print(f"python-docx: OK (version {getattr(docx, '__version__', 'unknown')})")
    except ImportError:
        print("python-docx: not installed (optional for .docx交底书 handling)")

    if errors:
        print("\nVALIDATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"\nVALIDATION PASSED: {len(skills)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
