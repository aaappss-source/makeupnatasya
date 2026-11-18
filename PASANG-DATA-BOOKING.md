# Pasang pencatat data booking ke Google Sheets

Setiap pengunjung menekan **Kirim ke WhatsApp** dengan form yang sudah lengkap, datanya masuk ke
spreadsheet **Data Booking Natasya Makeup** (folder Google Drive *Website Natasya Makeup*), walaupun
pesan WhatsApp-nya tidak jadi dikirim. Kolom **Status pembayaran** dan **Keterangan** diisi manual;
kolom **Status** terisi otomatis dari Status pembayaran:

| Status pembayaran (isi manual) | Status (otomatis) |
|---|---|
| Masih nanya-nanya (isian awal) | Pending |
| Sudah DP | Follow Up |
| Sudah lunas | Berhasil |
| Tidak ada kabar | Gagal |

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
   tab Booking dengan Status pembayaran **Masih nanya-nanya** dan Status **Pending**.

## Kalau skrip diubah nanti

Klik **Deploy > Manage deployments**, klik ikon pensil, pilih **Version: New version**, lalu
**Deploy**. URL-nya tetap sama. Jangan buat **New deployment** lagi, karena URL-nya akan berubah dan
website harus diperbarui.

## Input booking manual

Booking yang masuk lewat chat WA, DM, atau telepon diketik di baris kosong paling bawah tab **Booking**,
supaya ikut terhitung di dashboard. Kolom Jenis makeup, Tahu dari, Status pembayaran, dan Masuk lewat
berupa dropdown; kolom tanggal hanya menerima tanggal. Isi **Masuk lewat = Manual**, kosongkan kolom
Status (otomatis) dan ID. Lokasi ditulis dengan format `Kecamatan, Kota` (contoh `Cimanggis, Depok`)
supaya sama dengan isian dari website.

## Cara kerja & pengaman

- Kolom di tab Booking: Waktu isi form, Nama, Jenis makeup, Tanggal acara, Makeup selesai jam, Lokasi,
  Jumlah orang, Tahu dari, Catatan (A-I), Status (J), Status pembayaran (K), Keterangan (L), ID
  (M, disembunyikan), dan Masuk lewat (N: Website / Manual). Kalau urutan kolom diubah, konstanta
  `KOLOM_...` dan urutan `data` di skrip harus ikut diubah.
- Status dihitung oleh satu rumus di sel **J1** (`ARRAYFORMULA`). Skrip tidak menulis ke kolom J, dan
  baris baru dicari dari isi semua kolom selain J, bukan `getLastRow()`, karena rumus itu mengisi kolom J
  sampai bawah. Baris yang diketik manual (walaupun kolom A-nya lupa diisi) tidak akan tertimpa.
  Kalau sel di kolom J diketik manual, rumus di J1 jadi error (#REF!); hapus ketikan itu untuk memperbaiki.

- Satu isian form = satu baris. Kalau pengunjung mengubah isian lalu menekan kirim lagi, baris yang
  sama diperbarui; Status pembayaran dan Keterangan yang sudah diisi tidak berubah. Setelah tombol
  **Kosongkan form**, isian berikutnya jadi baris baru.
- Form yang belum lengkap (masih ada pesan error) tidak dicatat.
- URL Web App tertulis di kode website, jadi siapa pun bisa mencoba mengirim data palsu. Pengaman yang
  terpasang: data harus lengkap & berformat benar, kolom jebakan bot, maksimal 20 kiriman per menit,
  teks yang diawali `=`, `+`, `-`, `@` tidak dijalankan sebagai rumus, dan panjang teks dibatasi.
- Spreadsheet ini berisi data pribadi pelanggan. **Jangan** dibagikan dengan "Siapa saja yang memiliki
  link". Kalau Natasya perlu akses, bagikan ke emailnya sebagai Editor.
- Kalau `logUrl` dikosongkan, website tetap jalan normal, hanya tidak mencatat.
