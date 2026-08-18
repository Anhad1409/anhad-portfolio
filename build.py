#!/usr/bin/env python3
"""Assemble index.html: fetch + embed exact font families (guarding against
Fontshare bundling sibling families under one slug), embed the resume PDF."""
import base64, pathlib, re, sys, urllib.request

HERE = pathlib.Path(__file__).parent
SRC, OUT = HERE / "src.html", HERE / "index.html"
CACHE = HERE / "fonts.css"
RESUME = pathlib.Path("/Users/apple/Anhad-Resume/Anhad-Singh-Resume.pdf")

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
def get(u, b=False):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
        return r.read() if b else r.read().decode()

# slug -> (exact family name required, weights wanted)
WANT = {
    "cabinet-grotesk": ("Cabinet Grotesk", [700, 800]),
    "zodiak":          ("Zodiak",          [400, 700]),
}
GOOGLE = ("https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700"
          "&family=Fragment+Mono&display=swap")

def build_fonts():
    faces = []
    for slug, (fam_want, weights) in WANT.items():
        css = get(f"https://api.fontshare.com/v2/css?f%5B%5D={slug}&display=swap")
        byw = {}
        for blk in re.findall(r"@font-face\s*\{.*?\}", css, re.S):
            fam = re.search(r"font-family:\s*'([^']+)'", blk)
            if not fam or fam.group(1) != fam_want or "italic" in blk.lower():
                continue  # <- rejects Fontshare's bundled sibling families
            wt = re.search(r"font-weight:\s*(\d+)", blk)
            url = re.search(r"url\('(//cdn\.fontshare\.com/[^']+\.woff2)'\)", blk)
            if wt and url:
                byw[int(wt.group(1))] = url.group(1)
        if not byw:
            sys.exit(f"{slug}: family '{fam_want}' not found")
        for w in weights:
            pick = min(byw, key=lambda a: abs(a - w))
            data = get("https:" + byw[pick], True)
            faces.append((fam_want, w, data))
    css = get(GOOGLE)
    for label, body in zip(re.findall(r"/\*\s*([a-z\-]+)\s*\*/", css),
                           re.split(r"/\*\s*[a-z\-]+\s*\*/", css)[1:]):
        if label != "latin":
            continue
        for blk in re.findall(r"@font-face\s*\{.*?\}", blk_src := body, re.S):
            fam = re.search(r"font-family:\s*'([^']+)'", blk).group(1)
            wt = re.search(r"font-weight:\s*(\d+)", blk)
            url = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", blk)
            if url:
                faces.append((fam, int(wt.group(1)) if wt else 400, get(url.group(1), True)))
    out = []
    for fam, w, data in faces:
        out.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};"
                   f"font-display:swap;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(data).decode()}) format('woff2');}}")
        print(f"  {fam:ain18s}" if False else f"  {fam:18s} {w}  {len(data)/1024:6.1f} KB")
    return "\n".join(out)

if CACHE.exists() and "--refetch" not in sys.argv:
    fonts = CACHE.read_text()
    print("fonts: cached")
else:
    fonts = build_fonts()
    CACHE.write_text(fonts)

html = SRC.read_text()
assert "/*FONTS*/" in html and "{{RESUME_HREF}}" in html
html = html.replace("/*FONTS*/", fonts)
html = html.replace("{{RESUME_HREF}}",
                    "data:application/pdf;base64," + base64.b64encode(RESUME.read_bytes()).decode())
OUT.write_text(html)
assert "{{" not in html.replace("{{", "", 0) or "{{RESUME_HREF}}" not in html
print(f"built {OUT}  ({len(html)/1024:.0f} KB)")
