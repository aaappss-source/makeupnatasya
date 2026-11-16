# Pasang pencatat data booking ke Google Sheets

Setiap pengunjung menekan **Kirim ke WhatsApp** dengan form yang sudah lengkap, datanya masuk ke
spreadsheet **Data Booking Natasya Makeup** (folder Google Drive *Website Natasya Makeup*), walaupun
pesan WhatsApp-nya tidak jadi dikirim. Kolom **Status** (Berhasil / Gagal / Pending) dan
**Keterangan** diisi manual.

Spreadsheet: https://docs.google.com/spreadsheets/d/1lFOk_K9MTq5SyMvRuqiAQ0zpXmiN9n0H8VmCqS1nLqs/edit

Website tidak bisa menulis ke Google Sheets sendiri, jadi perlu "jembatan" berupa Apps Script.
Langkah ini cukup sekali, sekitar 5 menit, dan harus dilakukan pemilik spreadsheet.

## Langkah pasang

1. Buka spreadsheet di atas lewat laptop.
2. Klik menu **Ekstensi > Apps Script**. Tab baru terbuka.
3. Ganti nama proyek (kiri atas, "Proyek tanpa judul") jadi `Data Booking Website`.
4. Hapus semua isi `Code.gs`, lalu tempel seluruh isi file
   [`apps-script/data-booking.gs`](apps-script/data-booking.gs) dari repo ini. Klik ikon simpan.
5. **Tes dulu:** di bagian atas, pilih fungsi `tesSimpan`, lalu klik **Run**.
   - Muncul permintaan izin: klik **Review permissions**, pilih akun Google kamu.
   - Kalau muncul "Google hasn't verified this app": klik **Advanced**, lalu
     **Go to Data Booking Website (unsafe)**, lalu **Allow**. Ini wajar untuk skrip buatan sendiri.
     Skrip hanya diberi akses ke spreadsheet ini saja (`@OnlyCurrentDoc`).
   - Cek tab **Booking**: harus ada baris "Tes dari editor". Hapus baris itu.
6. Klik **Deploy > New deployment**. Klik ikon roda gigi, pilih **Web app**, lalu isi:
   - Description: `Website`
   - Execute as: **Me**
   - Who has access: **Anyone**
   Klik **Deploy**, lalu salin **Web app URL** (bentuknya `https://script.google.com/macros/s/.../exec`).
7. Tempel URL itu di `assets/js/main.js`, bagian `booking: { logUrl: "..." }`, lalu commit
   (lihat [EDIT-TEKS.md](EDIT-TEKS.md)). Atau kirim URL-nya ke Claude untuk dipasang.
8. **Tes dari website:** buka website, isi form sampai lengkap, tekan **Kirim ke WhatsApp**
   (tidak perlu benar-benar mengirim pesan di WhatsApp). Dalam beberapa detik baris baru muncul di
   tab Booking dengan status **Pending**.

## Kalau skrip diubah nanti

Klik **Deploy > Manage deployments**, klik ikon pensil, pilih **Version: New version**, lalu
**Deploy**. URL-nya tetap sama. Jangan buat **New deployment** lagi, karena URL-nya akan berubah dan
website harus diperbarui.

## Cara kerja & pengaman

- Kolom di tab Booking: Waktu isi form, Nama, Jenis makeup, Tanggal acara, Makeup selesai jam, Lokasi,
  Jumlah orang, Tahu dari, Catatan, Status, Keterangan, dan ID (kolom L, disembunyikan). Kalau urutan
  kolom diubah, `KOLOM_ID` dan urutan `data` di skrip harus ikut diubah.

- Satu isian form = satu baris. Kalau pengunjung mengubah isian lalu menekan kirim lagi, baris yang
  sama diperbarui; Status dan Keterangan yang sudah diisi tidak berubah. Setelah tombol
  **Kosongkan form**, isian berikutnya jadi baris baru.
- Form yang belum lengkap (masih ada pesan error) tidak dicatat.
- URL Web App tertulis di kode website, jadi siapa pun bisa mencoba mengirim data palsu. Pengaman yang
  terpasang: data harus lengkap & berformat benar, kolom jebakan bot, maksimal 20 kiriman per menit,
  teks yang diawali `=`, `+`, `-`, `@` tidak dijalankan sebagai rumus, dan panjang teks dibatasi.
- Spreadsheet ini berisi data pribadi pelanggan. **Jangan** dibagikan dengan "Siapa saja yang memiliki
  link". Kalau Natasya perlu akses, bagikan ke emailnya sebagai Editor.
- Kalau `logUrl` dikosongkan, website tetap jalan normal, hanya tidak mencatat.
