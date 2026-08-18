#!/usr/bin/env python3
"""Cache distinctive families as self-contained @font-face CSS in fontlib/.
Fontshare bundles sibling families under one slug, so every block is filtered
by exact family name. Guards: normal style only unless (fam, 'italic') listed."""
import base64, pathlib, re, urllib.request, sys

LIB = pathlib.Path(__file__).parent.parent / "fontlib"
LIB.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

def get(u, b=False):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
        return r.read() if b else r.read().decode()

# slug -> (family, weights, want_italic)
FONTSHARE = {
    "zodiak":          ("Zodiak",          [400, 700], True),
    "cabinet-grotesk": ("Cabinet Grotesk", [400, 700, 800], False),
    "bespoke-stencil": ("Bespoke Stencil", [400, 700], False),
    "melodrama":       ("Melodrama",       [500, 700], False),
    "panchang":        ("Panchang",        [400, 600, 700], False),
    "gambarino":       ("Gambarino",       [400], False),
    "ranade":          ("Ranade",          [400, 500, 700], True),
    "general-sans":    ("General Sans",    [400, 500, 600], True),
    "erode":           ("Erode",           [400, 500, 700], True),
    "boska":           ("Boska",           [400, 700, 900], True),
    "sentient":        ("Sentient",        [400, 700], True),
    "tanker":          ("Tanker",          [400], False),
    "khand":           ("Khand",           [400, 600, 700], False),
    "amulya":          ("Amulya",          [400, 700], False),
    "pramukh-rounded": ("Pramukh Rounded", [400, 700], False),
}
GOOGLE = {
    "Courier Prime": "family=Courier+Prime:ital,wght@0,400;0,700;1,400",
    "Fragment Mono": "family=Fragment+Mono",
    "Martian Mono":  "family=Martian+Mono:wght@400;700",
    "Caveat":        "family=Caveat:wght@400;600;700",
    "Special Elite": "family=Special+Elite",
}

def face(fam, style, weight, data):
    return (f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
            f"font-display:swap;src:url(data:font/woff2;base64,"
            f"{base64.b64encode(data).decode()}) format('woff2');}}")

for slug, (fam, weights, ital) in FONTSHARE.items():
    out = LIB / (fam.replace(" ", "-") + ".css")
    if out.exists(): print(f"cached  {fam}"); continue
    try:
        css = get(f"https://api.fontshare.com/v2/css?f%5B%5D={slug}&display=swap")
    except Exception as e:
        print(f"SKIP    {fam}: {e}"); continue
    got, faces = {}, []
    for blk in re.findall(r"@font-face\s*\{.*?\}", css, re.S):
        m = re.search(r"font-family:\s*'([^']+)'", blk)
        if not m or m.group(1) != fam: continue
        st = "italic" if "italic" in blk.lower() else "normal"
        if st == "italic" and not ital: continue
        wt = re.search(r"font-weight:\s*(\d+)", blk)
        url = re.search(r"url\('(//cdn\.fontshare\.com/[^']+\.woff2)'\)", blk)
        if wt and url: got[(st, int(wt.group(1)))] = url.group(1)
    if not got: print(f"MISS    {fam}"); continue
    for w in weights:
        for st in (["normal", "italic"] if ital else ["normal"]):
            avail = [k[1] for k in got if k[0] == st]
            if not avail: continue
            pick = min(avail, key=lambda a: abs(a - w))
            faces.append(face(fam, st, w, get("https:" + got[(st, pick)], True)))
    out.write_text("\n".join(faces))
    print(f"fetched {fam}: {len(faces)} faces, {out.stat().st_size//1024} KB")

for fam, q in GOOGLE.items():
    out = LIB / (fam.replace(" ", "-") + ".css")
    if out.exists(): print(f"cached  {fam}"); continue
    css = get(f"https://fonts.googleapis.com/css2?{q}&display=swap")
    faces = []
    for label, body in zip(re.findall(r"/\*\s*([a-z\-]+)\s*\*/", css),
                           re.split(r"/\*\s*[a-z\-]+\s*\*/", css)[1:]):
        if label != "latin": continue
        for blk in re.findall(r"@font-face\s*\{.*?\}", body, re.S):
            st = "italic" if "font-style: italic" in blk else "normal"
            wt = re.search(r"font-weight:\s*(\d+)", blk)
            url = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", blk)
            if url: faces.append(face(fam, st, int(wt.group(1)) if wt else 400,
                                      get(url.group(1), True)))
    out.write_text("\n".join(faces))
    print(f"fetched {fam}: {len(faces)} faces, {out.stat().st_size//1024} KB")

print("\nfontlib:", sorted(p.stem for p in LIB.glob("*.css")))
