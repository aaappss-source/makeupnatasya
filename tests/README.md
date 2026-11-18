# Tes website Natasya Makeup

Tes otomatis untuk mengecek website sebelum di-push. Semua tes jalan di komputer sendiri (server lokal), jadi tidak mengubah website yang sudah tayang.

## Persiapan (sekali saja)

```bash
pip install playwright pillow
python3 -m playwright install chromium
```

Butuh juga Node.js untuk tes Apps Script. Tes dijalankan di Linux atau macOS (di Windows pakai WSL).

## Menjalankan

```bash
python3 tests/run_all.py
```

Tiap tes juga bisa dijalankan sendiri, misalnya `python3 tests/test_wa_float.py` atau `node tests/test_appscript.js`. Screenshot hasil tes tersimpan di `tests/output/` dan tidak ikut di-commit.

## Isi tes

| File | Yang dicek |
| --- | --- |
| `test_site.py` | Isi halaman, semua link WhatsApp, form booking |
| `test_mobile.py` | Tidak ada elemen keluar layar atau teks terpotong di HP |
| `test_looks.py` | Pilih look (Wisuda, Lamaran, Akad, Bridesmaid) di laptop dan HP |
| `test_sheets.py` | Foto, portofolio, dan testimoni dari Google Sheets, termasuk kalau Sheets gagal dimuat |
| `test_content.py` | Harga dan isi paket sesuai brosur |
| `test_lokasi.py` | Pilihan kota dan kecamatan di form booking |
| `test_booking_log.py` | Data form terkirim ke Apps Script (pakai server tiruan) |
| `test_wa_float.py` | Tombol WhatsApp melayang di kanan bawah dan draf pesannya |
| `test_appscript.js` | Logika `apps-script/data-booking.gs` dengan spreadsheet tiruan |

## Aturan keamanan

- Tes **tidak pernah** menghubungi nomor WhatsApp asli Natasya. Nomornya diganti nomor tiruan `6281200000001`, dan semua request ke `wa.me` serta `api.whatsapp.com` diblok.
- Tes **tidak pernah** mengirim data ke Apps Script atau spreadsheet asli. `logUrl` diganti server tiruan atau dikosongkan, dan request ke `script.google.com` diblok.
- Data Google Sheets dan foto Drive diganti data tiruan dari folder `fixtures/`. Foto di sana gambar buatan, bukan foto klien.
- Kalau menambah tes baru, ikuti aturan yang sama.
