/**
 * @OnlyCurrentDoc
 *
 * Penerima data form booking website Natasya Makeup.
 * Tempel di spreadsheet "Data Booking Natasya Makeup": Ekstensi > Apps Script.
 * Cara pasang lengkap: PASANG-DATA-BOOKING.md di repo website.
 *
 * Setiap tombol "Kirim ke WhatsApp" ditekan (form sudah lengkap), website mengirim
 * data ke sini. Satu isian form punya satu ID: kalau dikirim ulang, barisnya
 * diperbarui, Status & Keterangan tidak disentuh.
 */

const NAMA_TAB = 'Booking';
const KOLOM_ID = 11;          // kolom K, disembunyikan
const MAKS_PER_MENIT = 20;    // pengaman dari kiriman spam

function doPost(e) {
  try {
    simpanBooking_(JSON.parse(e.postData.contents));
  } catch (err) {
    console.error(err);
  }
  return ContentService.createTextOutput('ok');
}

function simpanBooking_(d) {
  if (!d || typeof d !== 'object') return 'abaikan';
  if (d.website) return 'abaikan';                       // jebakan bot (kolom tersembunyi diisi)

  const id = String(d.id || '');
  if (!/^[A-Za-z0-9-]{8,64}$/.test(id)) return 'abaikan';

  const nama = teks_(d.nama, 80);
  const look = teks_(d.look, 40);
  const lokasi = teks_(d.lokasi, 150);
  const catatan = teks_(d.catatan, 500);
  const tgl = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(d.tanggal || ''));
  const jam = /^\d{2}:\d{2}$/.test(String(d.jam || '')) ? String(d.jam) : '';
  const jumlah = Math.floor(Number(d.jumlah));
  if (!nama || !look || !lokasi || !tgl || !(jumlah >= 1 && jumlah <= 99)) return 'abaikan';
  const ss = SpreadsheetApp.getActive();
  // Tanggal dibuat di zona waktu spreadsheet (jam 12 siang) supaya tidak mundur/maju sehari.
  const tanggal = Utilities.parseDate(tgl[0] + ' 12:00', ss.getSpreadsheetTimeZone(), 'yyyy-MM-dd HH:mm');

  // batas jumlah kiriman per menit
  const cache = CacheService.getScriptCache();
  const kunci = 'n' + Utilities.formatDate(new Date(), 'Asia/Jakarta', 'yyyyMMddHHmm');
  const n = Number(cache.get(kunci) || 0);
  if (n >= MAKS_PER_MENIT) return 'terlalu banyak';
  cache.put(kunci, String(n + 1), 120);

  const kunciTulis = LockService.getScriptLock();
  kunciTulis.waitLock(10000);
  try {
    const tab = ss.getSheetByName(NAMA_TAB);
    const data = [new Date(), nama, look, tanggal, jam, lokasi, jumlah, catatan];
    const akhir = tab.getLastRow();
    if (akhir >= 2) {
      const ids = tab.getRange(2, KOLOM_ID, akhir - 1, 1).getValues();
      for (let i = ids.length - 1; i >= 0; i--) {
        if (String(ids[i][0]) === id) {
          tab.getRange(i + 2, 1, 1, data.length).setValues([data]);   // Status & Keterangan tetap
          return 'diperbarui';
        }
      }
    }
    tab.appendRow(data.concat(['Pending', '', id]));
    return 'baru';
  } finally {
    kunciTulis.releaseLock();
  }
}

// Rapikan teks: buang karakter kontrol, batasi panjang, dan cegah teks dibaca sebagai rumus.
function teks_(v, maks) {
  let s = String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, maks);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

// Jalankan sekali dari editor (pilih fungsi ini lalu Run) untuk mengecek izin & tab.
function tesSimpan() {
  const hasil = simpanBooking_({
    id: 'tes-' + Date.now(), nama: 'Tes dari editor', look: 'Wisuda',
    tanggal: Utilities.formatDate(new Date(), 'Asia/Jakarta', 'yyyy-MM-dd'),
    jam: '07:30', lokasi: 'Cimanggis, Depok', jumlah: 1, catatan: 'Boleh dihapus',
  });
  console.log('Hasil: ' + hasil);
}
