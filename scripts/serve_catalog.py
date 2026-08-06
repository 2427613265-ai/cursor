#!/usr/bin/env python3
"""Generate and serve a simple HTML catalog of patent skills."""

from __future__ import annotations

import argparse
import html
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / ".cursor" / "skills"
OUT_DIR = ROOT / ".local" / "catalog"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
DESC_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)


def parse_skill(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path}: missing frontmatter")
    block = match.group(1)
    name = NAME_RE.search(block)
    desc = DESC_RE.search(block)
    if not name or not desc:
        raise ValueError(f"{path}: incomplete frontmatter")
    rel = path.relative_to(SKILLS_ROOT).as_posix()
    branch = str(path.relative_to(SKILLS_ROOT).parent)
    return {
        "name": name.group(1).strip().strip("\"'"),
        "description": desc.group(1).strip().strip("\"'"),
        "path": rel,
        "branch": branch,
    }


def build_catalog() -> Path:
    skills = [parse_skill(p) for p in sorted(SKILLS_ROOT.rglob("SKILL.md"))]
    skills.sort(key=lambda s: (s["branch"], s["name"]))

    cards = []
    for skill in skills:
        cards.append(
            f"""
            <article class="card">
              <h2>{html.escape(skill["name"])}</h2>
              <p class="branch">{html.escape(skill["branch"])}</p>
              <p class="desc">{html.escape(skill["description"])}</p>
              <code>{html.escape(skill["path"])}</code>
            </article>
            """
        )

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Patent Skills Catalog</title>
  <style>
    :root {{
      --ink: #1c2430;
      --muted: #5b6775;
      --paper: #f7f3ea;
      --panel: #fffdf8;
      --line: #d9d0bf;
      --accent: #0f6a5a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(15, 106, 90, 0.12), transparent 40%),
        linear-gradient(180deg, #efe7d8 0%, var(--paper) 45%, #f4efe4 100%);
      min-height: 100vh;
    }}
    header {{
      padding: 48px 24px 24px;
      max-width: 1100px;
      margin: 0 auto;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(2rem, 4vw, 3rem);
      letter-spacing: 0.02em;
    }}
    .lede {{
      margin: 0;
      color: var(--muted);
      max-width: 60ch;
      line-height: 1.5;
    }}
    .meta {{
      margin-top: 16px;
      color: var(--accent);
      font-weight: 600;
    }}
    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 8px 24px 64px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 18px 18px 16px;
      box-shadow: 0 10px 30px rgba(28, 36, 48, 0.05);
    }}
    .card h2 {{
      margin: 0 0 8px;
      font-size: 1.15rem;
      line-height: 1.3;
    }}
    .branch {{
      margin: 0 0 10px;
      color: var(--accent);
      font-size: 0.85rem;
    }}
    .desc {{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 0.95rem;
      line-height: 1.45;
    }}
    code {{
      display: block;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.75rem;
      color: #334155;
      word-break: break-all;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Patent Skills Catalog</h1>
    <p class="lede">本仓库中文专利撰写与质检 Cursor Agent Skills 的本地开发目录。环境安装完成后可在此确认 skill 已就绪。</p>
    <p class="meta">{len(skills)} skills loaded · development environment OK</p>
  </header>
  <main>
    {"".join(cards)}
  </main>
</body>
</html>
"""

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index = OUT_DIR / "index.html"
    index.write_text(page, encoding="utf-8")
    return index


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OUT_DIR), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))
        sys.stdout.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--once", action="store_true", help="only build HTML, do not serve")
    args = parser.parse_args()

    index = build_catalog()
    print(f"Catalog written to {index}")
    if args.once:
        return 0

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Serving patent skills catalog at http://{args.host}:{args.port}/")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
