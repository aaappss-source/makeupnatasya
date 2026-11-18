// Tes logika Apps Script dengan tiruan SpreadsheetApp/CacheService/LockService (Node).
const fs = require("fs"); const vm = require("vm");
const src = fs.readFileSync(process.argv[2] || require("path").join(__dirname, "..", "apps-script", "data-booking.gs"), "utf8");
let results = []; const check = (n, c, i = "") => results.push([n, !!c, i]);
function makeEnv(maxRows = 40) {
  // Tiruan tab Booking: 13 kolom (A-I data, J Status dari rumus, K Status pembayaran, L Keterangan, M ID).
  // Kolom J diisi "" sampai bawah seperti keluaran ARRAYFORMULA, jadi getLastRow() sengaja menunjuk baris paling bawah.
  const header = ["Waktu isi form","Nama","Jenis makeup","Tanggal acara","Makeup selesai jam","Lokasi","Jumlah orang","Tahu dari","Catatan","Status","Status pembayaran","Keterangan","ID (jangan diubah)","Masuk lewat"];
  const blank = () => Array(14).fill("");
  const rows = [header]; for (let i = 1; i < maxRows; i++) rows.push(blank());
  const cacheStore = {}; const formats = {};
  const sheet = {
    getLastRow: () => rows.length,
    getMaxRows: () => rows.length,
    getMaxColumns: () => 14,
    insertRowsAfter: (after, n) => { for (let i = 0; i < n; i++) rows.splice(after, 0, blank()); },
    getRange: (r, c, nr = 1, nc = 1) => ({
      getValues: () => rows.slice(r - 1, r - 1 + nr).map(row => row.slice(c - 1, c - 1 + nc)),
      setValues: (vals) => vals.forEach((v, i) => { const row = rows[r - 1 + i]; v.forEach((x, j) => row[c - 1 + j] = x); }),
      setValue: (x) => { rows[r - 1][c - 1] = x; },
      setNumberFormat: (f) => { formats[r + ":" + c] = f; },
    }),
    appendRow: () => { throw new Error("appendRow tidak boleh dipakai (rumus Status bikin baris baru jatuh di paling bawah)"); },
  };
  const ctx = {
    console, Date, JSON, String, Number, Math,
    SpreadsheetApp: { getActive: () => ({ getSheetByName: (n) => n === "Booking" ? sheet : null, getSpreadsheetTimeZone: () => "Asia/Jakarta" }) },
    CacheService: { getScriptCache: () => ({ get: k => cacheStore[k] ?? null, put: (k, v) => { cacheStore[k] = v; } }) },
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    Utilities: { formatDate: (d, tz, f) => f === "yyyy-MM-dd" ? "2027-03-20" : "202611170400", parseDate: (s) => { const [y, m, d] = s.slice(0, 10).split("-").map(Number); return new Date(y, m - 1, d, 12); } },
    ContentService: { createTextOutput: (t) => ({ text: t }) },
  };
  vm.createContext(ctx); vm.runInContext(src, ctx);
  const data = () => rows.slice(1).filter(r => r[0] !== "");
  const last = () => data()[data().length - 1];
  return { ctx, rows, formats, data, last };
}
const base = { id: "abc12345-0001", nama: "Rina", look: "Wisuda", tanggal: "2027-03-20", jam: "07:30", lokasi: "Cimanggis, Depok", jumlah: "3", sumber: "Instagram", catatan: "Hijab", website: "" };
let { ctx, rows, formats, data, last } = makeEnv();
check("data valid -> baris baru", ctx.simpanBooking_({ ...base }) === "baru" && data().length === 1 && rows[1] === data()[0]);
const r = rows[1];
check("isi kolom benar (nama, jenis, tanggal, jam, lokasi, jumlah, tahu dari, catatan)", r[1] === "Rina" && r[2] === "Wisuda" && r[3] instanceof Date && r[3].getFullYear() === 2027 && r[3].getMonth() === 2 && r[3].getDate() === 20 && r[4] === "07:30" && r[5] === "Cimanggis, Depok" && r[6] === 3 && r[7] === "Instagram" && r[8] === "Hijab", r);
check("baris baru: Status (J) tidak ditulis skrip, Status pembayaran (K) = Masih nanya-nanya, Keterangan (L) kosong, ID di M, Masuk lewat (N) = Website", r.length === 14 && r[9] === "" && r[10] === "Masih nanya-nanya" && r[11] === "" && r[12] === base.id && r[13] === "Website", r.slice(9));
check("format baris baru: waktu dd/mm/yyyy hh:mm, tanggal dengan nama hari, jam hh:mm", formats["2:1"] === "dd/mm/yyyy hh:mm" && formats["2:4"] === "dddd, d mmmm yyyy" && formats["2:5"] === "hh:mm", formats);
for (const k in formats) delete formats[k];
rows[1][10] = "Sudah DP"; rows[1][11] = "DP Rp200.000";
check("kirim ulang ID sama -> diperbarui, tidak dobel", ctx.simpanBooking_({ ...base, tanggal: "2027-03-21", catatan: "ganti tanggal" }) === "diperbarui" && data().length === 1);
check("format ikut dirapikan saat baris diperbarui", formats["2:4"] === "dddd, d mmmm yyyy", formats);
check("kirim ulang: Status pembayaran & Keterangan yang diisi manual tetap, J tetap kosong", rows[1][9] === "" && rows[1][10] === "Sudah DP" && rows[1][11] === "DP Rp200.000" && rows[1][8] === "ganti tanggal" && rows[1][3].getDate() === 21, rows[1]);
check("ID beda -> baris baru", ctx.simpanBooking_({ ...base, id: "abc12345-0002" }) === "baru" && data().length === 2 && rows[2][12] === "abc12345-0002");
check("kolom jebakan bot terisi -> diabaikan", ctx.simpanBooking_({ ...base, id: "bot12345", website: "http://spam" }) === "abaikan" && data().length === 2);
for (const [label, bad] of [["nama kosong", { nama: "  " }], ["tanggal salah format", { tanggal: "20/03/2027" }], ["jumlah 0", { jumlah: 0 }], ["ID aneh", { id: "<script>" }], ["lokasi kosong", { lokasi: "" }]])
  check(`data tidak valid (${label}) -> diabaikan`, ctx.simpanBooking_({ ...base, id: "x1234567-" + label.length, ...bad }) === "abaikan");
