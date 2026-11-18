"""Form booking: lokasi kota + kecamatan sebaris, 'Kota lain', validasi, pesan WA & data log.
Nomor WA tiruan, WhatsApp & Apps Script asli diblokir, log dikirim ke server tiruan."""
import sys, json, threading, http.server, functools, re, urllib.parse
from playwright.sync_api import sync_playwright
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parent; OUT = HERE / "output"; OUT.mkdir(exist_ok=True)
root = sys.argv[1] if len(sys.argv) > 1 else str(REPO)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
site = http.server.ThreadingHTTPServer(("127.0.0.1", 8795), functools.partial(Q, directory=root))
threading.Thread(target=site.serve_forever, daemon=True).start()
got = []
class Log(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); got.append(json.loads(self.rfile.read(n).decode()))
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
logsrv = http.server.ThreadingHTTPServer(("127.0.0.1", 8796), Log)
threading.Thread(target=logsrv.serve_forever, daemon=True).start()
res = []
def check(n, c, i=""): res.append((n, bool(c), i))
EXPECT = {"Depok": 11, "Jakarta Timur": 10, "Jakarta Selatan": 10, "Jakarta Pusat": 8, "Jakarta Barat": 8, "Jakarta Utara": 6,
          "Kota Bogor": 6, "Kab. Bogor": 40, "Kota Bekasi": 12, "Kab. Bekasi": 23, "Tangerang Selatan": 7, "Kota Tangerang": 13, "Kab. Tangerang": 29}
def page(b, vp=(1366, 860)):
    ctx = b.new_context(viewport={"width": vp[0], "height": vp[1]}, reduced_motion="reduce"); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    def js(route):
        body = route.fetch().text().replace('waNumber: "6285171502605"', 'waNumber: "6281200000001"')
        body = re.sub(r'logUrl: "[^"]*"', 'logUrl: "http://127.0.0.1:8796/exec"', body)
        route.fulfill(body=body, content_type="application/javascript")
    pg.route("**/assets/js/main.js", js)
    for pat in ["https://wa.me/**", "https://api.whatsapp.com/**", "https://script.google.com/**"]: ctx.route(pat, lambda r: r.abort())
    for pat in ["https://docs.google.com/**", "https://fonts.g*/**", "https://drive.google.com/**"]: pg.route(pat, lambda r: r.abort())
    pg.goto("http://127.0.0.1:8795/index.html", wait_until="networkidle")
    pops = []; ctx.on("page", lambda p: pops.append(p))
    return ctx, pg, errs, pops
def fill_rest(pg):
    pg.fill("#f-nama", "Rina"); pg.select_option("#f-look", "wisuda"); pg.fill("#f-tanggal", "2027-03-20")
    pg.fill("#f-jumlah", "2"); pg.select_option("#f-sumber", "instagram")
def wa_text(pg):
    return urllib.parse.parse_qs(urllib.parse.urlparse(pg.get_attribute("#wa-send", "href")).query)["text"][0]
