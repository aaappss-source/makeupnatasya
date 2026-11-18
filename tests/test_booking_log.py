"""Form booking -> data terkirim ke Apps Script (server tiruan). Nomor WA tiruan, WhatsApp diblokir."""
import sys, json, threading, http.server, functools, subprocess, re
from playwright.sync_api import sync_playwright
from pathlib import Path
HERE = Path(__file__).resolve().parent; REPO = HERE.parent; OUT = HERE / "output"; OUT.mkdir(exist_ok=True)
root = sys.argv[1] if len(sys.argv) > 1 else str(REPO)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
site = http.server.ThreadingHTTPServer(("127.0.0.1", 8785), functools.partial(Q, directory=root))
threading.Thread(target=site.serve_forever, daemon=True).start()
got = []
class Log(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); got.append({"body": self.rfile.read(n).decode(), "ctype": self.headers.get("Content-Type")})
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
logsrv = http.server.ThreadingHTTPServer(("127.0.0.1", 8786), Log)
threading.Thread(target=logsrv.serve_forever, daemon=True).start()
LOG = "http://127.0.0.1:8786/exec"
res = []
def check(n, c, i=""): res.append((n, bool(c), i))
def page(b, url_on=True, vp=(1366, 860)):
    ctx = b.new_context(viewport={"width": vp[0], "height": vp[1]}, reduced_motion="reduce"); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    def js(route):
        body = route.fetch().text().replace('waNumber: "6285171502605"', 'waNumber: "6281200000001"')
        body = re.sub(r'logUrl: "[^"]*"', f'logUrl: "{LOG if url_on else ""}"', body)  # jangan ke Apps Script asli
        route.fulfill(body=body, content_type="application/javascript")
    pg.route("**/assets/js/main.js", js)
    for pat in ["https://wa.me/**", "https://api.whatsapp.com/**", "https://script.google.com/**"]: ctx.route(pat, lambda r: r.abort())
    for pat in ["https://docs.google.com/**", "https://fonts.g*/**"]: pg.route(pat, lambda r: r.abort())
    pg.goto("http://127.0.0.1:8785/index.html", wait_until="networkidle")
    pops = []; ctx.on("page", lambda p: pops.append(p))
    return ctx, pg, errs, pops
def fill(pg, nama="Rina", catatan="Hijab", sumber="instagram"):
    pg.fill("#f-nama", nama); pg.select_option("#f-look", "wisuda"); pg.fill("#f-tanggal", "2027-03-20")
    pg.fill("#f-jam", "07:30"); pg.select_option("#f-kota", "Depok"); pg.select_option("#f-kecamatan", "Cimanggis"); pg.fill("#f-jumlah", "3")
    if sumber: pg.select_option("#f-sumber", sumber)
    pg.fill("#f-catatan", catatan)
