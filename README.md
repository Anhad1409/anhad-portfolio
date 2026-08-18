# wait, why? — Anhad's portfolio

Personal portfolio of **Anhad** — product manager who designs the interfaces he specs.
Live concept: **v1 "wait, why?"** — a particle field that organizes into clarity as you
scroll; the journey told as film storyboards.

## Structure

| Path | What |
|---|---|
| `index.html` | The site (= `v1.html`). Fully self-contained: fonts, images, résumé PDF all inlined. Zero external requests. |
| `v2–v5.html` | Alternate concepts (Dossier · Signal Room · The Knowing · Field Notes), kept for reference. `versions.html` = gallery. |
| `srcs/` | Editable sources with `/*FONT:…*/`, `/*ASSET:…*/`, `{{RESUME_HREF}}` tokens |
| `tools/assemble.py` | `python3 tools/assemble.py srcs/<x>.src.html <name>` → builds `<name>.html`, validates (charset-first, single h1, no external assets) |
| `tools/shot.sh` | `bash tools/shot.sh <url> <ABSOLUTE outdir>` → desktop+mobile scrolled screenshots + JS-error/overflow report |
| `fontlib/` | 20 cached families (Fontshare/ITF + Google) as base64 css |
| `assets/` | Design-shelf imagery (currently unused in v1) |
| `BRIEF.md` / `CONSTRAINTS.md` | Content contract + hard-won build pitfalls |

## Run locally

```bash
python3 -m http.server 4141   # from repo root → http://localhost:4141/
```

## Before public deploy
OG/social meta tags · analytics · custom domain · update résumé's portfolio URL.
