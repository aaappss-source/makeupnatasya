// Jalankan daftar kiriman (JSON) ke logika Apps Script tiruan, cetak isi tab Booking.
const fs = require("fs"); const vm = require("vm");
const src = fs.readFileSync(process.argv[2], "utf8"); const payloads = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
// Tab Booking: A-I data, J Status (rumus, tidak ditulis skrip), K Status pembayaran, L Keterangan, M ID.
const blank = () => Array(14).fill("");
const rows = [["Waktu","Nama","Jenis","Tanggal","Jam","Lokasi","Jumlah","Tahu dari","Catatan","Status","Status pembayaran","Keterangan","ID","Masuk lewat"]];
for (let i = 0; i < 30; i++) rows.push(blank());
const store = {};
const sheet = { getLastRow: () => rows.length, getMaxRows: () => rows.length, getMaxColumns: () => 14,
  insertRowsAfter: (a, n) => { for (let i = 0; i < n; i++) rows.splice(a, 0, blank()); },
  appendRow: () => { throw new Error("appendRow tidak dipakai lagi"); },
  getRange: (r, c, nr = 1, nc = 1) => ({ getValues: () => rows.slice(r - 1, r - 1 + nr).map(x => x.slice(c - 1, c - 1 + nc)),
    setValues: vals => vals.forEach((v, i) => v.forEach((x, k) => rows[r - 1 + i][c - 1 + k] = x)),
    setValue: x => { rows[r - 1][c - 1] = x; }, setNumberFormat() {} }) };
const ctx = { console: { log() {}, error() {} }, Date, JSON, String, Number, Math,
  SpreadsheetApp: { getActive: () => ({ getSheetByName: () => sheet, getSpreadsheetTimeZone: () => "Asia/Jakarta" }) },
  CacheService: { getScriptCache: () => ({ get: k => store[k] ?? null, put: (k, v) => store[k] = v }) },
  LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
  Utilities: { formatDate: () => "x", parseDate: (s) => { const [y, m, d] = s.slice(0, 10).split("-").map(Number); return new Date(y, m - 1, d, 12); } }, ContentService: { createTextOutput: t => ({ text: t }) } };
vm.createContext(ctx); vm.runInContext(src, ctx);
payloads.forEach(p => ctx.doPost({ postData: { contents: p } }));
console.log(JSON.stringify(rows.slice(1).filter(r => r[0] !== "").map(r => ({ nama: r[1], look: r[2], tgl: r[3] instanceof Date ? `${r[3].getFullYear()}-${String(r[3].getMonth() + 1).padStart(2, "0")}-${String(r[3].getDate()).padStart(2, "0")}` : r[3], lokasi: r[5], sumber: r[7], catatan: r[8], status_bayar: r[10], id: r[12], masuk: r[13] }))));
