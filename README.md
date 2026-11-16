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

## Konten draf (WAJIB dikonfirmasi Natasya sebelum online)

Semua isi di bawah ini **karangan developer** supaya halaman terlihat jadi. Elemennya
ditandai atribut `data-draft` (27 elemen). Cari `data-draft` di `index.html`, atau
aktifkan baris komentar `[data-draft]` di `style.css` untuk melihatnya di browser.
Setelah dikonfirmasi, hapus atribut `data-draft`-nya.

- [ ] Harga "mulai dari" 8 jenis makeup. Patokan draf: MUA pemula umumnya
      Rp250-350 ribu per orang untuk wisuda, MUA berpengalaman mulai Rp600 ribu (Orami).
      Wisuda 350rb, lamaran 500rb, akad 1,2jt, bridesmaid 300rb/orang,
      photoshoot 350rb, tari 250rb/orang, reguler 300rb, fantasi 400rb.
- [ ] Isi paket ("Sudah termasuk") 8 jenis makeup
- [ ] FAQ: transport gratis di Depok, home service, hijab do termasuk paket,
      DP 50% + aturan reschedule/batal, durasi 60-90 menit, aturan rombongan
- [ ] Izin klien untuk 5 testimoni (diambil dari highlight IG "Kata Mereka")
- [ ] Deskripsi singkat tiap jenis makeup

## Yang masih harus diganti

- [ ] **Isi semua foto di spreadsheet** (Foto Utama + Portofolio). Sebelum diisi, website
      menampilkan kotak putih.
- [ ] Izin klien untuk foto portofolio asli & screenshot chat testimoni
- [ ] Gambar pratinjau saat link dibagikan di WhatsApp/sosmed (`og:image`) belum ada.
      Tidak bisa dari spreadsheet karena WhatsApp tidak menjalankan JavaScript: simpan satu
      foto asli 1200x630 sebagai `assets/img/og-cover.jpg` lalu pasang lagi tag `og:image`
      dengan URL lengkap.
- [ ] Domain final, lalu ganti `canonical` jadi URL lengkap
- [ ] **Nomor WA masih nomor tes developer.** Sebelum online, ganti `waNumber` di
      `assets/js/main.js` (CONFIG) ke nomor Natasya `6285171502605`. Semua link WA,
      teks nomor, dan data SEO otomatis ikut. Konfirmasi juga nomornya ke Natasya.
- [ ] Konfirmasi area layanan (Depok/Jabodetabek)

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

