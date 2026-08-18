# BUILD CONSTRAINTS — every version (hard requirements + hard-won pitfalls)

## File contract
- Write source to `~/anhad-site/srcs/<vN-slug>.src.html`.
- FIRST line must be exactly `<meta charset="utf-8">`, then viewport meta, then <title>.
  (Served without charset headers; missing this mojibakes every quote — we hit it.)
- Fonts: NEVER fetch externally. Put `/*FONT:Family Name*/` tokens inside your <style>;
  the assembler inlines cached families. Available: Amulya, Bespoke Stencil, Boska,
  Cabinet Grotesk, Caveat, Courier Prime, Erode, Fragment Mono, Gambarino, General Sans,
  Khand, Martian Mono, Melodrama, Panchang, Pramukh Rounded, Ranade, Sentient,
  Special Elite, Tanker, Zodiak. (Italics exist for: Zodiak, Ranade, General Sans,
  Erode, Boska, Sentient, Courier Prime.)
- Résumé link: `href="{{RESUME_HREF}}" download="Anhad-Resume.pdf"`.
- Build: `/usr/bin/python3 ~/anhad-site/tools/assemble.py <your-src> <vN>` → serves at
  `http://localhost:4141/<vN>.html` (server already running).
- Screenshots: `bash ~/anhad-site/tools/shot.sh http://localhost:4141/<vN>.html ~/anhad-site/shots/<vN>`
  → then READ the PNGs (d1..dN desktop, m1..mN mobile). It also prints JS errors and
  horizontal-overflow offenders. Fix and re-shoot until: 0 JS errors, 0 offenders, and
  the pages genuinely look premium to you.
- No external requests of any kind (images/CSS/JS/fonts). Inline SVG for all graphics.
  Outbound <a href> links (LinkedIn, Drive, mailto, tel) are fine.

## Technical pitfalls we already paid for — do not repeat
- Absolutely-positioned REPLACED elements (svg/img) ignore left+right stretching; give
  them explicit width.
- `ch`/`em` on a wrapper resolve against the WRAPPER's font-size, not the child's.
- Stroke draw-on animations: set dasharray/offset from `getTotalLength()` in JS, never
  hand-guessed lengths.
- Marquees translating -50% need their content duplicated once in JS.
- IntersectionObserver reveals: everything must still be visible if JS dies —
  add `<noscript><style>.your-reveal-class{opacity:1;transform:none}</style></noscript>`.
- Touch targets ≥44px via BOTH `@media(pointer:coarse)` and `(max-width:760px)`.
- Test doc scrollWidth == viewport at 390px; shot.sh prints offenders.

## Quality bar (master-anhad standard)
- Exactly one <h1>. Semantic HTML. :focus-visible styled. ::selection themed.
- `prefers-reduced-motion: reduce` fully honoured (content reachable, nothing spins).
- Custom cursor (if any) desktop-only, hidden on coarse pointers.
- One 4px-based spacing scale; type ramp by ratio; tokens in :root — no ad-hoc hexes.
- Every interactive element: hover + focus-visible + active states.
- Copy: specific and witty per BRIEF voice. No lorem. No "delve". Em dashes sparingly.
- The page must answer: "what is the one visual idea here?" If a stranger could swap
  your palette onto a template and lose nothing, it has failed.
- Weight: keep total src (pre-fonts) under ~250 KB; JS hand-written, no libraries.

## Judging criteria (a critic agent will score you 1-10 on each)
distinctiveness · concept-to-Anhad fit · typography craft · interaction quality ·
storytelling/info completeness (journey, work, toolkit, quirks, contact, résumé) ·
mobile design intent · performance/robustness · quirk-that-lands
