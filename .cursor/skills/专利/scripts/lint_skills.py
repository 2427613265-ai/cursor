#!/usr/bin/env python3
"""Lint patent skills: description length, optional body line soft limits."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # .cursor/skills/专利
DESC_LIMIT = 150
# Soft limits (warn): 规范 180, 总控/策略 250 — post-optimization targets; not all migrated
BODY_WARN_NORM = 180
BODY_WARN_CTRL = 250
CTRL_HINTS = ("总控", "撰写", "理解", "评估与独权补强", "答复")


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = text[3:end]
    data = {}
    m = re.search(r"^name:\s*(.+)$", fm, re.M)
    if m:
        data["name"] = m.group(1).strip()
    m = re.search(r"^description:\s*(.+?)(?=\n(?:[a-zA-Z_]|---)|\Z)", fm, re.S | re.M)
    if m:
        data["description"] = " ".join(m.group(1).split())
    # optional metadata.中文名称 (warn if missing on non-jump skills)
    if re.search(r"^\s*中文名称:\s*\S", fm, re.M):
        data["has_cn_name"] = True
    return data


def is_controller(name: str, rel: str) -> bool:
    if any(h in name for h in ("总控",)):
        return True
    if "撰写策略" in rel:
        return True
    if name.endswith("撰写") and "规范" not in name:
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict-body", action="store_true", help="treat body soft limits as errors")
    args = ap.parse_args()

    errors = []
    warns = []
    skills = sorted(ROOT.rglob("SKILL.md"))
    # skip nothing under 专利
    for path in skills:
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        fm = parse_frontmatter(text)
        name = fm.get("name") or path.parent.name
        desc = fm.get("description") or ""
        if not desc:
            errors.append(f"{rel}: missing description")
            continue
        if len(desc) > DESC_LIMIT:
            errors.append(f"{rel}: description {len(desc)} > {DESC_LIMIT} ({name})")
        # jump stubs are short — ok
        is_jump = "已收束" in desc or "跳转" in name or "跳转" in desc[:20]
        if not is_jump and not fm.get("has_cn_name"):
            warns.append(f"{rel}: missing metadata.中文名称 ({name})")
        if is_jump:
            continue
        limit = BODY_WARN_CTRL if is_controller(name, rel) else BODY_WARN_NORM
        if lines > limit:
            msg = f"{rel}: body {lines} lines > soft {limit} ({name})"
            (errors if args.strict_body else warns).append(msg)

    for w in warns:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"Checked {len(skills)} SKILL.md; errors={len(errors)} warns={len(warns)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
