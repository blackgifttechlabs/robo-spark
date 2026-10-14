#!/usr/bin/env python3
"""Generate clean-URL topic pages: /topic/<id>/ from pages/topic/template.html and pages/home/projects.js."""
import json, re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
template = (root / 'pages/topic/template.html').read_text()
src = (root / 'pages/home/projects.js').read_text()
projects = json.loads(src[src.index('['):src.rindex(']') + 1])
for p in projects:
    out = root / 'topic' / p['id']
    out.mkdir(parents=True, exist_ok=True)
    page = template.replace('<title>Build a project — Robo Sparks</title>', f"<title>{p['title']} — Robo Sparks</title>")
    (out / 'index.html').write_text(page)
print(f'wrote {len(projects)} topic pages')
