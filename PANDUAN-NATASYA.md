# Panduan mengganti foto & testimoni website

Tidak perlu coding. Cukup pakai **Google Drive** (untuk foto) dan **Google Sheets** (daftar isi website).

## Yang dilakukan Natasya (tiap mau tambah/ganti foto)

1. **Upload foto** ke folder Drive "Foto Website".
2. Klik kanan foto → **Bagikan** → **Salin link**.
3. Buka spreadsheet website, tab **Portofolio**, tambah satu baris di bawah:
   - `kategori`: pilih salah satu: `wisuda`, `lamaran`, `akad`, `bridesmaid`, `tari`, `fantasi`, `photoshoot`, `reguler`
   - `foto`: tempel link tadi
   - `keterangan`: tulisan kecil di bawah foto (boleh kosong, nanti otomatis memakai nama kategori)
4. Selesai. Perubahan muncul di website dalam beberapa menit. Kalau belum muncul, tutup lalu buka ulang website-nya.

**Menyembunyikan foto:** isi kolom `tampil` dengan `tidak`. Baris tidak perlu dihapus.
**Menghapus foto:** hapus barisnya di spreadsheet.

### Testimoni
Tab **Testimoni**, caranya sama. Ada dua pilihan per baris:
- screenshot chat: upload ke Drive, lalu tempel link di kolom `foto`
- tulisan biasa: isi kolom `teks`

Sebelum upload screenshot chat: **minta izin klien dan tutup nama/nomor HP yang terlihat** (blur atau tutup dengan kotak).

### Tips foto
- Paling bagus **foto tegak (portrait)**, perbandingan 4:5. Foto mendatar akan terpotong di tengah.
- Ukuran bebas, tapi jangan lebih dari sekitar 5 MB supaya cepat diupload.
- Jangan hapus atau pindahkan foto dari Drive kalau masih dipakai di website, karena fotonya akan hilang dari website.
- Folder Drive harus tetap diatur **"Siapa saja yang memiliki link"** (cukup sebagai Pelihat), kalau tidak, fotonya tidak tampil.
- Jangan ubah judul kolom di baris paling atas (`kategori`, `foto`, `keterangan`, `tampil`).

Kalau ada foto yang linknya salah atau tidak bisa dibuka, foto itu otomatis tidak ditampilkan, jadi website tidak rusak.

---

## Setup satu kali (dilakukan developer)

1. Buat Google Sheets baru dengan dua tab bernama persis **Portofolio** dan **Testimoni**.
   Impor `sheets-template/Portofolio.csv` dan `sheets-template/Testimoni.csv` ke masing-masing tab (File → Impor).
2. Di tab Portofolio, kolom `kategori`: Data → Validasi data → daftar item (`wisuda, lamaran, akad, bridesmaid, tari, fantasi, photoshoot, reguler`) supaya Natasya tinggal memilih.
3. Bagikan spreadsheet ke akun Google Natasya sebagai **Editor**.
4. Buat folder Drive "Foto Website", atur ke "Siapa saja yang memiliki link" → **Pelihat**.
5. Untuk **tiap tab**: File → Bagikan → **Publikasikan ke web** → pilih nama tab, format **CSV** → Publikasikan → salin link.
6. Tempel kedua link itu di `assets/js/main.js`:

```js
sheets: {
  portfolioCsv: "https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&single=true&output=csv",
  testimonialsCsv: "https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&single=true&output=csv",
},
```

Kalau link dikosongkan, atau Sheets gagal dimuat, website otomatis memakai foto dan testimoni bawaan di `index.html`.

### Hal yang perlu diketahui
- Isi spreadsheet yang dipublikasikan ke web **bisa dibaca siapa pun** yang punya linknya. Jangan taruh data pribadi (nomor HP, alamat klien) di situ.
- Foto diambil lewat alamat `drive.google.com/thumbnail`. Ini fitur Google yang banyak dipakai tapi bukan API resmi, jadi bisa berubah. Kalau suatu hari foto Drive tidak tampil, ganti sumber foto ke Cloudinary: tempel link `https://...` gambarnya di kolom `foto`, kodenya sudah menerima link https biasa.
- Bagian "Pilih look" di atas (foto per jenis makeup) dan foto profil di bagian Tentang masih foto tetap di `assets/img/`, belum dari spreadsheet.
