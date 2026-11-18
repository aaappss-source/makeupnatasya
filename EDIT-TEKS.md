# Cara mengedit tulisan website tanpa coding

Panduan untuk mengganti teks (harga, paket, FAQ, kontak, dan lainnya) langsung di GitHub.
Foto dan testimoni tidak diedit di sini, tapi lewat spreadsheet (lihat [PANDUAN-NATASYA.md](PANDUAN-NATASYA.md)).

## Pilih cara mengedit

### 1. Edit langsung di website GitHub
Cocok untuk ganti harga atau satu-dua kalimat.

1. Buka repo `makeupnatasya` di GitHub, lalu klik file yang mau diubah (biasanya `index.html`).
2. Klik ikon pensil (**Edit this file**) di kanan atas.
3. Tekan **Ctrl+F**, cari tulisannya (misalnya `Rp200.000`), lalu ganti.
4. Klik **Commit changes**, isi keterangan singkat (misalnya "Ganti harga wisuda"), lalu konfirmasi.
5. Tunggu 1-2 menit, buka website, lalu tekan **Ctrl+Shift+R** supaya browser tidak menampilkan versi lama.

Bisa juga lewat browser HP, tapi lebih repot karena layarnya kecil.

### 2. Editor di browser (github.dev)
Cocok kalau satu info muncul di beberapa tempat.

1. Buka halaman repo, lalu tekan tombol titik (`.`) di keyboard.
2. Editor mirip VS Code terbuka di browser. Tekan **Ctrl+Shift+F** untuk mencari tulisan di semua file sekaligus.
3. Setelah selesai, buka ikon **Source Control** di kiri, tulis keterangan, lalu klik **Commit & Push**.

### 3. VS Code + GitHub Desktop di laptop
Cocok untuk perubahan besar, karena hasilnya bisa dilihat dulu sebelum di-upload.

1. Install [GitHub Desktop](https://desktop.github.com/) dan [VS Code](https://code.visualstudio.com/), lalu clone repo ini lewat GitHub Desktop.
2. Buka foldernya di VS Code. Pasang ekstensi **Live Server**, klik kanan `index.html`, pilih **Open with Live Server** untuk melihat hasilnya.
3. Kalau sudah benar, kembali ke GitHub Desktop: tulis keterangan, klik **Commit to main**, lalu **Push origin**.

## Letak tulisan

| Yang mau diganti | File | Cari kata ini |
|---|---|---|
| Harga, isi paket, tambahan, deskripsi layanan | `index.html` | `Makeup wisuda`, `Makeup lamaran`, `Makeup bridesmaid`, dst. |
| Nama layanan di palet warna | `index.html` | `pan-name` |
| FAQ dan ketentuan booking | `index.html` | `faq-list` |
| Teks pembuka di bagian atas | `index.html` | `hero-lead` |
| Bagian "Halo, aku Natasya" | `index.html` | `about-copy` |
| Lokasi, Instagram, footer | `index.html` | `site-footer` |
| Judul di tab browser & Google, teks preview link | `index.html` (paling atas) | `<title>`, `name="description"`, `og:` |
| Nomor WhatsApp | `assets/js/main.js` | `waNumber` |
| Draf pesan tombol WhatsApp di pojok kanan bawah | `assets/js/main.js` | `waChatText` (satu baris pesan = satu teks dalam tanda kutip, diakhiri koma) |
| Isi pesan WA otomatis dari form booking | `assets/js/main.js` | `buildMessage` |
| Pilihan kota & kecamatan di form booking | `assets/js/main.js` | `LOKASI_MAKEUP` (satu baris per kota: `["Nama kota", ["Kecamatan", ...]]`) |
| Pilihan jenis makeup di form | `index.html` dan `assets/js/main.js` | `f-look` (HTML) dan `LOOK_NAMES` (JS) |

## Aturan penting

- **Ganti hanya tulisan di antara tag.** Contoh: di `<dd>Rp200.000</dd>`, yang diganti hanya `Rp200.000`. Jangan hapus `<`, `>`, `/`, atau tanda kutip `"`.
- **Tanda `&` di kode ditulis `&amp;`.** Contoh: `Lamaran &amp; akad` tampil di website sebagai "Lamaran & akad".
- **Nomor WA ditulis format internasional tanpa `+` dan tanpa 0 di depan.** Contoh: 0851-7150-2605 ditulis `6285171502605`. Semua tombol WA, teks nomor, dan data Google ikut berubah otomatis.
- **Satu info bisa ada di beberapa tempat.** Selalu cari dengan Ctrl+F atau Ctrl+Shift+F supaya semuanya ikut terganti:
  - harga bridesmaid/regular dan harga rombongan: kartu layanan + FAQ "Bisa booking untuk rombongan?"
  - harga wisuda berdua dengan pendamping/bestie: kartu wisuda + FAQ "Bisa booking untuk rombongan?"
  - harga wisuda, lamaran, regular: kartu layanan + `name="description"` di bagian paling atas
  - hairdo dan softlens: kartu layanan + FAQ "Bisa tambah hairdo atau softlens?"
  - DP dan pelunasan: FAQ + langkah booking di bagian Booking
  - lokasi "Cimanggis, Depok": hero, Tentang, FAQ, footer, teks untuk Google, dan `city` di `assets/js/main.js`
- **Kalau menambah atau menghapus jenis makeup**, ubah tiga tempat sekaligus: tombol palet (`pan`), kartu detailnya (`look-detail`), dan pilihan di form (`f-look`), lalu `LOOK_NAMES` di `assets/js/main.js`. Ini lebih aman dikerjakan dengan cara 3 supaya bisa dicek dulu.
- **Commit ke `main` langsung tampil di website.** Kalau ada yang salah, buka file itu di GitHub, klik **History**, buka versi sebelumnya, lalu salin lagi isinya, atau minta bantuan untuk revert.

## Setelah mengedit

- Cek di laptop **dan** HP.
- Kalau setelah 5 menit website belum berubah, buka tab **Actions** di repo. Tanda silang merah berarti proses publish gagal. Klik untuk melihat sebabnya.
- Kalau nanti minta bantuan Claude untuk mengubah website lagi, bilang kalau kamu sudah mengedit sendiri, supaya versi terbaru dari GitHub diambil dulu dan editanmu tidak tertimpa.
