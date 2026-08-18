#!/usr/bin/env python3
"""assemble.py <src-file> <out-name>
Replaces /*FONT:Family Name*/ tokens with cached fontlib CSS and {{RESUME_HREF}}
with the resume data URI, validates, writes ~/anhad-site/<out-name>.html"""
import base64, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent.parent
RESUME = pathlib.Path("/Users/apple/Anhad-Resume/Anhad-Singh-Resume.pdf")

src = pathlib.Path(sys.argv[1]).read_text()
out = ROOT / (sys.argv[2] + ".html")

for tok in set(re.findall(r"/\*ASSET:([^*]+)\*/", src)):
    f = ROOT / "assets" / tok.strip()
    if not f.exists():
        sys.exit(f"unknown asset: {tok!r} — available: "
                 + ", ".join(sorted(x.name for x in (ROOT/'assets').glob('*.jpg'))))
    src = src.replace(f"/*ASSET:{tok}*/",
                      "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode())

for tok in set(re.findall(r"/\*FONT:([^*]+)\*/", src)):
    lib = ROOT / "fontlib" / (tok.strip().replace(" ", "-") + ".css")
    if not lib.exists():
        sys.exit(f"unknown font token: {tok!r} — available: "
                 + ", ".join(sorted(p.stem for p in (ROOT/'fontlib').glob('*.css'))))
    src = src.replace(f"/*FONT:{tok}*/", lib.read_text())

if "{{RESUME_HREF}}" in src:
    src = src.replace("{{RESUME_HREF}}",
        "data:application/pdf;base64," + base64.b64encode(RESUME.read_bytes()).decode())

errs = []
if not src.lstrip().startswith('<meta charset="utf-8">'):
    errs.append('file must START with <meta charset="utf-8">')
if src.count("<h1") != 1: errs.append(f"h1 count = {src.count('<h1')}, need exactly 1")
if 'name="viewport"' not in src: errs.append("missing viewport meta")
if "{{" in src: errs.append("unresolved {{placeholder}}")
if re.search(r"/\*FONT:|/\*ASSET:", src): errs.append("unresolved font/asset token")
if "http://" in src.replace("http://www.w3.org", "") or "https://cdn" in src or "fonts.googleapis" in src:
    pass  # external <a href> links are fine; assets must not be — spot-check below
for bad in ["<img src=\"http", "url(http", "<script src=", "<link rel=\"stylesheet\""]:
    if bad in src: errs.append(f"external asset reference: {bad}")
if errs: sys.exit("ASSEMBLE FAILED:\n  - " + "\n  - ".join(errs))

out.write_text(src)
print(f"built {out} ({len(src)/1024:.0f} KB)")
