"""Uji fungsional + screenshot draf website Natasya Makeup."""
import sys, threading, http.server, functools, urllib.parse
from playwright.sync_api import sync_playwright
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parent; OUT = HERE / "output"; OUT.mkdir(exist_ok=True)

root = sys.argv[1] if len(sys.argv) > 1 else str(REPO); outdir = sys.argv[2] if len(sys.argv) > 2 else str(OUT)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
handler = functools.partial(Quiet, directory=root)
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:8765/index.html"
results = []
def check(name, cond, info=""):
    results.append((name, bool(cond), info))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for label, vp in [("desktop", {"width": 1366, "height": 860}), ("mobile", {"width": 375, "height": 760})]:
        ctx = b.new_context(viewport=vp, reduced_motion="reduce")
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append(m.text + " @ " + str(m.location.get("url"))) if m.type == "error" and "fonts.g" not in str(m.location.get("url")) and "docs.google.com" not in str(m.location.get("url")) else None)
        def _js(route):
            body = route.fetch().text().replace('waNumber: "6285171502605"', 'waNumber: "6281200000001"')
            import re as _re
            body = _re.sub(r'logUrl: "[^"]*"', 'logUrl: ""', body)  # jangan kirim data tes ke spreadsheet asli
            route.fulfill(body=body, content_type="application/javascript")
        pg.route("**/assets/js/main.js", _js)  # nomor tiruan, jangan pernah ke WA Natasya
        ctx.route("https://wa.me/**", lambda r: r.abort())
        ctx.route("https://script.google.com/**", lambda r: r.abort())
        ctx.route("https://api.whatsapp.com/**", lambda r: r.abort())
        pg.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        pg.route("https://fonts.gstatic.com/**", lambda r: r.abort())
        pg.goto(URL, wait_until="networkidle")
        sw = pg.evaluate("document.documentElement.scrollWidth"); cw = pg.evaluate("document.documentElement.clientWidth")
        check(f"{label}: tidak ada scroll horizontal", sw <= cw, f"{sw} vs {cw}")
        pg.evaluate("(async()=>{for(let y=0;y<document.body.scrollHeight;y+=500){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}window.scrollTo(0,0);})()")
        pg.wait_for_timeout(800)
        broken = pg.evaluate("[...document.images].filter(i=>!i.closest('[hidden]')).filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)")
        check(f"{label}: semua gambar termuat", not broken, broken)
        pg.screenshot(path=f"{outdir}/{label}-full.png", full_page=True)

        if label == "desktop":
            # Pilih look
            pg.click(".pan[data-look='bridesmaid']")
            vis = pg.evaluate("[...document.querySelectorAll('.look-detail')].filter(d=>!d.hidden).map(d=>d.dataset.look)")
            check("pilih pan Bridesmaid menampilkan detail Bridesmaid saja", vis == ["bridesmaid"], vis)
            ph = pg.evaluate("(()=>{const i=document.querySelector('.look-detail[data-look=bridesmaid] .look-photo img');return [i.getAttribute('src'), i.getBoundingClientRect().height]})()")
            check("pilih Bridesmaid: panel foto tampil (kotak putih sebelum diisi sheet)", ph[0].startswith("data:image/gif") and ph[1] > 0, ph)
            pans = pg.evaluate("[...document.querySelectorAll('.pan')].map(p=>p.dataset.look)")
            check("Pilih look hanya 4: Wisuda, Lamaran, Akad, Bridesmaid", pans == ["wisuda","lamaran","akad","bridesmaid"] and pg.evaluate("document.querySelectorAll('.look-detail').length") == 4, pans)
            opts = pg.evaluate("[...document.querySelectorAll('#f-look option')].map(o=>o.value).filter(Boolean)")
            check("form booking: pilihan jenis makeup hanya 4", opts == ["wisuda","lamaran","akad","bridesmaid"], opts)
            txt = pg.evaluate("document.body.innerText + ' ' + document.querySelector('meta[name=description]').content + ' ' + document.querySelector('meta[property=\"og:description\"]').content + ' ' + (document.querySelector('script[type=\"application/ld+json\"]')?.textContent||'')").lower()
            gone = [w for w in ["photoshoot", "fantasi", "reguler", "regular", "tari,", "tari "] if w in txt]
            check("layanan yang dihapus tidak disebut lagi (teks, meta, data Google)", not gone, gone)
            for lk in ["wisuda","lamaran","akad","bridesmaid"]:
                pg.click(f".pan[data-look='{lk}']"); pg.wait_for_timeout(80)
            ok = pg.evaluate("[...document.querySelectorAll('.look-photo img')].map(i=>[i.closest('.look-detail').dataset.look, i.complete])")
            check("semua 4 foto look termuat saat dipilih", all(x[1] for x in ok), ok)
            pg.click(".pan[data-look='bridesmaid']"); pg.wait_for_timeout(200)
            check("aria-pressed pindah ke Bridesmaid", pg.get_attribute(".pan[data-look='bridesmaid']", "aria-pressed") == "true")
            pg.click(".look-detail[data-look='bridesmaid'] [data-book]")
            check("tombol booking look mengisi select", pg.input_value("#f-look") == "bridesmaid")
            check("portofolio tanpa kategori: tidak ada tombol filter, 6 kotak foto tampil", pg.evaluate("document.querySelectorAll('.chip,.filters,[data-filter]').length") == 0 and pg.evaluate("[...document.querySelectorAll('.shot')].filter(s=>!s.hidden).length") == 6)
            # Validasi form kosong
            pg.fill("#f-nama", ""); pg.select_option("#f-look", "")
            popup = []
            ctx.on("page", lambda np: popup.append(np))
            pg.click("#wa-send")
            pg.wait_for_timeout(400)
            errs = pg.evaluate("[...document.querySelectorAll('.field-error')].filter(e=>!e.hidden).map(e=>e.id)")
            check("form kosong: muncul pesan error (termasuk 'tahu dari mana')", set(errs) >= {"e-nama", "e-look", "e-tanggal", "e-lokasi", "e-sumber"}, errs)
            check("form kosong: WA tidak terbuka", len(popup) == 0)
            check("form kosong: fokus ke field pertama yang salah", pg.evaluate("document.activeElement.id") == "f-nama")
            # Tanggal lampau ditolak
            pg.fill("#f-nama", "Rina"); pg.select_option("#f-look", "wisuda")
            pg.fill("#f-tanggal", "2020-01-01"); pg.select_option("#f-kota", "Depok"); pg.select_option("#f-kecamatan", "Cimanggis")
            pg.click("#wa-send"); pg.wait_for_timeout(300)
            check("tanggal lampau ditolak", not pg.is_hidden("#e-tanggal") and len(popup) == 0)
            # Form valid
            pg.fill("#f-tanggal", "2027-03-20"); pg.fill("#f-jam", "07:30")
            pg.fill("#f-jumlah", "3"); pg.fill("#f-catatan", "Hijab, baju lilac")
            pg.click("#wa-send"); pg.wait_for_timeout(300)
            check("'Tahu dari mana' belum dipilih: ditolak, fokus ke dropdown", not pg.is_hidden("#e-sumber") and len(popup) == 0 and pg.evaluate("document.activeElement.id") == "f-sumber")
            opts = pg.evaluate("[...document.querySelectorAll('#f-sumber option')].map(o=>o.textContent)")
            check("opsi 'Tahu dari mana' lengkap & urut", opts == ["Pilih salah satu", "WhatsApp", "Instagram", "TikTok", "Google", "Iklan", "Dari teman", "Lainnya"], opts)
            order = pg.evaluate("[...document.querySelectorAll('#booking-form .field label')].map(l=>l.htmlFor)")
            check("pertanyaan ada tepat sebelum Catatan", order.index("f-sumber") == order.index("f-catatan") - 1, order)
            pg.select_option("#f-sumber", "instagram")
            check("error 'tahu dari mana' hilang setelah dipilih", pg.is_hidden("#e-sumber"))
            href = pg.get_attribute("#wa-send", "href")
            q = urllib.parse.urlparse(href)
            text = urllib.parse.parse_qs(q.query)["text"][0]
            check("link WA ke nomor benar", q.netloc == "wa.me" and q.path == "/6281200000001", href[:40])
            check("pesan WA berisi semua data", all(s in text for s in ["Rina", "Wisuda", "Sabtu, 20 Maret 2027", "07.30" if "07.30" in text else "07:30", "Cimanggis, Depok", "Jumlah orang: 3", "Tahu Natasya Makeup dari: Instagram", "Hijab, baju lilac"]), text)
            results.append(("contoh pesan WA", True, "\n" + text))
            pg.click("#wa-send"); pg.wait_for_timeout(800)
            check("form valid: WA terbuka di tab baru", len(popup) == 1, [pp.url[:60] for pp in popup])
            errs = pg.evaluate("[...document.querySelectorAll('.field-error')].filter(e=>!e.hidden).length")
            check("form valid: tidak ada error tersisa", errs == 0)
            # Reset form
            pg.fill("#f-nama", "Rina"); pg.select_option("#f-kota", "Jakarta Timur"); pg.select_option("#f-kecamatan", "Ciracas"); pg.fill("#f-jumlah", "4")
            pg.click("#wa-send", modifiers=[]) if False else None
            pg.fill("#f-nama", ""); pg.click("#wa-send"); pg.wait_for_timeout(300)
            check("sebelum reset: ada error nama", not pg.is_hidden("#e-nama"))
            pg.click("#form-reset"); pg.wait_for_timeout(200)
            vals = pg.evaluate("['f-nama','f-look','f-tanggal','f-jam','f-kota','f-kecamatan','f-lokasi-lain','f-sumber','f-catatan'].map(id=>document.getElementById(id).value)")
            check("reset: semua field kosong", all(v == "" for v in vals), vals)
            check("reset: kecamatan kembali terkunci, kolom 'kota lain' tersembunyi", pg.evaluate("document.getElementById('f-kecamatan').disabled && document.getElementById('f-lokasi-lain').hidden"))
            check("reset: jumlah kembali ke 1", pg.input_value("#f-jumlah") == "1")
            check("reset: semua error hilang", pg.evaluate("[...document.querySelectorAll('.field-error')].every(e=>e.hidden) && ![...document.querySelectorAll('[aria-invalid=true]')].length"))
            check("reset: fokus ke field nama", pg.evaluate("document.activeElement.id") == "f-nama")
            check("reset: status dibacakan", pg.text_content("#form-status") == "Form sudah dikosongkan.")
            check("reset: link WA ikut kosong", "Nama%3A%20%0A" in pg.get_attribute("#wa-send", "href") or "Nama%3A%20%0AJenis" in pg.get_attribute("#wa-send", "href"), pg.get_attribute("#wa-send", "href")[:120])
            check("reset: WA tidak terbuka", len(popup) == 1)
            check("tidak ada sisa placeholder todo di halaman", pg.evaluate("!document.querySelector('mark.todo') && !/isi harga|\\bisi\\b,/i.test(document.body.innerText)"))
            pg.locator("#looks").screenshot(path=f"{outdir}/desktop-looks.png")
        else:
            # Bar booking muncul setelah lewat hero, hilang di section booking
            check("mobile: bar booking tersembunyi di hero", "is-visible" not in (pg.get_attribute("#booking-bar", "class") or ""))
            pg.evaluate("window.scrollTo(0, document.getElementById('portofolio').offsetTop)"); pg.wait_for_timeout(400)
            check("mobile: bar booking muncul setelah hero", "is-visible" in pg.get_attribute("#booking-bar", "class"))
            pg.evaluate("window.scrollTo(0, document.getElementById('booking').offsetTop + 200)"); pg.wait_for_timeout(400)
            check("mobile: bar booking hilang di section booking", "is-visible" not in pg.get_attribute("#booking-bar", "class"))
            pg.evaluate("window.scrollTo(0,0)")
            pg.screenshot(path=f"{outdir}/mobile-hero.png")
        hrefs = pg.evaluate("[...document.querySelectorAll('a[href*=\"wa.me\"]')].map(a=>a.href)")
        check(f"{label}: semua link WA ke nomor tiruan (4 link, termasuk tombol melayang)", len(hrefs) == 4 and all("/6281200000001" in h for h in hrefs), hrefs)
        check(f"{label}: tidak ada link ke nomor Natasya", not any("85171502605" in h for h in hrefs))
        disp = pg.evaluate("[...document.querySelectorAll('[data-wa-display]')].map(e=>e.textContent)")
        check(f"{label}: teks nomor tampil 0812-0000-0001", disp == ["0812-0000-0001"] * 2, disp)
        ld = pg.evaluate("JSON.parse(document.querySelector('script[type=\"application/ld+json\"]').textContent).telephone")
        check(f"{label}: JSON-LD telephone ikut CONFIG", ld == "+6281200000001", ld)
        check(f"{label}: tidak ada error JS", not errors, errors)
        ctx.close()
    b.close()
httpd.shutdown()
for name, ok, info in results:
    print(("PASS " if ok else "FAIL ") + name + (f"  -> {info}" if (info and (not ok or name.startswith('contoh'))) else ""))
