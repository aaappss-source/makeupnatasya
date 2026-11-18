"""Tes tombol WhatsApp melayang. Pakai nomor dummy; semua request ke wa.me diblok."""
import re, sys, http.server, threading, functools
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parent; OUT = HERE / "output"; OUT.mkdir(exist_ok=True)

ROOT = sys.argv[1] if len(sys.argv) > 1 else str(REPO)
DUMMY = "6281200000001"
EXPECTED = ("Halo Kak Natasya, aku mau tanya-tanya dulu soal makeup ya 😊\n\n"
            "Nama: \n\n"
            "Jenis makeup (wisuda/lamaran/akad/bridesmaid): \n\n"
            "Tanggal acara: \n\n"
            "Makeup harus selesai jam: \n\n"
            "Jumlah orang: \n\n"
            "Lokasi makeup (boleh langsung kirim share location): \n\n"
            "Tahu Natasya dari (Instagram/TikTok/Google/teman/lainnya): ")

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8790), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()

results = []
def check(name, ok, info=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {info}"))

def overlap(a, b):
    return a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"] and a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"]

RECT = "(s) => { const r = document.querySelector(s).getBoundingClientRect(); return {x:r.x, y:r.y, width:r.width, height:r.height}; }"
wa_requests, errors = [], []

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, vh in [(360, 740), (390, 844), (768, 1024), (1024, 768), (1366, 768), (1920, 1080)]:
        ctx = b.new_context(viewport={"width": vw, "height": vh}, reduced_motion="reduce")
        ctx.route("https://wa.me/**", lambda r: (wa_requests.append(r.request.url), r.abort()))
        ctx.route("https://api.whatsapp.com/**", lambda r: (wa_requests.append(r.request.url), r.abort()))
        for pat in ["https://script.google.com/**", "https://docs.google.com/**", "https://drive.google.com/**", "https://fonts.g*/**"]:
            ctx.route(pat, lambda r: r.abort())
        ctx.route("**/assets/js/main.js", lambda r: r.fulfill(
            body=re.sub(r'logUrl: "[^"]*"', 'logUrl: ""', r.fetch().text()).replace('waNumber: "6285171502605"', f'waNumber: "{DUMMY}"'),
            content_type="application/javascript"))
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("http://127.0.0.1:8790/index.html", wait_until="networkidle")
        pg.add_style_tag(content="html{scroll-behavior:auto!important}")
        tag = f"{vw}px:"
        mobile = vw <= 760

        f0 = pg.evaluate(RECT, "#wa-float")
        st = pg.evaluate("() => { const s = getComputedStyle(document.getElementById('wa-float')); return [s.position, s.visibility, s.opacity, s.zIndex]; }")
        check(f"{tag} tombol tampil, position fixed", st[0] == "fixed" and st[1] == "visible" and st[2] == "1", st)
        check(f"{tag} ukuran tombol minimal 44px (mudah dipencet)", f0["width"] >= 44 and f0["height"] >= 44, f0)
        check(f"{tag} posisinya di kanan bawah", vw - (f0["x"] + f0["width"]) <= 45 and vh - (f0["y"] + f0["height"]) <= 40, f0)

        href = pg.get_attribute("#wa-float", "href")
        u = urlparse(href); text = parse_qs(u.query).get("text", [""])[0]
        check(f"{tag} link ke nomor dummy, bukan nomor asli", u.netloc == "wa.me" and u.path == f"/{DUMMY}", href)
        check(f"{tag} draf pesan persis sesuai rancangan", text == EXPECTED, repr(text))
        check(f"{tag} buka di tab baru (target _blank, rel noopener)",
              pg.get_attribute("#wa-float", "target") == "_blank" and "noopener" in (pg.get_attribute("#wa-float", "rel") or ""))
        check(f"{tag} punya nama untuk pembaca layar", pg.get_attribute("#wa-float", "aria-label") == "Chat WhatsApp Natasya")

        # Tetap di tempat saat scroll (dicek di beberapa titik halaman)
        moved = []
        for sel in ["#looks", "#portofolio", "#booking", ".site-footer"]:
            pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'start'}})"); pg.wait_for_timeout(350)
            r = pg.evaluate(RECT, "#wa-float")
            if abs(r["x"] - f0["x"]) > 0.5 or abs(r["y"] - f0["y"]) > 0.5: moved.append((sel, r))
        check(f"{tag} posisi tidak berubah saat discroll", not moved, moved)

        # Tidak menutupi header
        hdr = pg.evaluate(RECT, ".site-header")
        check(f"{tag} tidak menutupi header", not overlap(f0, hdr))

        # Akhir halaman: tidak ada teks/link footer yang tertutup
        pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)"); pg.wait_for_timeout(300)
        fr = pg.evaluate(RECT, "#wa-float")
        covered = pg.evaluate("""(f) => [...document.querySelectorAll('.site-footer p, .site-footer a, .site-footer img')].filter(el => {
            const r = el.getBoundingClientRect(); if (!r.width) return false;
            return r.left < f.x + f.width && f.x < r.right && r.top < f.y + f.height && f.y < r.bottom; }).map(el => el.textContent.trim().slice(0, 40) || el.tagName)""", fr)
        check(f"{tag} di akhir halaman tidak ada isi footer yang tertutup", not covered, covered)

        if mobile:
            # Bar booking tampil di tengah halaman: tombol WA di ujung kanan bar, tidak menumpuk
            pg.evaluate("document.querySelector('#portofolio').scrollIntoView({block:'start'})"); pg.wait_for_timeout(400)
            bar_on = pg.evaluate("document.getElementById('booking-bar').classList.contains('is-visible')")
            btn = pg.evaluate(RECT, "#booking-bar .btn"); bar = pg.evaluate(RECT, "#booking-bar"); fr = pg.evaluate(RECT, "#wa-float")
            check(f"{tag} bar booking tampil saat di tengah halaman", bar_on)
            check(f"{tag} tombol WA tidak menutupi tombol Booking jadwal makeup", not overlap(fr, btn) and btn["x"] + btn["width"] <= fr["x"] - 6, (btn, fr))
            check(f"{tag} tombol WA sejajar di dalam bar", fr["y"] >= bar["y"] and fr["y"] + fr["height"] <= bar["y"] + bar["height"], (bar, fr))
            check(f"{tag} tombol Booking tetap lebar (>= 60% layar)", btn["width"] >= 0.6 * vw, btn["width"])
            # Saat mengetik di form, tombol disembunyikan
            pg.evaluate("document.querySelector('#booking').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300)
            pg.focus("#f-nama"); pg.wait_for_timeout(250)
            hid = pg.evaluate("getComputedStyle(document.getElementById('wa-float')).visibility")
            pg.focus("#f-look"); pg.wait_for_timeout(250)
            hid2 = pg.evaluate("getComputedStyle(document.getElementById('wa-float')).visibility")
            pg.evaluate("document.activeElement.blur()"); pg.wait_for_timeout(250)
            back = pg.evaluate("getComputedStyle(document.getElementById('wa-float')).visibility")
            check(f"{tag} disembunyikan selama kolom form diisi, muncul lagi setelahnya", hid == "hidden" and hid2 == "hidden" and back == "visible", (hid, hid2, back))
        else:
            if vw >= 1280:
                cont = pg.evaluate("(() => { const c = document.querySelector('main .container'); const s = getComputedStyle(c); const r = c.getBoundingClientRect(); return r.right - parseFloat(s.paddingRight); })()")
                check(f"{tag} tombol berada di area kosong samping isi halaman", f0["x"] >= cont, (f0["x"], cont))
            # Fokus keyboard terlihat
            pg.evaluate("window.scrollTo(0,0)"); pg.focus("#wa-float")
            ol = pg.evaluate("getComputedStyle(document.activeElement).outlineStyle")
            check(f"{tag} fokus keyboard terlihat", pg.evaluate("document.activeElement.id") == "wa-float" and ol != "none", ol)

        # Klik: request menuju wa.me dummy (diblok, tidak terkirim)
        before = len(wa_requests)
        pg.evaluate("window.scrollTo(0, 400)"); pg.wait_for_timeout(200)
        try:
            with ctx.expect_page(timeout=4000) as newp:
                pg.click("#wa-float")
            newp.value.wait_for_timeout(500)
        except Exception as e:
            pass
        got = wa_requests[before:]
        check(f"{tag} dipencet membuka chat WA (ke nomor dummy)", bool(got) and all(f"/{DUMMY}" in x for x in got), got[:2])
        ctx.close()
    b.close()

check("tidak ada request ke nomor WA asli", all("6285171502605" not in x for x in wa_requests), [x for x in wa_requests if "6285171502605" in x][:2])
check("tidak ada error JavaScript", not errors, errors[:3])
print(f"\n{sum(results)}/{len(results)} lulus")
