"""Jalankan semua tes website Natasya Makeup sekaligus.

Cara pakai (dari folder repo):  python3 tests/run_all.py
Hasil screenshot tersimpan di tests/output/ (tidak ikut di-commit).
"""
import os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = [
    "test_site.py",        # isi halaman, link WA, form dasar
    "test_mobile.py",      # tidak ada elemen keluar layar / teks terpotong
    "test_looks.py",       # pilih look (4 layanan), layout laptop & HP
    "test_sheets.py",      # foto/portofolio/testimoni dari Google Sheets
    "test_content.py",     # teks harga & paket sesuai brosur
    "test_lokasi.py",      # pilihan kota & kecamatan di form
    "test_booking_log.py", # data form terkirim ke Apps Script (tiruan)
    "test_wa_float.py",    # tombol WhatsApp melayang
    "test_lightbox.py",    # portofolio: lihat foto besar, geser, tutup
    "test_appscript.js",   # logika Apps Script data booking
]


def summary(out):
    m = re.findall(r"(\d+)/(\d+) lulus", out)
    if m:
        a, b = m[-1]
        return f"{a}/{b} lulus", a == b
    if "SEMUA BERSIH" in out:
        return "bersih", True
    passed = len(re.findall(r"^PASS", out, re.M))
    return f"{passed} PASS", passed > 0


gagal = []
for name in TESTS:
    cmd = ["node", str(HERE / name)] if name.endswith(".js") else [sys.executable, str(HERE / name)]
    env = dict(os.environ, TZ="Asia/Jakarta", PYTHONIOENCODING="utf-8")
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    out = p.stdout + p.stderr
    fails = [l for l in out.splitlines() if l.startswith("FAIL") or "keluar area" in l or "terpotong:" in l]
    ringkas, ok = summary(out)
    ok = ok and p.returncode == 0 and not fails
    print(f"{'OK  ' if ok else 'GAGAL'} {name:<20} {ringkas}")
    if not ok:
        gagal.append(name)
        for line in (fails or out.strip().splitlines()[-8:])[:10]:
            print("      " + line[:300])

print("\nSemua tes lulus." if not gagal else f"\n{len(gagal)} tes gagal: {', '.join(gagal)}")
sys.exit(1 if gagal else 0)