def visible_err(pg): return pg.evaluate("[...document.querySelectorAll('.field-error')].filter(e=>!e.hidden).map(e=>e.id)")
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg, errs, pops = page(b)
    pg.locator("#booking").scroll_into_view_if_needed()
    kota = pg.evaluate("[...document.querySelectorAll('#f-kota option')].map(o=>[o.value,o.textContent])")
    check("pilihan kota: placeholder, 13 kota Jabodetabek (Depok paling atas), lalu 'Kota lain'",
          kota[0] == ["", "Pilih kota"] and [k for _, k in kota[1:-1]] == list(EXPECT) and kota[-1] == ["lain", "Kota lain"], kota)
    st = pg.evaluate("(()=>{const k=document.getElementById('f-kecamatan');return [k.disabled,k.options.length,k.options[0].textContent,document.getElementById('f-lokasi-lain').hidden]})()")
    check("awal: kecamatan terkunci bertuliskan 'Kecamatan', kolom ketik tersembunyi", st == [True, 1, "Kecamatan", True], st)
    counts = {}
    for k in EXPECT:
        pg.select_option("#f-kota", k)
        opts = pg.evaluate("[...document.querySelectorAll('#f-kecamatan option')].map(o=>o.value)")
        counts[k] = (len(opts) - 1, opts[0] == "", len(set(opts[1:])) == len(opts) - 1, opts[1:] == sorted(opts[1:]))
    check("jumlah kecamatan per kota sesuai sumber resmi, urut abjad, tanpa dobel (total 183)",
          all(counts[k] == (EXPECT[k], True, True, True) for k in EXPECT), counts)
    pg.select_option("#f-kota", "Depok")
    has = pg.evaluate("[...document.querySelectorAll('#f-kecamatan option')].map(o=>o.value)")
    check("Depok berisi Cimanggis & Tapos", "Cimanggis" in has and "Tapos" in has)
    pg.select_option("#f-kecamatan", "Cimanggis"); pg.select_option("#f-kota", "Jakarta Timur")
    check("ganti kota: kecamatan dikosongkan & daftarnya ikut berganti", pg.input_value("#f-kecamatan") == "" and pg.evaluate("[...document.querySelectorAll('#f-kecamatan option')].some(o=>o.value==='Ciracas')"))
    # validasi: kota dipilih, kecamatan belum
    fill_rest(pg); pg.click("#wa-send"); pg.wait_for_timeout(300)
    check("kecamatan belum dipilih: error lokasi, fokus ke kecamatan, WA tidak terbuka",
          visible_err(pg) == ["e-lokasi"] and pg.evaluate("document.activeElement.id") == "f-kecamatan"
          and pg.get_attribute("#f-kecamatan", "aria-invalid") == "true" and len(pops) == 0, visible_err(pg))
    pg.select_option("#f-kecamatan", "Ciracas"); pg.wait_for_timeout(100)
    check("error lokasi hilang begitu kecamatan dipilih", pg.is_hidden("#e-lokasi") and pg.get_attribute("#f-kecamatan", "aria-invalid") != "true")
    check("pesan WA: 'Lokasi: Ciracas, Jakarta Timur'", "Lokasi: Ciracas, Jakarta Timur" in wa_text(pg), wa_text(pg))
    pg.click("#wa-send"); pg.wait_for_timeout(800)
    check("form valid: WA terbuka (nomor tiruan) & data log berisi 'Ciracas, Jakarta Timur'",
          len(pops) == 1 and got and got[-1]["lokasi"] == "Ciracas, Jakarta Timur", got[-1] if got else None)
    # kota kosong -> fokus ke kota
    pg.select_option("#f-kota", ""); pg.click("#wa-send"); pg.wait_for_timeout(300)
    check("kota belum dipilih: error lokasi, fokus ke kota", not pg.is_hidden("#e-lokasi") and pg.evaluate("document.activeElement.id") == "f-kota" and pg.get_attribute("#f-kota", "aria-invalid") == "true")
    # kota lain
    pg.select_option("#f-kota", "lain"); pg.wait_for_timeout(100)
    st = pg.evaluate("(()=>{const k=document.getElementById('f-kecamatan'),t=document.getElementById('f-lokasi-lain');return [k.hidden,t.hidden,document.activeElement.id]})()")
    check("'Kota lain': kotak kecamatan diganti kolom ketik & langsung difokus", st == [True, False, "f-lokasi-lain"], st)
    pg.click("#wa-send"); pg.wait_for_timeout(300)
    check("'Kota lain' kosong: error, fokus ke kolom ketik", not pg.is_hidden("#e-lokasi") and pg.evaluate("document.activeElement.id") == "f-lokasi-lain")
    pg.fill("#f-lokasi-lain", "  Karawaci, Karawang  ")
    pg.fill("#f-lokasi-lain", "Telukjambe, Karawang"); pg.wait_for_timeout(100)
    check("error hilang setelah diketik; pesan WA pakai teks ketikan", pg.is_hidden("#e-lokasi") and "Lokasi: Telukjambe, Karawang" in wa_text(pg), wa_text(pg))
    n = len(got); pg.click("#wa-send"); pg.wait_for_timeout(800)
    check("'Kota lain' terkirim ke log apa adanya", len(got) > n and got[-1]["lokasi"] == "Telukjambe, Karawang", got[-1] if got else None)
    pg.press("#f-lokasi-lain", "Enter"); pg.wait_for_timeout(500)
    check("Enter di kolom ketik = kirim", len(pops) >= 3, len(pops))
    pg.select_option("#f-kota", "Depok")
    check("kembali pilih kota dari daftar: kolom ketik disembunyikan & dikosongkan", pg.evaluate("document.getElementById('f-lokasi-lain').hidden && document.getElementById('f-lokasi-lain').value===''"))
    pg.click("#form-reset"); pg.wait_for_timeout(200)
    st = pg.evaluate("(()=>{const k=document.getElementById('f-kecamatan');return [document.getElementById('f-kota').value,k.value,k.disabled,k.options[0].textContent,document.getElementById('f-lokasi-lain').hidden]})()")
    check("reset: kota kosong, kecamatan terkunci lagi", st == ["", "", True, "Kecamatan", True], st)
    lab = pg.evaluate("(()=>{const g=document.querySelector('.field-pair');return [g.getAttribute('role'),document.getElementById(g.getAttribute('aria-labelledby')).textContent,document.getElementById('f-kota').getAttribute('aria-label'),document.getElementById('f-kecamatan').getAttribute('aria-label')]})()")
    check("aksesibilitas: grup berlabel 'Lokasi makeup', dropdown berlabel Kota & Kecamatan", lab == ["group", "Lokasi makeup", "Kota", "Kecamatan"], lab)
    check("tidak ada error JavaScript", not errs, errs)
    ctx.close()
    # tata letak: selalu sebaris, tidak meluber
    for w in [320, 360, 390, 768, 1024, 1366]:
        ctx, pg, errs, pops = page(b, (w, 800))
        for mode in ["Kab. Tangerang", "lain"]:
            pg.select_option("#f-kota", mode)
            if mode != "lain": pg.select_option("#f-kecamatan", "Sepatan Timur")
            r = pg.evaluate("""(()=>{const a=document.getElementById('f-kota').getBoundingClientRect();
              const bEl=document.getElementById(document.getElementById('f-kota').value==='lain'?'f-lokasi-lain':'f-kecamatan');const c=bEl.getBoundingClientRect();
              const pair=document.querySelector('.field-pair').getBoundingClientRect();
              return {sameRow: Math.abs(a.top-c.top)<1, aw: Math.round(a.width), bw: Math.round(c.width), inside: c.right<=pair.right+0.5,
                      overflow: document.documentElement.scrollWidth>innerWidth, h: Math.round(a.height)}})()""")
            fs = pg.evaluate("[getComputedStyle(document.getElementById('f-kota')).fontSize, getComputedStyle(document.getElementById('f-kecamatan')).fontSize, getComputedStyle(document.getElementById('f-lokasi-lain')).fontSize]")
            check(f"{w}px: font dropdown/kolom lokasi 16px (iPhone tidak zoom otomatis)", fs == ["16px"] * 3, fs)
            line = pg.evaluate("(()=>{const e=document.getElementById('lokasi-lengkap');return [getComputedStyle(e).display, e.textContent]})()")
            if mode != "lain":
                want = "block" if w <= 420 else "none"
                check(f"{w}px: baris 'Lokasi: Sepatan Timur, Kab. Tangerang' {'tampil' if w <= 420 else 'disembunyikan'}", line == [want, "Lokasi: Sepatan Timur, Kab. Tangerang"], line)
            else:
                check(f"{w}px: 'Kota lain' tidak memunculkan baris lokasi", line[1] == "", line)
            check(f"{w}px ({'kota lain' if mode=='lain' else 'kota+kecamatan'}): sebaris, lebar sama, tidak meluber",
                  r["sameRow"] and abs(r["aw"] - r["bw"]) <= 1 and r["inside"] and not r["overflow"] and r["aw"] >= 110 and r["h"] >= 44, r)
        ctx.close()
    b.close()
bad = [r for r in res if not r[1]]
for n, ok, i in res: print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {i}"))
print(f"\n{len(res)-len(bad)}/{len(res)} lulus"); sys.exit(1 if bad else 0)
