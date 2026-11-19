"""Cek isi website sesuai 4 brosur Natasya + penanda kuning. Nomor WA diganti tiruan, WhatsApp diblokir."""
import sys, re, threading, http.server, functools
from playwright.sync_api import sync_playwright
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parent; OUT = HERE / "output"; OUT.mkdir(exist_ok=True)
root = sys.argv[1] if len(sys.argv) > 1 else str(REPO)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8781), functools.partial(Q, directory=root))
threading.Thread(target=srv.serve_forever, daemon=True).start()
res = []
def check(n, c, i=""): res.append((n, bool(c), i))
js = open(f"{root}/assets/js/main.js").read()
check("CONFIG: nomor WA Natasya 6285171502605 (dari brosur)", 'waNumber: "6285171502605"' in js)
html = open(f"{root}/index.html").read()
for old in ["DP 50%", "termasuk transport untuk wilayah Depok", "hairdo simpel", "Rp1.200.000</dd>\n                  <div><dt>Sudah termasuk</dt><dd>Makeup pengantin"]:
    check(f"info lama yang bertentangan dengan brosur sudah diganti: {old[:40]!r}", old not in html)
YELLOW = "rgb(229, 176, 0)"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for w in [1366, 375]:
        ctx = b.new_context(viewport={"width": w, "height": 900}); pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        def _js(route):
            route.fulfill(body=route.fetch().text().replace('waNumber: "6285171502605"', 'waNumber: "6281200000001"'), content_type="application/javascript")
        pg.route("**/assets/js/main.js", _js)
        ctx.route("https://wa.me/**", lambda r: r.abort()); pg.route("https://fonts.g*/**", lambda r: r.abort()); pg.route("https://docs.google.com/**", lambda r: r.abort()); ctx.route("https://script.google.com/**", lambda r: r.abort())
        pg.goto(f"http://127.0.0.1:8781/index.html", wait_until="networkidle")
        def look(name):
            pg.click(f".pan[data-look='{name}']"); pg.wait_for_timeout(200)
            return pg.evaluate("""(n)=>{const a=document.querySelector(`.look-detail[data-look=${n}]`);return {
              txt:a.innerText, dd:[...a.querySelectorAll('dd')].map(d=>[d.innerText,getComputedStyle(d).color]),
              h3:getComputedStyle(a.querySelector('h3')).color}}""", name)
        W = look("wisuda")
        check(f"{w}px wisuda: Rp200.000, Rp380.000, toga, softlens Rp35.000, hairdo Rp150.000 (warna normal)",
              all(x in W["txt"] for x in ["Rp200.000", "Rp380.000", "pemasangan toga", "Softlens normal Rp35.000", "hairdo mulai Rp150.000", "transport sampai 5 km"])
              and all(c != YELLOW for _, c in W["dd"]), W["dd"])
        L = look("lamaran")
        check(f"{w}px lamaran: promo Rp250.000, softlens, body tone up", all(x in L["txt"] for x in ["Rp250.000", "Softlens", "body tone up", "Hairdo mulai Rp150.000"]) and all(c != YELLOW for _, c in L["dd"]), L["dd"])
        for n in ["bridesmaid"]:
            R = look(n)
            check(f"{w}px {n}: Rp175.000, 3+ Rp170.000, 5+ Rp165.000", all(x in R["txt"] for x in ["Rp175.000 per orang", "Rp170.000", "Rp165.000", "Bulu mata palsu, hijab do"]) and all(c != YELLOW for _, c in R["dd"]), R["dd"])
        check(f"{w}px teks baru: hero, wisuda, lamaran, akad segera hadir, domisili, FAQ hairdo Rp150.000",
              all(s in pg.evaluate("document.body.textContent") for s in ["Halo, aku Natasya!", "MUA yang berdomisili di Cimanggis, Depok. Aku percaya setiap perempuan punya pesona dan kecantikannya sendiri. Melalui makeup, aku ingin membantu kamu tampil lebih percaya diri, nyaman, dan bersinar di setiap momen spesial.", "Let's shine together, because you were born to be shining! ♡",
              "Sudah termasuk hijabdo dan pemasangan toga. Bisa untuk kamu yang berhijab maupun non-hijab.", "Tampil cantik dan percaya diri di hari spesialmu! Bebas request makeup sesuai look yang kamu inginkan.",
              "Natasya berdomisili di Cimanggis, Depok.", "Bisa! Hairdo ditangani oleh team hairstylist dengan harga mulai Rp150.000."])
              and "berbasis" not in pg.evaluate("document.body.textContent") and "Rp50.000" not in pg.evaluate("document.body.textContent")
              and pg.evaluate("document.querySelector('.look-detail[data-look=akad] .look-info').innerText.trim()") == "Segera hadir.")
        for n in ["akad"]:
            X = look(n)
            check(f"{w}px {n}: tidak ada tulisan kuning lagi", X["h3"] != YELLOW and all(c != YELLOW for _, c in X["dd"]), (X["h3"], X["dd"]))
        faq = pg.evaluate("[...document.querySelectorAll('.faq-list details')].map(d=>d.textContent)")
        ft = " ".join(faq)
        check(f"{w}px FAQ: S&K brosur (DP Rp30.000, H-1, 30 menit, stop kontak, keramas H-1, krim dokter)",
              all(x in ft for x in ["DP minimal Rp30.000", "H-1", "30 menit", "stop kontak", "jangan keramas H-1", "krim dokter", "15 sampai 30 menit"]), len(faq))
        yellow = pg.evaluate("[...document.querySelectorAll('body *')].filter(e=>getComputedStyle(e).color==='rgb(229, 176, 0)').length")
        check(f"{w}px: tidak ada tulisan kuning tersisa", yellow == 0, yellow)
        check(f"{w}px: tidak ada atribut data-draft tersisa", pg.evaluate("document.querySelectorAll('[data-draft]').length") == 0)
        body = pg.evaluate("document.body.textContent")
        gone = ["Riasan lembut yang tetap kelihatan di foto", "Klien paling sering bilang", "jarum pentul", "Reschedule bisa satu kali", "60 sampai 90 menit", "Berapa lama proses makeup"]
        check(f"{w}px: 5 kalimat yang diminta sudah terhapus", not [g for g in gone if g in body], [g for g in gone if g in body])
        keep = ["Banyak klien Natasya berhijab, dan hijab do juga termasuk di paket akad.",
                "Hallo calon client Natasya Makeup!", "DP tidak dikembalikan.", "Certified MUA sejak 2023", "born to be shining",
                "Lokasinya bisa di rumah, gedung, atau dekat kampus.", "Melayani Depok dan sekitar Jabodetabek."]
        check(f"{w}px: kalimat yang tidak diminta tetap ada", not [k for k in keep if k not in body], [k for k in keep if k not in body])
        check(f"{w}px: FAQ tinggal 8 pertanyaan", pg.evaluate("document.querySelectorAll('.faq-list details').length") == 8)
        check(f"{w}px: link WA pakai nomor tiruan saat tes", pg.evaluate("document.querySelector('[data-wa]').href").startswith("https://wa.me/6281200000001"))
        sw = pg.evaluate("document.documentElement.scrollWidth"); cw = pg.evaluate("document.documentElement.clientWidth")
        check(f"{w}px: tidak ada scroll horizontal", sw <= cw, (sw, cw))
        check(f"{w}px: tidak ada error JS", not errs, errs)
        if w == 1366:
            pg.click(".pan[data-look='wisuda']"); pg.locator("#looks").screenshot(path=f"{OUT}/brosur-wisuda.png")
            pg.click(".pan[data-look='akad']"); pg.locator(".compact").screenshot(path=f"{OUT}/brosur-akad.png")
            pg.locator(".hero").screenshot(path=f"{OUT}/brosur-hero.png")
            pg.evaluate("document.querySelectorAll('.faq-list details').forEach(d=>d.open=true)")
            pg.locator("#faq").screenshot(path=f"{OUT}/brosur-faq.png")
        else:
            pg.click(".pan[data-look='bridesmaid']"); pg.locator(".compact").screenshot(path=f"{OUT}/brosur-bridesmaid-hp.png")
        ctx.close()
    b.close()
bad = [r for r in res if not r[1]]
for n, ok, i in res: print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {i}"))
print(f"\n{len(res)-len(bad)}/{len(res)} lulus"); sys.exit(1 if bad else 0)
