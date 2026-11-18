"""Uji overflow di banyak lebar HP + ukuran huruf sistem diperbesar."""
import sys, threading, http.server, functools, json
from playwright.sync_api import sync_playwright
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parent; OUT = HERE / "output"; OUT.mkdir(exist_ok=True)

root = sys.argv[1] if len(sys.argv) > 1 else str(REPO); outdir = sys.argv[2] if len(sys.argv) > 2 else str(OUT)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 8770), functools.partial(Q, directory=root))
threading.Thread(target=httpd.serve_forever, daemon=True).start()

CHECK = r"""
() => {
  const vw = document.documentElement.clientWidth, out = [];
  const name = el => el.tagName.toLowerCase() + (el.id ? '#'+el.id : '') + (el.className && typeof el.className==='string' ? '.'+el.className.trim().split(/\s+/).join('.') : '');
  const vis = el => { if (el.closest('[hidden]') || el.closest('.booking-bar') || el.closest('.trap')) return false;
    const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden'; };
  if (document.documentElement.scrollWidth > vw) out.push('halaman scroll horizontal: ' + document.documentElement.scrollWidth + '>' + vw);
  for (const el of document.querySelectorAll('body *')) {
    if (!vis(el)) continue; const r = el.getBoundingClientRect(); if (!r.width) continue;
    if (r.right > vw + 0.5 || r.left < -0.5) out.push('keluar layar: ' + name(el) + ' [' + Math.round(r.left) + ',' + Math.round(r.right) + ']');
  }
  for (const box of ['.compact', '.look-panel', '.look-detail:not([hidden]) .look-body', '.booking-form', '.hero-inner']) {
    const b = document.querySelector(box); if (!b || getComputedStyle(b).display === 'contents') continue; const bb = b.getBoundingClientRect(), bs = getComputedStyle(b);
    const L = bb.left + parseFloat(bs.paddingLeft) + parseFloat(bs.borderLeftWidth), R = bb.right - parseFloat(bs.paddingRight) - parseFloat(bs.borderRightWidth);
    for (const el of b.querySelectorAll('*')) { if (!vis(el)) continue; const r = el.getBoundingClientRect(); if (!r.width) continue;
      if (r.right > R + 0.5 || r.left < L - 0.5) out.push('keluar area isi ' + box + ': ' + name(el) + ' [' + Math.round(r.left) + ',' + Math.round(r.right) + '] batas [' + Math.round(L) + ',' + Math.round(R) + ']'); }
  }
  for (const el of document.querySelectorAll('.pan-name, .btn, .chip, .look-detail h3, label, summary')) {
    if (!vis(el)) continue; if (el.scrollWidth > el.clientWidth + 1) out.push('teks terpotong: ' + name(el) + ' "' + el.textContent.trim().slice(0,30) + '"');
  }
  return [...new Set(out)];
}
"""
widths = [320, 360, 375, 390, 412, 430, 480, 600, 768, 820, 1024, 1366]
scales = [100, 115, 130]
looks = ["wisuda","lamaran","akad","bridesmaid"]
problems = {}
modes = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for w in widths:
        for sc in scales:
            ctx = b.new_context(viewport={"width": w, "height": 800}, device_scale_factor=2, is_mobile=True, has_touch=True, reduced_motion="reduce")
            pg = ctx.new_page()
            pg.route("https://fonts.**", lambda r: r.abort())
            # ukuran huruf diterapkan sebelum script jalan, seperti setelan huruf sistem di HP
            pg.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const st=document.createElement('style');st.textContent='html{font-size:%d%% !important}';document.head.appendChild(st)})" % sc)
            pg.goto("http://127.0.0.1:8770/index.html", wait_until="networkidle")
            pg.wait_for_timeout(150)
            modes.setdefault(sc, []).append(f"{w}:{pg.evaluate('document.querySelector(\'.pans\').className.replace(\'pans\',\'\').trim() || \'grid\'')}")
            found = set()
            for lk in looks:
                pg.click(f".pan[data-look='{lk}']"); pg.mouse.move(1, 1); pg.wait_for_timeout(60)
                for x in pg.evaluate(CHECK): found.add(f"[{lk}] {x}")
            if found: problems[f"{w}px @ {sc}%"] = sorted(found)
            if (w, sc) in [(320,100),(360,100),(360,130),(412,115),(768,100)]:
                pg.click(".pan[data-look='bridesmaid']"); pg.wait_for_timeout(400)
                el = pg.query_selector(".compact"); el.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
                pg.evaluate("document.getElementById('booking-bar').style.display='none'")
                el.screenshot(path=f"{outdir}/m{w}-{sc}.png")
            if (w, sc) == (360, 100):
                pg.evaluate("document.getElementById('booking-bar').style.display=''")
                pg.screenshot(path=f"{outdir}/m360-full.png", full_page=True)
            ctx.close()
    b.close()
httpd.shutdown()
total = len(widths) * len(scales)
print(f"Kombinasi diuji: {total} ({len(widths)} lebar x {len(scales)} ukuran huruf), tiap kombinasi 4 look")
for sc, m in modes.items(): print(f"Tata letak palet @ {sc}%:", " ".join(m))
if not problems: print("SEMUA BERSIH: tidak ada elemen keluar layar/kotak, tidak ada teks terpotong")
for k, v in problems.items():
    print(k); [print("   ", x) for x in v[:12]]
