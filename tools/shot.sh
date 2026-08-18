#!/bin/bash
# shot.sh <url> <outdir>  — progressive-scroll captures at 1440x900 + 390x844,
# prints console errors and horizontal-overflow offenders. Run from anywhere.
set -e
URL="$1"; OUT="$2"; mkdir -p "$OUT"
cd ~/.claude/skills/master-anhad/scripts
node - "$URL" "$OUT" <<'EOF'
const { chromium } = require('playwright');
const [url, out] = process.argv.slice(2);
(async () => {
  let b; try { b = await chromium.launch({channel:'chromium'}); } catch(e){ b = await chromium.launch(); }
  for (const [w,h,name] of [[1440,900,'d'],[390,844,'m']]) {
    const p = await b.newPage({viewport:{width:w,height:h}});
    const errs = [];
    p.on('pageerror', e=>errs.push('PAGEERROR: '+e));
    p.on('console', m=>{ if(m.type()==='error') errs.push('CONSOLE: '+m.text()); });
    await p.goto(url, {waitUntil:'networkidle'});
    await p.waitForTimeout(1200);
    const H = await p.evaluate(()=>document.documentElement.scrollHeight);
    for(let y=0;y<H;y+=h*0.75){ await p.evaluate(v=>scrollTo(0,v),y); await p.waitForTimeout(380); }
    await p.waitForTimeout(1400);
    const ov = await p.evaluate(() => {
      const vw = document.documentElement.clientWidth, out = [];
      if (document.documentElement.scrollWidth <= vw + 1) return out;
      document.querySelectorAll('*').forEach(el => {
        const r = el.getBoundingClientRect();
        const c = getComputedStyle(el);
        if (c.position === 'fixed') return;
        let n = el, clipped = false;
        while ((n = n.parentElement)) {
          const oc = getComputedStyle(n).overflowX;
          if (oc === 'hidden' || oc === 'auto' || oc === 'scroll') { clipped = true; break; }
        }
        if (!clipped && (r.right > vw + 1 || r.left < -1))
          out.push(`${el.tagName}.${[...el.classList].join('.')} L${r.left|0} R${r.right|0}`);
      });
      return out.slice(0, 12);
    });
    const n = Math.ceil(H/h);
    for(let i=0;i<n;i++){
      await p.evaluate(v=>scrollTo(0,v), i*h);
      await p.waitForTimeout(600);
      await p.screenshot({path:`${out}/${name}${i+1}.png`});
    }
    console.log(`[${name}] height=${H} views=${n} scrollW=${await p.evaluate(()=>document.documentElement.scrollWidth)}/${w}`);
    if (ov.length) console.log(`[${name}] OVERFLOW OFFENDERS:\n  ` + ov.join('\n  '));
    if (errs.length) console.log(`[${name}] JS ERRORS:\n  ` + errs.slice(0,8).join('\n  '));
    await p.close();
  }
  await b.close();
})();
EOF
