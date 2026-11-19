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

    def open_page(vp=None, porto=PORTO, mode="ok", mobile=False, thumb=None, vendor_ctl=None):
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
        if vendor_ctl is not None:
            def vend(route):
                kind = "css" if route.request.url.split("?")[0].endswith(".css") else "js"
                if vendor_ctl.get("fail_" + kind): return route.abort()
                if vendor_ctl.get("delay"): pg.wait_for_timeout(vendor_ctl["delay"])
                route.continue_()
            pg.route("**/vendor/photoswipe/**", vend)
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
    pg.evaluate("""window.__capMut=0;new MutationObserver(m=>window.__capMut+=m.length).observe(document.querySelector('.pswp__caption-bar'),{childList:true,characterData:true,subtree:true})""")
    pg.wait_for_timeout(1500)
    check("keterangan tidak ditulis ulang saat ukuran foto dirapikan", pg.evaluate("window.__capMut") == 0, pg.evaluate("window.__capMut"))
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

    # Review: foto tersembunyi dicapai dengan geser satu-satu (dimuat duluan tanpa slide)
    ctx, pg, errors, vendor = open_page(thumb=lambda u: LANDSCAPE if "1KKKK" in u else None)
    k_hidden = pg.evaluate("(()=>{const i=[...document.querySelectorAll('.gallery .shot img[data-full]')].find(x=>x.dataset.caption==='Foto 11');return !!(i&&i.closest('.shot').hidden)})()")
    shot(pg, 7).click(); wait_bar(pg, f"Foto 9 · 8 / {TOTAL}"); pg.wait_for_timeout(2000)
    pg.keyboard.press("ArrowRight"); wait_bar(pg, f"Foto 10 · 9 / {TOTAL}"); pg.wait_for_timeout(1000)
    pg.keyboard.press("ArrowRight"); wait_bar(pg, f"Foto 11 · 10 / {TOTAL}"); pg.wait_for_timeout(1200)
    ratio = pg.evaluate("""(()=>{const s=[...document.querySelectorAll('.pswp__item')].find(i=>i.getAttribute('aria-hidden')==='false');
      const im=s&&s.querySelector('img.pswp__img:not(.pswp__img--placeholder)'); if(!im||!im.naturalWidth) return null;
      const r=im.getBoundingClientRect(); return [im.naturalWidth/im.naturalHeight, r.width/r.height]})()""")
    check("foto tersembunyi dicapai lewat geser: proporsi benar", k_hidden and ratio and abs(ratio[0] - ratio[1]) / ratio[0] < 0.03, (k_hidden, ratio))
    pg.keyboard.press("Escape"); wait_closed(pg); pg.wait_for_timeout(300)
    # Review: back ditekan saat animasi buka belum selesai
    url0 = pg.url
    shot(pg, 0).click(); pg.wait_for_selector(".pswp", timeout=3000)
    pg.evaluate("history.back()")
    check("back saat animasi buka: viewer tertutup", wait_closed(pg, 3000))
    pg.wait_for_timeout(300)
    check("back saat animasi buka: tetap di website", pg.url == url0, pg.url)
    check("review: tidak ada error JS", not errors, errors)
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

    # ---------- Perbaikan temuan kecil review ----------
    # a. Aksesibilitas & kode galeri tidak bocor ke global
    ctx, pg, errors, vendor = open_page()
    leak = pg.evaluate("['openViewer','galleryImages','slideFrom','viewer','opening','cssReady','FULL_WIDTH'].filter(n=>{try{return eval('typeof '+n)!=='undefined'}catch(e){return true}})")
    check("galeri.js tidak membuat nama global (aman bila main.js diedit)", not leak, leak)
    shot(pg, 0).click(); wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"); pg.wait_for_timeout(500)
    a11y = pg.evaluate("""({label:document.querySelector('.pswp').getAttribute('aria-label'), modal:document.querySelector('.pswp').getAttribute('aria-modal'),
      roles:[...new Set([...document.querySelectorAll('.pswp [aria-roledescription]')].map(e=>e.getAttribute('aria-roledescription')))]})""")
    check("pembaca layar: dialog bernama 'Foto portofolio' & aria-modal", a11y["label"] == "Foto portofolio" and a11y["modal"] == "true", a11y)
    check("pembaca layar: tanpa label Inggris carousel/slide", a11y["roles"] and not set(a11y["roles"]) & {"carousel", "slide"}, a11y["roles"])
    pg.keyboard.press("Escape"); wait_closed(pg)
    # b. Masuk lewat menu #portofolio, buka foto, tutup X, lalu back -> tetap di website, foto tidak terbuka lagi
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(300)
    pg.click("a[href='#portofolio']"); pg.wait_for_timeout(800)
    shot(pg, 0).click(); wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"); pg.wait_for_timeout(500)
    tap(pg, ".pswp__button--close"); wait_closed(pg); pg.wait_for_timeout(400)
    u1 = pg.url
    pg.go_back(); pg.wait_for_timeout(600)
    check("menu #portofolio -> foto -> X -> back: tetap di website & foto tidak terbuka", u1.endswith("#portofolio") and pg.url.startswith(URL) and not is_open(pg), (u1, pg.url, is_open(pg)))
    check("a/b: tidak ada error JS", not errors, errors)
    ctx.close()

    # c. Library gagal dimuat: tidak error, tidak ada riwayat nyangkut, klik berikutnya mencoba lagi
    for kind in ["js", "css"]:
        ctl = {"fail_" + kind: True}
        ctx, pg, errors, vendor = open_page(vendor_ctl=ctl)
        shot(pg, 0).click(); pg.wait_for_timeout(1200)
        st = pg.evaluate("history.state && history.state.natasyaFoto")
        check(f"{kind} library gagal: viewer tidak terbuka, tanpa error, tanpa riwayat", not is_open(pg) and not errors and not st, (is_open(pg), errors, st))
        ctl["fail_" + kind] = False
        shot(pg, 0).click()
        ok = wait_bar(pg, f"Foto 1 · 1 / {TOTAL}"); pg.wait_for_timeout(500)
        bg = pg.evaluate("(()=>{const e=document.querySelector('.pswp__bg');return e?getComputedStyle(e).backgroundColor:null})()")
        check(f"{kind} library gagal: klik lagi -> terbuka normal", ok and bg == "rgb(43, 23, 32)", (bar(pg), bg))
        ctx.close()

    # d. Foto di galeri berubah selama library masih diunduh -> tetap membuka foto yang diklik
    ctx, pg, errors, vendor = open_page(vendor_ctl={"delay": 900})
    shot(pg, 5).click(); pg.wait_for_timeout(150)
    pg.evaluate("document.querySelector('.gallery .shot').remove()")
    check("galeri berubah saat memuat: tetap membuka foto yang diklik (Foto 7)", wait_bar(pg, f"Foto 7 · 5 / {TOTAL - 1}", 4000), bar(pg))
    ctx.close()

    # e. Keterangan panjang di HP tidak menumpuk di foto tinggi, maksimal 2 baris
    buf = io.BytesIO(); Image.new("RGB", (900, 1600), (183, 132, 154)).save(buf, "JPEG"); TALL = buf.getvalue()
    longcap = "Wisuda Universitas Indonesia di Depok, hijab soft glam warna dusty pink dengan kebaya brokat putih dan softlens coklat natural"
    one_long = '"foto","keterangan","tampil","pratinjau"\n"' + D("A") + '","' + longcap + '","",""\n'
    ctx, pg, errors, vendor = open_page({"width": 375, "height": 760}, porto=one_long, mobile=True, thumb=lambda u: TALL)
    shot(pg, 0).tap(); pg.wait_for_selector(".pswp__caption-bar", timeout=3000); pg.wait_for_timeout(1200)
    geo = pg.evaluate("""(()=>{const s=[...document.querySelectorAll('.pswp__item')].find(i=>i.getAttribute('aria-hidden')==='false');
      const im=s.querySelector('img.pswp__img:not(.pswp__img--placeholder)')||s.querySelector('img.pswp__img');
      const b=document.querySelector('.pswp__caption-bar'), cs=getComputedStyle(b);
      return {imgBottom:Math.round(im.getBoundingClientRect().bottom), barTop:Math.round(b.getBoundingClientRect().top),
              lines:Math.round((b.scrollHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom))/parseFloat(cs.lineHeight)),
              text:b.textContent}})()""")
    check("HP keterangan panjang: maks 2 baris & tidak menumpuk di foto", geo["lines"] <= 2 and geo["imgBottom"] <= geo["barTop"], geo)
    check("HP keterangan panjang: dipendekkan dengan '…', nomor tetap utuh", "…" in geo["text"] and geo["text"].endswith("· 1 / 1"), geo["text"])
    pg.screenshot(path=str(OUT / "lightbox-hp-panjang.png"))
    ctx.close()

    # f. Link rusak di balik "Lihat lebih banyak": slide berisi pesan, tanpa error JS
    rows = [f'"{D(chr(65 + i)) if i != 11 else "https://drive.google.com/file/d/" + RUSAK + "/view"}","Foto {i + 1}","",""' for i in range(12)]
    porto_hidden_broken = '"foto","keterangan","tampil","pratinjau"\n' + "\n".join(rows) + "\n"
    ctx, pg, errors, vendor = open_page(porto=porto_hidden_broken)
    shot(pg, 0).click(); wait_bar(pg, "Foto 1 · 1 / 12"); pg.wait_for_timeout(500)
    pg.keyboard.press("ArrowLeft"); wait_bar(pg, "Foto 12 · 12 / 12"); pg.wait_for_timeout(1200)
    msg = pg.evaluate("[...document.querySelectorAll('.pswp__error-msg')].map(e=>e.innerText.trim()).filter(Boolean)")
    check("link rusak tersembunyi: tampil 'Foto tidak bisa dimuat'", "Foto tidak bisa dimuat" in msg, msg)
    check("link rusak tersembunyi: tidak ada error JS", not errors, errors)
    ctx.close()

    b.close()

httpd.shutdown()
bad = [r for r in results if not r[1]]
for n, ok, info in results:
    print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {info!r}"[:400]))
print(f"\n{len(results) - len(bad)}/{len(results)} lulus")
sys.exit(1 if bad else 0)
