"""Tes tampilan foto besar (lightbox) di Portofolio, dengan Google Sheets & Drive tiruan, tanpa internet."""
import sys, threading, http.server, functools, urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent; REPO = HERE.parent; OUT = HERE / "output"; OUT.mkdir(exist_ok=True)
root = sys.argv[1] if len(sys.argv) > 1 else str(REPO)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 8790), functools.partial(Quiet, directory=root))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:8790/index.html"

SID = "TESTSHEETID_abcdefghijklmnop"
JPG = (HERE / "fixtures" / "foto-1.jpg").read_bytes()          # 800x1000
RUSAK = "1RUSAKRUSAKRUSAKRUSA"

def D(x): return f"https://drive.google.com/file/d/1{x * 20}/view?usp=sharing"

# 12 baris: baris ke-3 link rusak (404, terlihat di layar sehingga langsung terhapus),
# baris ke-5 tanpa keterangan. Foto valid = 11.
ROWS = []
for i in range(12):
    link = f"https://drive.google.com/file/d/{RUSAK}/view" if i == 2 else D(chr(65 + i))
    ket = "" if i == 4 else f"Foto {i + 1}"
    ROWS.append(f'"{link}","{ket}","",""')
PORTO = '"foto","keterangan","tampil","pratinjau"\n' + "\n".join(ROWS) + "\n"
TOTAL = 11

