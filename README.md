# Natasya Makeup — website one-page

Website statis (HTML, CSS, JS murni, tanpa framework) untuk MUA Natasya di Depok.

## Struktur folder

```
natasya-makeup/
├── index.html              # semua konten halaman
├── assets/
│   ├── css/style.css       # token warna & font ada di :root paling atas
│   └── js/main.js          # nomor WA & ID Google Sheets ada di CONFIG paling atas
├── PANDUAN-NATASYA.md      # cara ganti foto & testimoni lewat Google Sheets
└── README.md
```

## Cara ganti foto

Semua foto **tidak disimpan di repo**. Foto hero, foto Natasya (Tentang), 8 foto Pilih look,
dan galeri portofolio diambil dari Google Sheets "Isi Website Natasya Makeup", dengan file
fotonya di Google Drive. Foto yang belum diisi tampil sebagai kotak putih. Testimoni juga dari
spreadsheet; kalau spreadsheet gagal dimuat, 5 testimoni teks bawaan di `index.html` yang tampil.
Panduan lengkap: [PANDUAN-NATASYA.md](PANDUAN-NATASYA.md).

## Sumber isi & penanda kuning

Harga, paket, tambahan (add-on), lokasi, nomor WA, dan ketentuan booking diambil dari
4 brosur Natasya: Terms & Conditions, Makeup Regular, Promo Makeup Lamaran, dan
Graduation Makeup. Ketentuan booking masuk ke FAQ.

Info yang **tidak ada di brosur** belum dihapus, tapi ditandai atribut `data-draft` dan
tampil **tulisan kuning** (aturan di bagian atas `style.css`). Sumbernya: Instagram
(layanan akad/tari/photoshoot/fantasi, "Certified MUA sejak 2023", "born to be shining",
@makeupnatasya) atau karangan developer (harga & isi paket akad/photoshoot/tari/fantasi,
durasi, reschedule, area Jabodetabek, dll).

Setelah dicek bersama Natasya: hapus elemen yang salah, lepas atribut `data-draft` dari
yang benar, lalu hapus aturan kuning di `style.css`. Catatan: meta description & JSON-LD
(tidak terlihat di halaman) juga masih menyebut "bersertifikat", akad/tari/photoshoot/fantasi,
dan Jabodetabek.

- [ ] Harga lamaran Rp250.000 adalah **harga promo**. Ubah kalau promonya selesai.
- [ ] Izin klien untuk testimoni (diambil dari highlight IG "Kata Mereka").

## Yang masih harus diganti

- [ ] **Isi semua foto di spreadsheet** (Foto Utama + Portofolio). Sebelum diisi, website
      menampilkan kotak putih.
- [ ] Izin klien untuk foto portofolio asli & screenshot chat testimoni
- [ ] Gambar pratinjau saat link dibagikan di WhatsApp/sosmed (`og:image`) belum ada.
      Tidak bisa dari spreadsheet karena WhatsApp tidak menjalankan JavaScript: simpan satu
      foto asli 1200x630 sebagai `assets/img/og-cover.jpg` lalu pasang lagi tag `og:image`
      dengan URL lengkap.
- [ ] Domain final, lalu ganti `canonical` jadi URL lengkap
- [x] Nomor WA sudah nomor Natasya `6285171502605` (sesuai brosur). Tes otomatis memakai
      nomor tiruan dan memblokir WhatsApp, jadi tidak pernah mengirim ke Natasya.
- [ ] Konfirmasi area layanan (brosur hanya menyebut Cimanggis, Depok dan gratis transport 5 km)

## Catatan teknis: palet "Pilih look"

Tata letak palet dipilih otomatis oleh `initPanLayout()` di `main.js` supaya nama look
tidak pernah terpotong, termasuk di HP kecil dan saat ukuran huruf sistem diperbesar:
grid 4 kolom (desktop/tablet) -> `.is-pills` 2 kolom (HP) -> `.is-list` 1 kolom
(HP sangat kecil atau huruf sangat besar). Kalau menambah look baru dengan nama
panjang, tidak perlu ubah CSS.

## Uji lokal

```
python3 -m http.server 8000
```

lalu buka http://localhost:8000.

## Deploy

Folder ini bisa langsung di-upload ke Netlify, Vercel, GitHub Pages, atau hosting biasa.