check("rumus di isian dinetralkan", ctx.simpanBooking_({ ...base, id: "rumus1234", nama: "=HYPERLINK(\"http://x\")", catatan: "+62 812" }) === "baru" && last()[1].startsWith("'=") && last()[8].startsWith("'+"), last());
check("teks kepanjangan dipotong (catatan maks 500)", ctx.simpanBooking_({ ...base, id: "panjang12", catatan: "a".repeat(2000) }) === "baru" && last()[8].length === 500);
check("JSON rusak tidak bikin error (doPost tetap balas ok)", ctx.doPost({ postData: { contents: "{rusak" } }).text === "ok");
check("doPost menyimpan dari JSON", ctx.doPost({ postData: { contents: JSON.stringify({ ...base, id: "post12345" }) } }).text === "ok" && last()[12] === "post12345");
({ ctx, rows, data, last } = makeEnv());
let ok = 0; for (let i = 0; i < 25; i++) if (ctx.simpanBooking_({ ...base, id: "spam0000-" + i }) === "baru") ok++;
check("batas spam: maks 20 kiriman per menit", ok === 20 && data().length === 20, ok);
check("fungsi tesSimpan ada untuk cek dari editor", typeof ctx.tesSimpan === "function");
({ ctx, rows, data, last } = makeEnv());
const old = { ...base, id: "lama12345" }; delete old.sumber;
check("kiriman dari website versi lama (tanpa 'tahu dari') tetap diterima, kolom H kosong", ctx.simpanBooking_(old) === "baru" && rows[1][7] === "" && rows[1][8] === "Hijab", rows[1]);
({ ctx, rows, data, last } = makeEnv(3));
ctx.simpanBooking_({ ...base, id: "penuh0001" }); ctx.simpanBooking_({ ...base, id: "penuh0002" }); ctx.simpanBooking_({ ...base, id: "penuh0003" });
check("tab penuh -> baris otomatis ditambah, data tetap urut", data().length === 3 && rows[3][12] === "penuh0003" && rows.length > 3, rows.length);
({ ctx, rows, data, last } = makeEnv());
rows[1][0] = new Date(); rows[1][1] = "Lama"; rows[1][12] = "lama00001"; rows[2][0] = new Date(); rows[2][1] = "Lama 2"; rows[2][12] = "lama00002";
check("baris baru masuk tepat di bawah data terakhir (bukan di paling bawah tab)", ctx.simpanBooking_({ ...base, id: "baru00001" }) === "baru" && rows[3][12] === "baru00001");
// Baris yang diketik manual: tanpa ID, kolom A kadang lupa diisi
({ ctx, rows, data, last } = makeEnv());
rows[1][0] = new Date(); rows[1][1] = "Web lama"; rows[1][12] = "web00001"; rows[1][13] = "Website";
rows[2][1] = "Manual tanpa waktu"; rows[2][2] = "Akad"; rows[2][10] = "Sudah DP"; rows[2][13] = "Manual"; rows[2][9] = "Follow Up";
rows[3][9] = "";   // J berisi keluaran rumus kosong
check("baris manual yang kolom A-nya kosong tidak tertimpa booking baru", ctx.simpanBooking_({ ...base, id: "baru00002" }) === "baru" && rows[2][1] === "Manual tanpa waktu" && rows[2][10] === "Sudah DP" && rows[3][12] === "baru00002" && rows[3][13] === "Website", rows.slice(1, 5).map(r => [r[1], r[12], r[13]]));
rows[5][9] = "Pending";  // sisa nilai di kolom J saja tidak dianggap data
check("nilai di kolom J (rumus) saja tidak dianggap baris terisi", ctx.simpanBooking_({ ...base, id: "baru00003" }) === "baru" && rows[4][12] === "baru00003", rows.slice(1, 7).map(r => [r[1], r[12]]));
check("baris manual tanpa ID tidak ikut diperbarui saat ID website dikirim ulang", ctx.simpanBooking_({ ...base, id: "baru00002", catatan: "ubah" }) === "diperbarui" && rows[3][8] === "ubah" && rows[2][8] === "");
const bad = results.filter(r => !r[1]);
results.forEach(([n, ok, i]) => console.log((ok ? "PASS " : "FAIL ") + n + (ok ? "" : "  -> " + JSON.stringify(i))));
console.log(`\n${results.length - bad.length}/${results.length} lulus`); process.exit(bad.length ? 1 : 0);
