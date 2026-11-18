"""Tes loader Google Sheets (gviz + cadangan csvUrls) dengan data tiruan, tanpa internet."""
import sys, re, threading, http.server, functools, time, urllib.parse
from playwright.sync_api import sync_playwright
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parent; OUT = HERE / "output"; OUT.mkdir(exist_ok=True)

root = sys.argv[1] if len(sys.argv) > 1 else str(REPO)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 8766), functools.partial(Quiet, directory=root))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:8766/index.html"
class SlowCsv(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        time.sleep(int(q.get("delay", ["0"])[0]) / 1000)
        body = TABS[q["tab"][0]].encode()
        self.send_response(200); self.send_header("Content-Type", "text/csv")
        self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers(); self.wfile.write(body)
slow = http.server.ThreadingHTTPServer(("127.0.0.1", 8767), SlowCsv)
threading.Thread(target=slow.serve_forever, daemon=True).start()
SID = "TESTSHEETID_abcdefghijklmnop"
jpg = open(HERE / "fixtures" / "foto-1.jpg", "rb").read()
jpg2 = open(HERE / "fixtures" / "foto-2.jpg", "rb").read()
jpg_long = open(HERE / "fixtures" / "chat-panjang.jpg", "rb").read()
jpg_short = open(HERE / "fixtures" / "chat-pendek.jpg", "rb").read()

def D(x): return f"https://drive.google.com/file/d/1{x * 20}/view?usp=sharing"

TABS = {
"Foto Utama": f'''"bagian","letak di website","foto","pratinjau"
"hero","Foto besar paling atas","{D('H')}",""
"tentang","Foto Natasya","{D('T')}",""
"look-wisuda","Pilih look: Wisuda","{D('W')}",""
"look-bridesmaid","Pilih look: Bridesmaid","https://drive.google.com/file/d/1RUSAKRUSAKRUSAKRUSA/view",""
"look-akad","Pilih look: Akad","",""
"slot-ngawur","tidak ada","{D('X')}",""
''',
"Portofolio": f'''"foto","keterangan","tampil","pratinjau"
"{D('A')}","Wisuda UI, hijab ""soft glam""","",""
"https://drive.google.com/open?id=1{'B'*20}","","",""
"{D('C')}","Akad di Depok","ya",""
"{D('D')}","","",""
"{D('E')}","Kebaya merah","",""
"{D('F')}","Foto yang disembunyikan","tidak",""
"tidak-ada-link","Link bukan URL","",""
"https://drive.google.com/file/d/1RUSAKRUSAKRUSAKRUSA/view","Foto rusak (404)","",""
"javascript:alert(1)","XSS coba","",""
''',
"Testimoni": f'''"foto","teks","nama","tampil","pratinjau"
"{D('S')}","","Rani","",""
"","Hasilnya <img src=x onerror=window.__xss=1> bagus banget","Dina","",""
"","Disembunyikan","Eka","tidak",""
"","","","",""
'''}

port_rows = []
for i in range(20):
    link = "https://drive.google.com/file/d/1RUSAKRUSAKRUSAKRUSA/view" if i == 9 else D(chr(65 + i % 26))
    port_rows.append(f'"{link}","Foto {i + 1}","",""')
testi_rows = [f'"https://drive.google.com/file/d/1LONGLONGLONGLONGLONG/view","","Panjang","",""',
              f'"https://drive.google.com/file/d/1SHORTSHORTSHORTSHORT/view","","Pendek","",""'] + [f'"","Testimoni teks {i}","Klien {i}","",""' for i in range(8)]
TABS_MANY = {
    "Foto Utama": TABS["Foto Utama"],
    "Portofolio": '"foto","keterangan","tampil","pratinjau"\n' + "\n".join(port_rows) + "\n",
    "Testimoni": '"foto","teks","nama","tampil","pratinjau"\n' + "\n".join(testi_rows) + "\n",
}

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    results = []
    def check(n, c, i=""): results.append((n, bool(c), i))

    def open_page(vp, mode="ok", config=True, csv_delay_ms=0, csv_urls=None):
        ctx = b.new_context(viewport=vp, reduced_motion="reduce")
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.route("https://fonts.g*/**", lambda r: r.abort())
        ctx.route("https://wa.me/**", lambda r: r.abort())
        def serve_js(route):
                import re
                body = re.sub(r'spreadsheetId: "[^"]*"', f'spreadsheetId: "{SID if config else ""}"', route.fetch().text())
                body = re.sub(r'waNumber: "[^"]*"', 'waNumber: "6281200000001"', body)
                if csv_urls:
                    body = body.replace('csvUrls: { photos: "", portfolio: "", testimonials: "" }',
                        'csvUrls: { photos: "%s", portfolio: "%s", testimonials: "%s" }' % csv_urls)
                route.fulfill(body=body, content_type="application/javascript")
        pg.route("**/assets/js/main.js", serve_js)
        def gviz(route):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(route.request.url).query)
            tab = q.get("sheet", [""])[0]
            if mode == "fail": return route.abort()
            if mode == "login": return route.fulfill(body="<!DOCTYPE html><html><body>Sign in</body></html>", content_type="text/html", headers={"access-control-allow-origin": "*"})
            if mode == "empty": return route.fulfill(body=TABS[tab].splitlines()[0] + "\n", content_type="text/csv", headers={"access-control-allow-origin": "*"})
            src = TABS_MANY if mode == "many" else TABS
            route.fulfill(body=src.get(tab, ""), content_type="text/csv", headers={"access-control-allow-origin": "*"})
        pg.route(f"https://docs.google.com/spreadsheets/d/{SID}/gviz/tq**", gviz)
        def thumb(route):
            u = route.request.url
            if "1RUSAK" in u: route.fulfill(status=404, body="no")
            elif "1LONG" in u: route.fulfill(body=jpg_long, content_type="image/jpeg")
            elif "1SHORT" in u: route.fulfill(body=jpg_short, content_type="image/jpeg")
            else: route.fulfill(body=jpg2 if ("DDDD" in u or "HHHH" in u) else jpg, content_type="image/jpeg")
        pg.route("https://drive.google.com/thumbnail**", thumb)
        return ctx, pg, errors

    def scroll(pg):
        pg.evaluate("(async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,50));}window.scrollTo(0,0);})()")
        pg.wait_for_timeout(700)

    EMPTY = "data:image/gif;base64,"
    def img_state(pg, sel):
        return pg.evaluate("(s)=>{const i=document.querySelector(s);return {src:i.getAttribute('src'),alt:i.alt,empty:i.classList.contains('is-empty'),ok:i.complete&&i.naturalWidth>0,bg:getComputedStyle(i).backgroundColor}}", sel)
    PLACEHOLDER_JS = "[...document.querySelectorAll('img')].filter(i=>i.classList.contains('is-empty')&&i.getAttribute('src').startsWith('data:image/gif')).length"

    # 1. Normal
    ctx, pg, errors = open_page({"width": 1366, "height": 860})
    reqs, local = [], []
    pg.on("request", lambda r: reqs.append(r.url) if "gviz" in r.url else (local.append(r.url) if re.search(r"/assets/img/(hero|profil|portfolio/)", r.url) else None))
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(500); scroll(pg)
    check("gviz dipanggil per tab dengan headers=1", len(reqs) == 3 and all("tqx=out:csv&headers=1&sheet=" in u for u in reqs), reqs)
    check("tidak ada request ke foto lama (assets/img)", not local, local)
    h = img_state(pg, ".hero-mirror img")
    check("hero diganti foto dari sheet & tidak putih lagi", "thumbnail?id=1HHHH" in h["src"] and "sz=w800" in h["src"] and h["ok"] and not h["empty"], h)
    check("alt hero diisi", h["alt"] == "Natasya, makeup artist Natasya Makeup", h["alt"])
    a = img_state(pg, ".about-photo")
    check("foto Natasya (Tentang) diganti & termuat", "1TTTT" in a["src"] and a["ok"] and not a["empty"] and a["alt"] == "Natasya, MUA di Depok", a)
    pg.click(".pan[data-look='wisuda']"); pg.wait_for_timeout(400)
    w = img_state(pg, ".look-detail[data-look=wisuda] img")
    check("Pilih look Wisuda diganti & termuat", "1WWWW" in w["src"] and w["ok"] and not w["empty"], w)
    pg.click(".pan[data-look='bridesmaid']"); pg.wait_for_timeout(800)
    t = img_state(pg, ".look-detail[data-look=bridesmaid] img")
    check("look Bridesmaid link rusak -> jadi kotak putih", t["src"].startswith(EMPTY) and t["empty"] and t["alt"] == "" and t["bg"] == "rgb(255, 255, 255)", t)
    pg.click(".pan[data-look='akad']"); pg.wait_for_timeout(400)
    k = img_state(pg, ".look-detail[data-look=akad] img")
    check("look Akad kosong di sheet -> kotak putih", k["src"].startswith(EMPTY) and k["empty"], k)
    shots = pg.evaluate("[...document.querySelectorAll('.shot')].map(s=>({c:s.dataset.category||null,t:s.querySelector('figcaption')?.textContent??null,alt:s.querySelector('img').alt,e:s.querySelector('img').classList.contains('is-empty')}))")
    check("galeri: kotak putih diganti 5 foto valid dari sheet", len(shots) == 5 and not any(x["e"] for x in shots), shots)
    check("galeri tanpa kategori: tidak ada tombol filter & data kategori", pg.evaluate("document.querySelectorAll('.chip,.filters,[data-filter]').length") == 0 and all(x["c"] is None for x in shots), shots)
    check("keterangan bertanda kutip & koma utuh", shots and shots[0]['t'] == 'Wisuda UI, hijab "soft glam"', shots[0]['t'] if shots else "")
    check("foto tanpa keterangan: tanpa tulisan di bawah foto, alt 'Hasil makeup Natasya'", shots and shots[1]['t'] is None and shots[1]['alt'] == "Hasil makeup Natasya", shots[1] if len(shots) > 1 else None)
    tb = pg.evaluate("[...document.querySelectorAll('.bubbles > *')].map(e=>({cls:e.className,txt:e.textContent.trim()}))")
    check("testimoni: 1 screenshot + 1 teks", len(tb) == 2 and 'bubble-shot' in tb[0]['cls'], tb)
    check("teks berbahaya tidak dieksekusi", pg.evaluate("window.__xss") is None)
    sw = pg.evaluate("document.documentElement.scrollWidth"); cw = pg.evaluate("document.documentElement.clientWidth")
    check("desktop: tidak ada scroll horizontal", sw <= cw, f"{sw}/{cw}")
    check("tidak ada error JS", not errors, errors)
    ctx.close()

    # 2. Mobile
    ctx, pg, errors = open_page({"width": 375, "height": 760})
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(500); scroll(pg)
    sw = pg.evaluate("document.documentElement.scrollWidth"); cw = pg.evaluate("document.documentElement.clientWidth")
    check("mobile: tidak ada scroll horizontal", sw <= cw, f"{sw}/{cw}")
    check("mobile: tidak ada error JS", not errors, errors)
    ctx.close()

    # 3. Sheet lambat (4 detik): kotak putih dulu, lalu foto
    base = "http://127.0.0.1:8767/?delay=4000&tab="
    ctx, pg, errors = open_page({"width": 1366, "height": 860}, csv_urls=tuple(base + urllib.parse.quote(t) for t in ["Foto Utama", "Portofolio", "Testimoni"]))
    gv = []
    pg.on("request", lambda r: gv.append(r.url) if "gviz" in r.url else None)
    pg.goto(URL, wait_until="domcontentloaded"); pg.wait_for_timeout(1500)
    h = img_state(pg, ".hero-mirror img")
    check("sheet lambat: hero kotak putih dulu (bukan foto lama)", h["src"].startswith(EMPTY) and h["empty"] and h["bg"] == "rgb(255, 255, 255)", h)
    pg.wait_for_timeout(4000)
    h = img_state(pg, ".hero-mirror img")
    check("sheet lambat: hero terisi setelah sheet datang", "1HHHH" in h["src"] and not h["empty"], h)
    check("cadangan csvUrls dipakai, gviz tidak dipanggil", not gv, gv)
    ctx.close()

    # 4. Gagal / sheet private / kosong: semua kotak putih, testimoni teks tetap
    for mode, name in [("fail", "Sheets diblokir"), ("login", "sheet masih private"), ("empty", "sheet kosong")]:
        ctx, pg, errors = open_page({"width": 1366, "height": 860}, mode=mode)
        pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(400); scroll(pg)
        n = pg.evaluate(PLACEHOLDER_JS)
        nb = pg.evaluate("document.querySelectorAll('.bubbles > blockquote.bubble').length")
        broken = pg.evaluate("[...document.images].filter(i=>!i.closest('[hidden]')).filter(i=>!i.complete||i.naturalWidth===0).length")
        check(f"{name}: 12 kotak putih, 5 testimoni teks, tidak ada ikon gambar rusak", n == 12 and nb == 5 and broken == 0, (n, nb, broken))
        check(f"{name}: tidak ada error JS", not errors, errors)
        ctx.close()

    # 5. Tanpa spreadsheetId
    ctx, pg, errors = open_page({"width": 1366, "height": 860}, config=False)
    gv = []
    pg.on("request", lambda r: gv.append(r.url) if "docs.google.com" in r.url else None)
    pg.goto(URL, wait_until="networkidle")
    n = pg.evaluate(PLACEHOLDER_JS)
    check("tanpa spreadsheetId: tidak memanggil Google, 12 kotak putih", not gv and n == 12 and not errors, (gv, n, errors))
    pg.locator(".hero").screenshot(path=f"{OUT}/kosong-hero.png")
    pg.locator("#portofolio").screenshot(path=f"{OUT}/kosong-portofolio.png")
    ctx.close()

    # 6. Kotak putih di HP
    ctx, pg, errors = open_page({"width": 375, "height": 760}, config=False)
    pg.goto(URL, wait_until="networkidle"); scroll(pg)
    sw = pg.evaluate("document.documentElement.scrollWidth"); cw = pg.evaluate("document.documentElement.clientWidth")
    check("mobile kosong: tidak ada scroll horizontal", sw <= cw, f"{sw}/{cw}")
    pg.screenshot(path=f"{OUT}/kosong-mobile.png", full_page=True)
    ctx.close()

    # 7. Banyak foto & testimoni: tombol "Lihat lebih banyak" + screenshot panjang
    VIS = "(s)=>[...document.querySelectorAll(s)].filter(e=>!e.hidden).length"
    BTN = "(id)=>{const b=document.getElementById(id);return {shown:!b.hidden&&getComputedStyle(b).display!=='none',txt:b.textContent}}"
    ctx, pg, errors = open_page({"width": 1366, "height": 860}, mode="many")
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(500); scroll(pg)
    check("laptop: galeri tampil 9 foto dulu", pg.evaluate(VIS, ".shot") == 9, pg.evaluate(VIS, ".shot"))
    bt = pg.evaluate(BTN, "gallery-load")
    check("laptop: tombol galeri 'Lihat lebih banyak' tampil", bt["shown"] and bt["txt"] == "Lihat lebih banyak", bt)
    pg.click("#gallery-load"); pg.wait_for_timeout(500); n1 = pg.evaluate(VIS, ".shot"); t1 = pg.evaluate(BTN, "gallery-load")
    pg.click("#gallery-load"); pg.wait_for_timeout(500); n2 = pg.evaluate(VIS, ".shot"); t2 = pg.evaluate(BTN, "gallery-load")
    total = pg.evaluate("document.querySelectorAll('.shot').length")
    check("laptop: klik -> 18 foto, klik lagi -> 19 (foto rusak dibuang) & tombol hilang", n1 == 18 and t1["shown"] and n2 == 19 and total == 19 and not t2["shown"], (n1, t1, n2, t2, total))
    check("laptop: testimoni tampil 6 dari 10", pg.evaluate(VIS, ".bubbles > .bubble") == 6 and pg.evaluate(BTN, "testi-load")["shown"])
    pg.click("#testi-load")
    check("laptop: klik -> 10 testimoni, tombol hilang", pg.evaluate(VIS, ".bubbles > .bubble") == 10 and not pg.evaluate(BTN, "testi-load")["shown"])
    SHOT = """(n)=>{const f=[...document.querySelectorAll('.bubble-shot')].find(x=>x.querySelector('figcaption').textContent===n);
      const t=f.querySelector('.shot-toggle');return {tall:f.classList.contains('is-tall'),clip:Math.round(f.querySelector('.shot-clip').getBoundingClientRect().height),
      img:Math.round(f.querySelector('img').getBoundingClientRect().height),btn:getComputedStyle(t).display!=='none',exp:t.getAttribute('aria-expanded'),txt:t.textContent}}"""
    lg = pg.evaluate(SHOT, "Panjang")
    check("screenshot panjang dipotong maks 420px + tombol 'Lihat chat lengkap'", lg["tall"] and lg["clip"] <= 420 and lg["img"] > 1000 and lg["btn"] and lg["exp"] == "false", lg)
    sh = pg.evaluate(SHOT, "Pendek")
    check("screenshot pendek tampil utuh tanpa tombol", not sh["tall"] and abs(sh["clip"] - sh["img"]) <= 1 and not sh["btn"], sh)
    pg.locator(".bubble-shot .shot-toggle >> visible=true").first.click()
    op = pg.evaluate(SHOT, "Panjang")
    check("klik 'Lihat chat lengkap' -> utuh, tombol jadi 'Tutup'", op["clip"] > 1000 and op["exp"] == "true" and op["txt"] == "Tutup", op)
    pg.locator(".bubble-shot .shot-toggle >> visible=true").first.click()
    cl = pg.evaluate(SHOT, "Panjang")
    check("klik 'Tutup' -> dipotong lagi", cl["clip"] <= 420 and cl["exp"] == "false", cl)
    pg.evaluate("document.querySelector('.bubble-shot.is-tall').scrollIntoView({block:'center'})")
    pg.locator(".bubble-shot.is-tall .shot-clip").first.click()
    check("ketuk gambar screenshot juga membuka utuh", pg.evaluate(SHOT, "Panjang")["exp"] == "true")
    check("laptop: tidak ada error JS", not errors, errors)
    pg.set_viewport_size({"width": 800, "height": 900}); pg.wait_for_timeout(300)
    check("diperkecil ke tablet 800px: 6 foto per halaman (3 halaman dibuka = 18)", pg.evaluate(VIS, ".shot") == 18, pg.evaluate(VIS, ".shot"))
    ctx.close()

    for w in [375, 320]:
        ctx, pg, errors = open_page({"width": w, "height": 760}, mode="many")
        pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(400); scroll(pg)
        g = pg.evaluate(VIS, ".shot"); t = pg.evaluate(VIS, ".bubbles > .bubble")
        check(f"HP {w}px: galeri 6, testimoni 4 dulu", g == 6 and t == 4, (g, t))
        lg = pg.evaluate(SHOT, "Panjang")
        check(f"HP {w}px: screenshot panjang dipotong maks 360px", lg["tall"] and lg["clip"] <= 360, lg)
        sw = pg.evaluate("document.documentElement.scrollWidth"); cw = pg.evaluate("document.documentElement.clientWidth")
        check(f"HP {w}px: tidak ada scroll horizontal", sw <= cw, f"{sw}/{cw}")
        check(f"HP {w}px: tidak ada error JS", not errors, errors)
        if w == 375:
            pg.locator("#portofolio").screenshot(path=f"{OUT}/banyak-galeri-hp.png")
            pg.locator("#testimoni").screenshot(path=f"{OUT}/banyak-testi-hp.png")
        ctx.close()

    # 8. Isi bawaan (tanpa sheet): 5 testimoni teks -> HP 4 + tombol, laptop 5 tanpa tombol
    for w, exp, btn in [(1366, 5, False), (375, 4, True)]:
        ctx, pg, errors = open_page({"width": w, "height": 800}, config=False)
        pg.goto(URL, wait_until="networkidle")
        t = pg.evaluate(VIS, ".bubbles > .bubble"); b2 = pg.evaluate(BTN, "testi-load")["shown"]; gb = pg.evaluate(BTN, "gallery-load")["shown"]
        check(f"isi bawaan {w}px: testimoni {exp}, tombol galeri tersembunyi", t == exp and b2 == btn and not gb, (t, b2, gb))
        ctx.close()
    b.close()

bad = [r for r in results if not r[1]]
for n, ok, i in results: print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {i}"))
print(f"\n{len(results)-len(bad)}/{len(results)} lulus")
sys.exit(1 if bad else 0)
