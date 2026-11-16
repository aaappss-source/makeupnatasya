# Natasya Makeup — website one-page

Website statis (HTML, CSS, JS murni, tanpa framework) untuk MUA Natasya di Depok.

## Struktur folder

```
natasya-makeup/
├── index.html              # semua konten halaman
├── assets/
│   ├── css/style.css       # token warna & font ada di :root paling atas
│   ├── js/main.js          # nomor WA & ID Google Sheets ada di CONFIG paling atas
│   └── img/
│       ├── logo-*.webp/png            # logo asli lengkap (footer), latar transparan
│       ├── logo-mendatar-*.webp/png   # header: ikon kiri, tulisan kanan
│       ├── logo-tulisan-*.webp/png    # hero: tulisan NATASYA MAKEUP saja
│       └── og-cover.jpg    # gambar preview saat link dibagikan (1200x630)
├── PANDUAN-NATASYA.md      # cara ganti foto & testimoni lewat Google Sheets
├── EDIT-TEKS.md            # cara edit tulisan (harga, paket, FAQ, kontak) langsung di GitHub
├── PASANG-DATA-BOOKING.md  # catat isian form booking ke Google Sheets (Apps Script)
├── apps-script/data-booking.gs  # kode Apps Script untuk spreadsheet Data Booking
└── README.md
```

## Cara ganti foto

Semua foto **tidak disimpan di repo**. Foto hero, foto Natasya (Tentang), 8 foto Pilih look,
dan galeri portofolio diambil dari Google Sheets "Isi Website Natasya Makeup", dengan file
fotonya di Google Drive. Foto yang belum diisi tampil sebagai kotak putih. Testimoni juga dari
spreadsheet; kalau spreadsheet gagal dimuat, 5 testimoni teks bawaan di `index.html` yang tampil.
Panduan lengkap: [PANDUAN-NATASYA.md](PANDUAN-NATASYA.md).

## Sumber isi

Harga, paket, tambahan (add-on), lokasi, nomor WA, dan ketentuan booking diambil dari
4 brosur Natasya: Terms & Conditions, Makeup Regular, Promo Makeup Lamaran, dan
Graduation Makeup. Ketentuan booking masuk ke FAQ.

Info yang tidak ada di brosur sudah dicek: sebagian dipertahankan, sebagian dihapus
(17 Nov 2026). Penanda kuning (`data-draft`) sudah dilepas semua.

- [ ] Harga lamaran Rp250.000 adalah **harga promo**. Ubah kalau promonya selesai.
- [ ] Izin klien untuk testimoni (diambil dari highlight IG "Kata Mereka").

## Yang masih harus diganti

- [ ] **Isi semua foto di spreadsheet** (Foto Utama + Portofolio). Sebelum diisi, website
      menampilkan kotak putih.
- [ ] Izin klien untuk foto portofolio asli & screenshot chat testimoni
- [x] Gambar preview link (`og:image`) = logo Natasya di atas putih, 1200x630.
- [ ] Kalau pindah ke domain sendiri: ganti `canonical`, `og:url`, dan `og:image` di `index.html`
      (sekarang memakai alamat GitHub Pages).
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

