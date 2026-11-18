"""Pilih look: ukuran foto sama, kotak gelap muat 1 layar laptop, info penting tidak terpotong, Lihat selengkapnya."""
import sys, threading, http.server, functools
from playwright.sync_api import sync_playwright
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parent; OUT = HERE / "output"; OUT.mkdir(exist_ok=True)
root = sys.argv[1] if len(sys.argv) > 1 else str(REPO); shots = len(sys.argv) > 2
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8794), functools.partial(Q, directory=root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
LOOKS = ["wisuda", "lamaran", "akad", "bridesmaid"]
res = []
def check(n, c, i=""): res.append((n, bool(c), i))
# ukuran jendela browser laptop umum (tinggi = area halaman setelah toolbar browser)
VIEWS = [(1366, 657, "laptop 1366x768"), (1440, 789, "laptop 1440x900"), (1536, 730, "laptop 1536x864"), (1280, 610, "laptop 1280x720"),
         (1920, 969, "monitor 1920x1080"), (1024, 660, "laptop kecil 1024"), (820, 1000, "tablet 820"), (375, 760, "HP 375")]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for w, hgt, name in VIEWS:
        for sc in ([100, 115] if w >= 1024 else [100]):
            ctx = b.new_context(viewport={"width": w, "height": hgt}, reduced_motion="reduce"); pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            for pat in ["https://docs.google.com/**", "https://script.google.com/**", "https://fonts.g*/**", "https://wa.me/**"]: pg.route(pat, lambda r: r.abort())
            if sc != 100:
                pg.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const st=document.createElement('style');st.textContent='html{font-size:%d%% !important}';document.head.appendChild(st)})" % sc)
            pg.goto(f"http://127.0.0.1:8794/index.html", wait_until="networkidle"); pg.wait_for_timeout(300)
            tag = f"{name} @{sc}%"
            data = {}
            for lk in LOOKS:
                pg.click(f".pan[data-look='{lk}']"); pg.wait_for_timeout(120)
                data[lk] = pg.evaluate("""(lk)=>{const d=document.querySelector(`.look-detail[data-look=${lk}]`);
                  const r=e=>e.getBoundingClientRect(); const ph=r(d.querySelector('.look-photo')), info=d.querySelector('.look-info'), ir=r(info);
                  const rows=[...d.querySelectorAll('.look-meta > div')].map(x=>({dt:x.querySelector('dt').textContent, cut: r(x).bottom > ir.bottom + 1}));
                  const more=d.querySelector('.look-more');
                  const ov=getComputedStyle(info).overflow, mr=r(more), br=r(d.querySelector('.btn')), body=r(d.querySelector('.look-body')), pans=r(document.querySelector('.pans')), comp=r(document.querySelector('.compact'));
                  const leak = !more.hidden && (ov !== 'hidden');
                  const overlap = (!more.hidden && mr.bottom > br.top + 1) || ir.bottom > (more.hidden ? br.top : mr.top) + 1;
                  const outside = br.bottom > body.bottom + 1;
                  return {leak, overlap, outside, ph:[Math.round(ph.width),Math.round(ph.height)], compact:Math.round(r(document.querySelector('.compact')).height),
                    rows, more: !more.hidden, btn: br.height > 0 && br.bottom <= body.bottom + 1, header: Math.round(r(document.querySelector('.site-header')).height),
                    lay: {pansBottom: pans.bottom, pansLeft: pans.left, pansTop: pans.top, phTop: ph.top, phLeft: ph.left, phRight: ph.right, phW: ph.width,
                          bodyLeft: body.left, bodyTop: body.top, bodyBottom: body.bottom, phBottom: ph.bottom, compW: comp.width}}}""", lk)
            sizes = {tuple(v["ph"]) for v in data.values()}
            side = w >= 761
            if side:
                check(f"{tag}: 4 foto look ukurannya sama", len(sizes) == 1, sizes)
                ph = list(sizes)[0]
                if w > 960:
                    L = data["wisuda"]["lay"]
                    check(f"{tag}: pilihan look di kiri atas, foto di bawahnya, info di kanan",
                          L["phTop"] >= L["pansBottom"] - 1 and abs(L["phLeft"] - L["pansLeft"]) <= 2 and L["bodyLeft"] >= L["phRight"] + 8 and abs(L["bodyTop"] - L["pansTop"]) <= 2, L)
                    check(f"{tag}: foto besar mengikuti lebar kolom (lebar {ph[0]}px >= 45% kotak, tinggi 320-640px)", ph[0] >= 0.45 * L["compW"] and 320 <= ph[1] <= 640, (ph, round(L["compW"])))
                    check(f"{tag}: bawah foto sejajar bawah kotak info", abs(L["phBottom"] - L["bodyBottom"]) <= 2, (L["phBottom"], L["bodyBottom"]))
                else:
                    check(f"{tag}: ukuran foto wajar (tinggi 360-540px)", 360 <= ph[1] <= 540, ph)
                if w > 960:
                    comp = max(v["compact"] for v in data.values())
                    check(f"{tag}: kotak gelap muat 1 layar ({comp}px <= {hgt - data['wisuda']['header']}px)", comp <= hgt - data["wisuda"]["header"], comp)
                imp_cut = {lk: [r["dt"] for r in v["rows"] if r["cut"] and r["dt"] in ("Mulai dari", "Harga", "Harga promo", "Sudah termasuk")] for lk, v in data.items()}
                check(f"{tag}: harga & isi paket tidak terpotong", not any(imp_cut.values()), {k: v for k, v in imp_cut.items() if v})
                any_cut = {lk: v["more"] for lk, v in data.items()}
                check(f"{tag}: tombol Booking selalu terlihat", all(v["btn"] for v in data.values()))
                check(f"{tag}: teks yang disembunyikan benar-benar terpotong (tidak bocor)", not any(v["leak"] for v in data.values()), {k: v["leak"] for k, v in data.items() if v["leak"]})
                check(f"{tag}: teks tidak menimpa tombol", not any(v["overlap"] for v in data.values()), {k: 1 for k, v in data.items() if v["overlap"]})
                check(f"{tag}: tombol Booking di dalam kotak", not any(v["outside"] for v in data.values()), {k: 1 for k, v in data.items() if v["outside"]})
                res.append((f"{tag}: info: foto {ph[0]}x{ph[1]}, 'Lihat selengkapnya' muncul di: " + (", ".join(k for k, v in any_cut.items() if v) or "-"), True, ""))
                # buka-tutup di look yang terpotong
                lk = next((k for k, v in any_cut.items() if v), None)
                if lk:
                    pg.click(f".pan[data-look='{lk}']"); pg.wait_for_timeout(100)
                    before = pg.evaluate(f"document.querySelector('.look-detail[data-look={lk}] .look-body').getBoundingClientRect().height")
                    pg.click(f".look-detail[data-look={lk}] .look-more"); pg.wait_for_timeout(100)
                    st = pg.evaluate(f"""(()=>{{const d=document.querySelector('.look-detail[data-look={lk}]'),i=d.querySelector('.look-info'),m=d.querySelector('.look-more');
                       return {{h:d.querySelector('.look-body').getBoundingClientRect().height, full:i.scrollHeight<=i.clientHeight+1, exp:m.getAttribute('aria-expanded'), txt:m.textContent,
                       ph:Math.round(d.querySelector('.look-photo').getBoundingClientRect().height)}}}})()""")
                    check(f"{tag}: 'Lihat selengkapnya' ({lk}) membuka semua teks, foto tetap ukuran sama", st["full"] and st["h"] > before and st["exp"] == "true" and st["ph"] == ph[1] and st["txt"] == "Tampilkan lebih sedikit", st)
                    pg.click(f".look-detail[data-look={lk}] .look-more"); pg.wait_for_timeout(100)
                    h2 = pg.evaluate(f"document.querySelector('.look-detail[data-look={lk}] .look-body').getBoundingClientRect().height")
                    check(f"{tag}: 'Tampilkan lebih sedikit' kembali ke ukuran awal", abs(h2 - before) <= 1, (before, h2))
                    pg.click(f".look-detail[data-look={lk}] .look-more"); pg.click(".pan[data-look='akad']" if lk != "akad" else ".pan[data-look='wisuda']"); pg.click(f".pan[data-look='{lk}']")
                    check(f"{tag}: ganti look -> kembali ringkas", pg.evaluate(f"!document.querySelector('.look-detail[data-look={lk}]').classList.contains('is-open')"))
                    if shots and sc == 100 and w == 1366:
                        pg.click(f".look-detail[data-look={lk}] .look-more"); pg.wait_for_timeout(100)
                        pg.locator(".compact").screenshot(path=f"{OUT}/look-open-{w}.png")
                        pg.click(f".look-detail[data-look={lk}] .look-more")
            else:
                check(f"{tag}: HP tanpa tombol 'Lihat selengkapnya' (tidak berubah)", not any(v["more"] for v in data.values()))
            sw = pg.evaluate("document.documentElement.scrollWidth"); cw = pg.evaluate("document.documentElement.clientWidth")
            check(f"{tag}: tidak ada scroll horizontal", sw <= cw, (sw, cw))
            check(f"{tag}: tidak ada error JS", not errs, errs)
            if shots and sc == 100 and side:
                for lk in ["wisuda", "akad"]:
                    pg.click(f".pan[data-look='{lk}']"); pg.wait_for_timeout(100)
                    pg.evaluate("window.scrollTo(0, document.querySelector('.compact').getBoundingClientRect().top + scrollY - document.querySelector('.site-header').offsetHeight - 8)")
                    pg.wait_for_timeout(200); pg.screenshot(path=f"{OUT}/look-{w}-{lk}.png")
            ctx.close()
    b.close()
bad = [r for r in res if not r[1]]
for n, ok, i in res: print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {i}"))
print(f"\n{len(res)-len(bad)}/{len(res)} lulus"); sys.exit(1 if bad else 0)