def wait(n, pg):
    for _ in range(40):
        if len(got) >= n: return
        pg.wait_for_timeout(100)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    ctx, pg, errs, pops = page(b)
    pg.click("#wa-send"); pg.wait_for_timeout(600)
    check("form kosong/tidak lengkap: tidak ada data terkirim", len(got) == 0, got)
    fill(pg, sumber=""); pg.click("#wa-send"); pg.wait_for_timeout(500)
    check("'Tahu dari mana' kosong: tidak ada data terkirim", len(got) == 0, got)
    pg.select_option("#f-sumber", "instagram"); pg.click("#wa-send"); wait(1, pg); pg.wait_for_timeout(500)
    check("form lengkap + klik kirim: 1 data terkirim", len(got) == 1, len(got))
    d1 = json.loads(got[0]["body"]) if got else {}
    check("isi data benar", d1.get("nama") == "Rina" and d1.get("look") == "Wisuda" and d1.get("tanggal") == "2027-03-20" and d1.get("jam") == "07:30"
          and d1.get("lokasi") == "Cimanggis, Depok" and str(d1.get("jumlah")) == "3" and d1.get("sumber") == "Instagram" and d1.get("catatan") == "Hijab" and d1.get("website") == "", d1)
    check("ID berbentuk aman untuk skrip", bool(re.fullmatch(r"[A-Za-z0-9-]{8,64}", d1.get("id", ""))), d1.get("id"))
    check("dikirim sebagai text/plain (tanpa izin CORS tambahan)", got and (got[0]["ctype"] or "").startswith("text/plain"), got[0]["ctype"] if got else "")
    check("WhatsApp tetap terbuka di tab baru", len(pops) == 1, len(pops))
    pg.fill("#f-catatan", "Ganti: non-hijab"); pg.click("#wa-send"); wait(2, pg)
    d2 = json.loads(got[1]["body"]) if len(got) > 1 else {}
    check("kirim ulang: ID sama, isi terbaru", d2.get("id") == d1.get("id") and d2.get("catatan") == "Ganti: non-hijab", d2)
    pg.click("#form-reset"); pg.wait_for_timeout(200); fill(pg, nama="Sari", sumber="teman"); pg.click("#wa-send"); wait(3, pg)
    d3 = json.loads(got[2]["body"]) if len(got) > 2 else {}
    check("setelah 'Kosongkan form': ID baru", d3.get("id") and d3.get("id") != d1.get("id") and d3.get("nama") == "Sari", d3)
    pg.focus("#f-nama"); pg.keyboard.press("Enter"); wait(4, pg)
    check("tekan Enter di form juga tercatat", len(got) == 4, len(got))
    pg.evaluate("document.getElementById('f-website').value='http://spam'"); pg.click("#wa-send"); wait(5, pg)
    d5 = json.loads(got[4]["body"]) if len(got) > 4 else {}
    check("kolom jebakan bot ikut terkirim (diabaikan oleh skrip)", d5.get("website") == "http://spam", d5.get("website"))
    trap = pg.evaluate("(()=>{const i=document.getElementById('f-website'),r=i.getBoundingClientRect();return {x:r.right,tab:i.tabIndex,hidden:i.closest('[aria-hidden=true]')!==null}})()")
    check("kolom jebakan tidak terlihat & tidak bisa di-Tab", trap["x"] < 0 and trap["tab"] == -1 and trap["hidden"], trap)
    check("tidak ada error JS", not errs, errs)
    ctx.close()
    # alur nyata: semua kiriman tadi diproses logika Apps Script tiruan
    open(str(OUT / "kiriman.json"), "w").write(json.dumps([g["body"] for g in got]))
    out = json.loads(subprocess.check_output(["env", "TZ=Asia/Jakarta", "node", str(HERE / "appscript_replay.js"), f"{root}/apps-script/data-booking.gs", str(OUT / "kiriman.json")]))
    check("hasil di spreadsheet: 2 baris (Rina diperbarui, Sari), spam diabaikan, lokasi Cimanggis, Depok, status pembayaran awal", len(out) == 2 and out[0]["nama"] == "Rina" and out[0]["catatan"] == "Ganti: non-hijab"
          and out[1]["nama"] == "Sari" and out[0]["sumber"] == "Instagram" and out[1]["sumber"] == "Dari teman" and all(r["status_bayar"] == "Masih nanya-nanya" for r in out) and out[0]["tgl"] == "2027-03-20" and out[0]["lokasi"] == "Cimanggis, Depok", out)
    # tanpa logUrl: tidak ada kiriman
    n0 = len(got); ctx, pg, errs, pops = page(b, url_on=False)
    fill(pg); pg.click("#wa-send"); pg.wait_for_timeout(800)
    check("logUrl kosong: tidak ada data terkirim, WA tetap terbuka", len(got) == n0 and len(pops) == 1, (len(got) - n0, len(pops)))
    ctx.close()
    # HP
    ctx, pg, errs, pops = page(b, vp=(375, 760)); n0 = len(got)
    fill(pg); pg.click("#wa-send"); wait(n0 + 1, pg)
    check("HP: data terkirim saat klik kirim", len(got) == n0 + 1 and not errs, (len(got) - n0, errs))
    ctx.close(); b.close()
bad = [r for r in res if not r[1]]
for n, ok, i in res: print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {i}"))
print(f"\n{len(res)-len(bad)}/{len(res)} lulus"); sys.exit(1 if bad else 0)