results = []
def check(n, c, i=""): results.append((n, bool(c), i))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])

    def open_page(vp=None, porto=PORTO, mode="ok", mobile=False, thumb=None):
        vp = vp or {"width": 1366, "height": 860}
        ctx = b.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile)
        pg = ctx.new_page()
        errors, vendor = [], []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("request", lambda r: vendor.append(r.url) if "photoswipe" in r.url else None)
        pg.route("https://fonts.g*/**", lambda r: r.abort())
        ctx.route("https://wa.me/**", lambda r: r.abort())
        ctx.route("https://script.google.com/**", lambda r: r.abort())
        def serve_js(route):
            import re
            body = re.sub(r'spreadsheetId: "[^"]*"', f'spreadsheetId: "{SID}"', route.fetch().text())
            body = re.sub(r'waNumber: "[^"]*"', 'waNumber: "6281200000001"', body)
            route.fulfill(body=body, content_type="application/javascript")
        pg.route("**/assets/js/main.js", serve_js)
        def gviz(route):
            if mode == "fail": return route.abort()
            tab = urllib.parse.parse_qs(urllib.parse.urlparse(route.request.url).query).get("sheet", [""])[0]
            body = porto if tab == "Portofolio" else '"bagian","letak di website","foto","pratinjau"\n'
            route.fulfill(body=body, content_type="text/csv", headers={"access-control-allow-origin": "*"})
        pg.route(f"https://docs.google.com/spreadsheets/d/{SID}/gviz/tq**", gviz)
        def drive(route):
            u = route.request.url
            if RUSAK in u: return route.fulfill(status=404, body="no")
            if thumb:
                special = thumb(u)
                if special is not None: return route.fulfill(body=special, content_type="image/jpeg")
            route.fulfill(body=JPG, content_type="image/jpeg")
        ctx.route("https://drive.google.com/thumbnail**", drive)
        pg.goto(URL, wait_until="networkidle")
        pg.evaluate("(async()=>{const s=document.querySelector('#portofolio');s.scrollIntoView();await new Promise(r=>setTimeout(r,600));window.scrollTo(0,0);})()")
        pg.wait_for_timeout(600)
        return ctx, pg, errors, vendor

    def bar(pg):
        el = pg.query_selector(".pswp__caption-bar")
        return el.inner_text().strip() if el else None
    def wait_bar(pg, text, timeout=3000):
        try:
            pg.wait_for_function("(t)=>{const e=document.querySelector('.pswp__caption-bar');return e&&e.innerText.trim()===t}", arg=text, timeout=timeout)
            return True
        except Exception:
            return False
    def is_open(pg): return pg.evaluate("!!document.querySelector('.pswp')")
    def wait_closed(pg, timeout=2500):
        try:
            pg.wait_for_function("!document.querySelector('.pswp')", timeout=timeout); return True
        except Exception:
            return False
    def tap(pg, sel):
        try: pg.click(sel, timeout=2000)
        except Exception: pass
    def shot(pg, n): return pg.locator(".gallery .shot img").nth(n)
    def active_src(pg):
        return pg.evaluate("(()=>{const s=[...document.querySelectorAll('.pswp__item')].find(i=>i.getAttribute('aria-hidden')==='false');const im=s&&s.querySelector('img.pswp__img:not(.pswp__img--placeholder)');return im?im.src:''})()")

    # ---------- Task 1: viewer dasar (laptop) ----------
    ctx, pg, errors, vendor = open_page()
    check("vendor belum dimuat sebelum klik", not vendor, vendor)
    check("foto rusak sudah terhapus dari galeri, sisa 11", pg.evaluate("document.querySelectorAll('.gallery .shot img[data-full]').length") == TOTAL,
          pg.evaluate("document.querySelectorAll('.gallery .shot img').length"))
    lbl = shot(pg, 0).get_attribute("aria-label") or ""
    check("foto bisa difokus keyboard & punya label", lbl.startswith("Lihat foto besar: ") and shot(pg, 0).get_attribute("tabindex") == "0", lbl)
    shot(pg, 0).click()
    check("klik foto 1 -> viewer terbuka dengan 'Foto 1 · 1 / 11'", wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"), bar(pg))
    pg.wait_for_timeout(500)
    check("slide memakai foto besar sz=w1600", "sz=w1600" in active_src(pg), active_src(pg))
    pg.keyboard.press("ArrowRight")
    check("ArrowRight -> 2 / 11", wait_bar(pg, f"Foto 2 · 2 / {TOTAL}"), bar(pg))
    tap(pg, ".pswp__button--arrow--next")
    check("tombol next -> 3 / 11 (foto 4, foto rusak dilewati)", wait_bar(pg, f"Foto 4 · 3 / {TOTAL}"), bar(pg))
    tap(pg, ".pswp__button--arrow--next")
    check("foto tanpa keterangan -> hanya nomor '4 / 11'", wait_bar(pg, f"4 / {TOTAL}"), bar(pg))
    tap(pg, ".pswp__button--arrow--prev")
    check("tombol prev -> kembali 3 / 11", wait_bar(pg, f"Foto 4 · 3 / {TOTAL}"), bar(pg))
    for _ in range(2): pg.keyboard.press("ArrowLeft"); pg.wait_for_timeout(250)
    check("di foto 1", wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"), bar(pg))
    pg.keyboard.press("ArrowLeft")
    check("looping: prev dari 1 -> 'Foto 12 · 11 / 11'", wait_bar(pg, f"Foto 12 · {TOTAL} / {TOTAL}"), bar(pg))
    pg.keyboard.press("ArrowRight")
    check("looping: next dari 11 -> 1 / 11", wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"), bar(pg))
    srcs = pg.evaluate("[...document.querySelectorAll('.pswp img')].map(i=>i.src)")
    check("tidak ada slide foto rusak", not any(RUSAK in s for s in srcs), srcs)
    tap(pg, ".pswp__button--close")
    check("tombol X menutup viewer", wait_closed(pg))
    shot(pg, 1).click(); wait_bar(pg, f"Foto 2 · 2 / {TOTAL}")
    pg.wait_for_timeout(500)  # tunggu animasi buka selesai (Esc diabaikan PhotoSwipe selama animasi)
    titles = pg.evaluate("({x:document.querySelector('.pswp__button--close')?.title,p:document.querySelector('.pswp__button--arrow--prev')?.title,n:document.querySelector('.pswp__button--arrow--next')?.title})")
    check("label tombol: Tutup / Foto sebelumnya / Foto berikutnya", titles == {"x": "Tutup", "p": "Foto sebelumnya", "n": "Foto berikutnya"}, titles)
    pg.keyboard.press("Escape")
    check("Esc menutup viewer", wait_closed(pg))
    pg.wait_for_timeout(300)
    bx = shot(pg, 0).bounding_box()
    pg.mouse.dblclick(bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2)
    pg.wait_for_timeout(1200)
    check("klik dobel cepat -> viewer tetap terbuka (ketukan ke-2 tidak menutup)", pg.evaluate("document.querySelectorAll('.pswp').length") == 1, pg.evaluate("document.querySelectorAll('.pswp').length"))
    pg.keyboard.press("Escape"); wait_closed(pg); pg.wait_for_timeout(300)
    shot(pg, 1).focus(); pg.keyboard.press("Enter")
    check("keyboard: Enter di foto 2 membuka 'Foto 2 · 2 / 11'", wait_bar(pg, f"Foto 2 · 2 / {TOTAL}"), bar(pg))
    pg.wait_for_timeout(700); pg.screenshot(path=str(OUT / "lightbox-laptop.png"))
    bg = pg.evaluate("getComputedStyle(document.querySelector('.pswp__bg')).backgroundColor")
    check("latar viewer warna maskara #2B1720", bg == "rgb(43, 23, 32)", bg)
    geo = pg.evaluate("""(()=>{const s=[...document.querySelectorAll('.pswp__item')].find(i=>i.getAttribute('aria-hidden')==='false');
      const im=s.querySelector('img.pswp__img:not(.pswp__img--placeholder)')||s.querySelector('img.pswp__img');
      const r=im.getBoundingClientRect(), t=document.querySelector('.pswp__caption-bar').getBoundingClientRect();
      return {imgBottom:Math.round(r.bottom), barTop:Math.round(t.top)}})()""")
    check("teks bawah tidak menumpuk di atas foto", geo["imgBottom"] <= geo["barTop"], geo)
    pg.keyboard.press("Escape"); wait_closed(pg)
    check("laptop: tidak ada error JS", not errors, errors)
    ctx.close()

    # Sheets gagal: kotak putih bawaan tidak bisa dibuka
    ctx, pg, errors, vendor = open_page(mode="fail")
    pg.locator(".gallery .shot img").first.click()
    pg.wait_for_timeout(1000)
    check("Sheets gagal: kotak putih tidak membuka viewer", not is_open(pg) and not vendor, vendor)
    check("Sheets gagal: tidak ada error JS", not errors, errors)
    ctx.close()

    # ---------- Task 2: back HP, geser, zoom, foto tersembunyi, proporsi ----------
    from PIL import Image
    import io
    buf = io.BytesIO(); Image.new("RGB", (900, 600), (138, 52, 86)).save(buf, "JPEG"); LANDSCAPE = buf.getvalue()
    ctx, pg, errors, vendor = open_page(thumb=lambda u: LANDSCAPE if "1LLLL" in u else None)
    url0 = pg.url
    hidden = pg.evaluate("document.querySelectorAll('.gallery .shot[hidden]').length")
    shot(pg, 0).click(); wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"); pg.wait_for_timeout(500)
    pg.keyboard.press("ArrowLeft")
    check("foto di balik 'Lihat lebih banyak' ikut (prev dari 1 -> Foto 12)", hidden > 0 and wait_bar(pg, f"Foto 12 · {TOTAL} / {TOTAL}"), (hidden, bar(pg)))
    pg.wait_for_timeout(1500)
    ratio = pg.evaluate("""(()=>{const s=[...document.querySelectorAll('.pswp__item')].find(i=>i.getAttribute('aria-hidden')==='false');
      const im=s&&s.querySelector('img.pswp__img:not(.pswp__img--placeholder)'); if(!im||!im.naturalWidth) return null;
      const r=im.getBoundingClientRect(); return [im.naturalWidth/im.naturalHeight, r.width/r.height]})()""")
    check("proporsi foto benar setelah foto besar termuat (tidak gepeng)", ratio and abs(ratio[0] - ratio[1]) / ratio[0] < 0.03, ratio)
    pg.keyboard.press("ArrowRight"); wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"); pg.wait_for_timeout(400)
    def drag(dx, dy):
        bx = pg.evaluate("(()=>{const r=document.querySelector('.pswp__scroll-wrap').getBoundingClientRect();return [r.width/2, r.height/2]})()")
        pg.mouse.move(bx[0], bx[1]); pg.mouse.down()
        for k in range(1, 11): pg.mouse.move(bx[0] + dx * k / 10, bx[1] + dy * k / 10); pg.wait_for_timeout(16)
        pg.mouse.up()
    drag(-320, 0)
    check("geser kiri -> foto berikutnya (2 / 11)", wait_bar(pg, f"Foto 2 · 2 / {TOTAL}"), bar(pg))
    pg.wait_for_timeout(500)
    pg.go_back()
    check("tombol back menutup viewer", wait_closed(pg))
    check("tombol back: tetap di website", pg.url == url0, pg.url)
    if pg.url != url0:  # back keluar dari website (bug): muat ulang supaya cek lain tetap jalan
        pg.goto(URL, wait_until="networkidle")
        pg.evaluate("document.querySelector('#portofolio').scrollIntoView()"); pg.wait_for_timeout(800)
    pg.wait_for_timeout(300)
    shot(pg, 0).click(); wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"); pg.wait_for_timeout(500)
    tap(pg, ".pswp__button--close"); wait_closed(pg); pg.wait_for_timeout(300)
    st = pg.evaluate("history.state && history.state.natasyaFoto")
    check("tutup pakai X: tidak ada riwayat 'foto' tersisa", not st and pg.url == url0, (st, pg.url))
    shot(pg, 0).click()
    check("buka lagi setelah X tetap bisa", wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"), bar(pg))
    pg.wait_for_timeout(500)
    drag(0, 320)
    check("geser ke bawah menutup viewer", wait_closed(pg))
    check("geser ke bawah: tidak ada riwayat 'foto' tersisa", not pg.evaluate("history.state && history.state.natasyaFoto"))
    check("Task 2 laptop: tidak ada error JS", not errors, errors)
    ctx.close()

    # HP: panah terlihat, ketuk 2x zoom
    ctx, pg, errors, vendor = open_page({"width": 375, "height": 760}, mobile=True)
    shot(pg, 0).tap()
    wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"); pg.wait_for_timeout(600)
    vis = pg.evaluate("getComputedStyle(document.querySelector('.pswp__button--arrow--next')).visibility")
    check("HP: tombol panah terlihat", vis == "visible", vis)
    pg.screenshot(path=str(OUT / "lightbox-hp.png"))
    c = pg.evaluate("(()=>{const r=document.querySelector('.pswp__scroll-wrap').getBoundingClientRect();return [r.width/2, r.height/2]})()")
    pg.touchscreen.tap(c[0], c[1]); pg.wait_for_timeout(120); pg.touchscreen.tap(c[0], c[1]); pg.wait_for_timeout(700)
    check("HP: ketuk 2x -> zoom", pg.evaluate("document.querySelector('.pswp').classList.contains('pswp--zoomed-in')"),
          pg.evaluate("document.querySelector('.pswp')?.className"))
    check("HP: tidak ada error JS", not errors, errors)
    ctx.close()

    # Portofolio hanya 1 foto
    one = '"foto","keterangan","tampil","pratinjau"\n"' + D("A") + '","Foto 1","",""\n'
    ctx, pg, errors, vendor = open_page(porto=one)
    shot(pg, 0).click()
    check("satu foto: 'Foto 1 · 1 / 1'", wait_bar(pg, "Foto 1 · 1 / 1"), bar(pg))
    pg.wait_for_timeout(500)
    av = pg.evaluate("getComputedStyle(document.querySelector('.pswp__button--arrow--next')).display")
    check("satu foto: tanpa tombol panah", av == "none", av)
    check("satu foto: tidak ada error JS", not errors, errors)
    ctx.close()

    b.close()

httpd.shutdown()
bad = [r for r in results if not r[1]]
for n, ok, info in results:
    print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {info!r}"[:400]))
print(f"\n{len(results) - len(bad)}/{len(results)} lulus")
sys.exit(1 if bad else 0)
