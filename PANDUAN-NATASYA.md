# Panduan mengganti foto & testimoni website

Semua foto di website dan testimoni bisa diganti tanpa coding, cukup lewat **Google Drive** (tempat foto) dan **Google Sheets** (daftar isi website).

- Spreadsheet: **Isi Website Natasya Makeup**
  https://docs.google.com/spreadsheets/d/15qbmT3pzQlUKdb3AlZXk-Zf__gRcN40_OAGzR2qoAgk/edit
- Folder foto: **Website Natasya Makeup → Foto Website**
  https://drive.google.com/drive/folders/1LTZRf-WgQ2_WZPz-hXIq7vgwsoFQo6hM

## Langkah mengganti foto (bisa dari HP)

1. **Upload foto.** Buka aplikasi Google Drive, masuk folder *Foto Website*, tekan **+** lalu **Upload**, pilih fotonya.
2. **Salin link foto.** Tekan titik tiga (⋮) di samping foto, lalu **Salin link**.
3. **Tempel di spreadsheet.** Buka aplikasi Google Sheets, buka *Isi Website Natasya Makeup*, lalu pilih tab:
   - **Foto Utama**: foto bulat besar paling atas (`hero`), foto Natasya di bagian Tentang (`tentang`), dan foto tiap jenis makeup di "Pilih look" (`look-wisuda`, `look-akad`, dst.). Tempel link di kolom **foto** pada baris yang sesuai.
   - **Portofolio**: satu baris untuk satu foto hasil makeup. Pilih kategori dari daftar, tempel link, keterangan boleh kosong.
   - **Testimoni**: tempel link screenshot chat di kolom **foto**, atau tulis testimoninya di kolom **teks**.
4. **Cek.** Kolom **pratinjau** menampilkan foto kalau link-nya benar. Website ikut berubah dalam beberapa menit. Tutup lalu buka ulang website-nya.

**Menyembunyikan** foto/testimoni: pilih `tidak` di kolom **tampil**. **Menghapus**: hapus barisnya.

## Tampilan kalau foto & testimoni sudah banyak
- **Portofolio:** tampil 9 foto dulu di laptop (6 di HP/tablet), sisanya muncul saat pengunjung menekan **Lihat lebih banyak**. Urutan di website sama dengan urutan baris di spreadsheet, jadi taruh foto terbaik di baris paling atas.
- **Testimoni:** tampil 6 dulu di laptop (4 di HP), sisanya lewat tombol yang sama.
- **Screenshot chat yang panjang** dipotong dulu (maks ±420px di laptop, ±360px di HP) dengan tombol **Lihat chat lengkap**. Screenshot pendek tampil utuh.
- Jumlah foto tidak dibatasi. Spreadsheet sudah disiapkan 79 baris Portofolio dan 59 baris Testimoni lengkap dengan dropdown dan pratinjau.

## Aturan penting
- Pakai **foto tegak (portrait)**. Foto mendatar terpotong di kiri-kanan. Untuk `hero`, foto dipotong bulat, jadi wajah sebaiknya di tengah.
- Jangan hapus foto dari folder Drive selama masih dipakai di website.
- Jangan ubah judul kolom di baris paling atas, dan jangan ubah kolom **bagian** di tab Foto Utama. (Kalau dicoba, Google akan menampilkan peringatan.)
- Screenshot chat: **minta izin klien dulu**, lalu tutup nama dan nomor HP-nya sebelum diupload.
- Spreadsheet dan folder foto bisa dilihat siapa saja yang punya link-nya. Jangan tulis nomor HP atau alamat klien di sana.
- Foto yang belum diisi, atau link-nya salah, tampil sebagai **kotak putih** di website. Isi semua baris di Foto Utama dan tambahkan foto di Portofolio sebelum link website disebarkan.

---

## Catatan teknis (developer)

- Website membaca spreadsheet lewat `docs.google.com/spreadsheets/d/<ID>/gviz/tq?tqx=out:csv&headers=1&sheet=<tab>`. ID ada di `CONFIG.sheets.spreadsheetId` (`assets/js/main.js`). Nama tab di `CONFIG.sheets.tabs`.
- Syarat: spreadsheet dibagikan **"Siapa saja yang memiliki link: Pelihat"**, begitu juga folder *Foto Website* (file di dalamnya ikut mewarisi).
- Kalau Google suatu saat memblokir cara baca ini, pakai cadangan: di spreadsheet buka File → Bagikan → **Publikasikan ke web**, pilih tiap tab dengan format CSV, lalu tempel link-nya ke `CONFIG.sheets.csvUrls`.
- Foto Drive ditampilkan lewat `drive.google.com/thumbnail?id=...`. Ini bukan API resmi Google. Kalau berhenti jalan, kolom **foto** juga menerima link `https://` gambar dari tempat lain (misalnya Cloudinary).
- Kolom **pratinjau** memakai rumus `IMAGE`. Pemilik/editor harus sekali membuka spreadsheet di browser desktop dan menekan **"Izinkan akses"**, sebelum itu semua pratinjau bertuliskan "Link belum benar".
- Repo tidak menyimpan foto sama sekali. Semua `<img>` mulai sebagai kotak putih (GIF transparan 1x1 + kelas `is-empty`) lalu diisi dari spreadsheet. Kalau spreadsheet gagal dimuat, semua foto tetap kotak putih, sedangkan testimoni memakai 5 teks bawaan di `index.html`.
- Yang **tidak** bisa diganti lewat spreadsheet: gambar pratinjau link saat website dibagikan di WhatsApp/sosmed (`og:image`), karena WhatsApp tidak menjalankan JavaScript. Saat ini belum ada; tambahkan file `assets/img/og-cover.jpg` (foto asli, 1200x630) dan tag `og:image` dengan URL lengkap.
