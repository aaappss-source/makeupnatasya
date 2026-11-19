/* =========================================================
   Natasya Makeup — main.js
   Fitur: pilih look, portofolio, form booking ke WhatsApp, tombol WhatsApp
   melayang, bar booking di HP, header saat scroll.
   ========================================================= */

const CONFIG = {
  // SATU-SATUNYA tempat nomor WhatsApp. Semua link WA, teks nomor,
  // dan data SEO (JSON-LD) ikut nomor ini.
  // Format internasional: tanpa "+", tanpa 0 di depan.
  //
  // Nomor Natasya (sesuai brosur: 085171502605).
  waNumber: "6285171502605",

  // Pesan yang langsung terisi saat pengunjung menekan tombol WhatsApp di pojok kanan bawah.
  // Satu baris = satu teks di dalam tanda kutip. Spasi setelah titik dua sengaja dibiarkan
  // supaya pelanggan tinggal mengetik jawabannya.
  // Baris "" = baris kosong, supaya tiap pertanyaan berjarak dan mudah diisi.
  waChatText: [
    "Halo Kak Natasya, aku mau tanya-tanya dulu soal makeup ya 😊",
    "",
    "Nama: ",
    "",
    "Jenis makeup (wisuda/lamaran/akad/bridesmaid): ",
    "",
    "Tanggal acara: ",
    "",
    "Makeup harus selesai jam: ",
    "",
    "Jumlah orang: ",
    "",
    "Lokasi makeup (boleh langsung kirim share location): ",
    "",
    "Tahu Natasya dari (Instagram/TikTok/Google/teman/lainnya): ",
  ],

  // Foto & testimoni bisa diubah Natasya lewat Google Sheets.
  // spreadsheetId: kode di link spreadsheet, di antara /d/ dan /edit.
  // Spreadsheet harus dibagikan "Siapa saja yang memiliki link: Pelihat".
  // Kosong = semua foto tampil sebagai kotak putih.
  sheets: {
    spreadsheetId: "15qbmT3pzQlUKdb3AlZXk-Zf__gRcN40_OAGzR2qoAgk",
    tabs: {
      photos: "Foto Utama",
      portfolio: "Portofolio",
      testimonials: "Testimoni",
    },
    // Cadangan: kalau cara baca langsung diblokir Google, isi dengan link
    // "File > Bagikan > Publikasikan ke web" (format CSV) per tab.
    csvUrls: { photos: "", portfolio: "", testimonials: "" },
  },

  // Data form booking dicatat ke spreadsheet "Data Booking Natasya Makeup" (privat).
  // Isi dengan link Web App dari Apps Script (lihat PASANG-DATA-BOOKING.md).
  // Kosong = tidak dicatat, form tetap jalan seperti biasa.
  booking: {
    logUrl: "https://script.google.com/macros/s/AKfycbxLrt1tbnTBIFzOf-E9s-DMpJJgfDUQSThIRAhqe8iTxmQBoD-W3r6H9JCHlMSaUq4/exec",
  },

  business: {
    name: "Natasya Makeup",
    description: "MUA di Cimanggis, Depok untuk makeup wisuda, lamaran, akad, dan bridesmaid, termasuk hijab do.",
    city: "Cimanggis, Depok",
    region: "Jawa Barat",
    areaServed: ["Depok", "Jabodetabek"],
    instagram: [
      "https://www.instagram.com/natasyamlsyhdll/",
      "https://www.instagram.com/makeupnatasya/",
    ],
  },
};

// Jawaban "Tahu Natasya Makeup dari mana?" (value di form -> teks)
const SUMBER_NAMES = {
  whatsapp: "WhatsApp",
  instagram: "Instagram",
  tiktok: "TikTok",
  google: "Google",
  iklan: "Iklan",
  teman: "Dari teman",
  lainnya: "Lainnya",
};

/* Pilihan lokasi di form booking: kota/kabupaten Jabodetabek dan kecamatannya.
   Dicocokkan dengan UU No. 101, 102, 118 Tahun 2024 (Kab. Bekasi, Kab. Bogor, Kab. Tangerang)
   dan Perwal Kota Tangerang No. 24 Tahun 2018. Lokasi di luar daftar: pilihan "Kota lain". */
const LOKASI_MAKEUP = [
  ["Depok", ["Beji", "Bojongsari", "Cilodong", "Cimanggis", "Cinere", "Cipayung", "Limo", "Pancoran Mas", "Sawangan", "Sukmajaya", "Tapos"]],
  ["Jakarta Timur", ["Cakung", "Cipayung", "Ciracas", "Duren Sawit", "Jatinegara", "Kramat Jati", "Makasar", "Matraman", "Pasar Rebo", "Pulo Gadung"]],
  ["Jakarta Selatan", ["Cilandak", "Jagakarsa", "Kebayoran Baru", "Kebayoran Lama", "Mampang Prapatan", "Pancoran", "Pasar Minggu", "Pesanggrahan", "Setiabudi", "Tebet"]],
  ["Jakarta Pusat", ["Cempaka Putih", "Gambir", "Johar Baru", "Kemayoran", "Menteng", "Sawah Besar", "Senen", "Tanah Abang"]],
  ["Jakarta Barat", ["Cengkareng", "Grogol Petamburan", "Kalideres", "Kebon Jeruk", "Kembangan", "Palmerah", "Taman Sari", "Tambora"]],
  ["Jakarta Utara", ["Cilincing", "Kelapa Gading", "Koja", "Pademangan", "Penjaringan", "Tanjung Priok"]],
  ["Kota Bogor", ["Bogor Barat", "Bogor Selatan", "Bogor Tengah", "Bogor Timur", "Bogor Utara", "Tanah Sareal"]],
  ["Kab. Bogor", ["Babakan Madang", "Bojonggede", "Caringin", "Cariu", "Ciampea", "Ciawi", "Cibinong", "Cibungbulang", "Cigombong", "Cigudeg", "Cijeruk", "Cileungsi", "Ciomas", "Cisarua", "Ciseeng", "Citeureup", "Dramaga", "Gunung Putri", "Gunung Sindur", "Jasinga", "Jonggol", "Kemang", "Klapanunggal", "Leuwiliang", "Leuwisadeng", "Megamendung", "Nanggung", "Pamijahan", "Parung", "Parung Panjang", "Rancabungur", "Rumpin", "Sukajaya", "Sukamakmur", "Sukaraja", "Tajurhalang", "Tamansari", "Tanjungsari", "Tenjo", "Tenjolaya"]],
  ["Kota Bekasi", ["Bantargebang", "Bekasi Barat", "Bekasi Selatan", "Bekasi Timur", "Bekasi Utara", "Jatiasih", "Jatisampurna", "Medan Satria", "Mustika Jaya", "Pondok Gede", "Pondok Melati", "Rawalumbu"]],
  ["Kab. Bekasi", ["Babelan", "Bojongmangu", "Cabangbungin", "Cibarusah", "Cibitung", "Cikarang Barat", "Cikarang Pusat", "Cikarang Selatan", "Cikarang Timur", "Cikarang Utara", "Karang Bahagia", "Kedungwaringin", "Muara Gembong", "Pebayuran", "Serang Baru", "Setu", "Sukakarya", "Sukatani", "Sukawangi", "Tambelang", "Tambun Selatan", "Tambun Utara", "Tarumajaya"]],
  ["Tangerang Selatan", ["Ciputat", "Ciputat Timur", "Pamulang", "Pondok Aren", "Serpong", "Serpong Utara", "Setu"]],
  ["Kota Tangerang", ["Batuceper", "Benda", "Cibodas", "Ciledug", "Cipondoh", "Jatiuwung", "Karang Tengah", "Karawaci", "Larangan", "Neglasari", "Periuk", "Pinang", "Tangerang"]],
  ["Kab. Tangerang", ["Balaraja", "Cikupa", "Cisauk", "Cisoka", "Curug", "Gunung Kaler", "Jambe", "Jayanti", "Kelapa Dua", "Kemiri", "Kosambi", "Kresek", "Kronjo", "Legok", "Mauk", "Mekar Baru", "Pagedangan", "Pakuhaji", "Panongan", "Pasar Kemis", "Rajeg", "Sepatan", "Sepatan Timur", "Sindang Jaya", "Solear", "Sukadiri", "Sukamulya", "Teluknaga", "Tigaraksa"]],
];
const KOTA_LAIN = "lain";
const KECAMATAN = Object.fromEntries(LOKASI_MAKEUP);

const LOOK_NAMES = {
  wisuda: "Wisuda",
  lamaran: "Lamaran",
  akad: "Akad",
  bridesmaid: "Bridesmaid",
};

/* ---------- Pilih look (palet) ---------- */
/* ---------- "Lihat selengkapnya" di detail look (laptop/tablet) ---------- */
const LOOK_SIDE_BY_SIDE = window.matchMedia("(min-width: 761px)");

function closeLookInfo(detail) {
  const btn = detail.querySelector(".look-more");
  detail.classList.remove("is-open");
  if (btn) {
    btn.setAttribute("aria-expanded", "false");
    btn.textContent = "Lihat selengkapnya";
  }
  measureLookInfo(detail);
}

function measureLookInfo(detail) {
  const info = detail.querySelector(".look-info");
  const btn = detail.querySelector(".look-more");
  if (!info || !btn || detail.classList.contains("is-open")) return;
  const clipped = LOOK_SIDE_BY_SIDE.matches && info.scrollHeight > info.clientHeight + 2;
  detail.classList.toggle("is-clipped", clipped);
  btn.hidden = !clipped;
}

function initLookMore() {
  const details = document.querySelectorAll(".look-detail");
  const observer = "ResizeObserver" in window
    ? new ResizeObserver((entries) => entries.forEach((e) => measureLookInfo(e.target.closest(".look-detail"))))
    : null;
  details.forEach((detail) => {
    const info = detail.querySelector(".look-info");
    const btn = detail.querySelector(".look-more");
    if (!info || !btn) return;
    btn.addEventListener("click", () => {
      const open = !detail.classList.contains("is-open");
      if (!open) return closeLookInfo(detail);
      detail.classList.add("is-open");
      btn.setAttribute("aria-expanded", "true");
      btn.textContent = "Tampilkan lebih sedikit";
    });
    if (observer) observer.observe(info);
    measureLookInfo(detail);
  });
  LOOK_SIDE_BY_SIDE.addEventListener("change", () => details.forEach(closeLookInfo));
  if (document.fonts) document.fonts.ready.then(() => details.forEach((d) => measureLookInfo(d)));
}

function initLooks() {
  const pans = document.querySelectorAll(".pan");
  const details = document.querySelectorAll(".look-detail");
  if (!pans.length) return;

  pans.forEach((pan) => {
    pan.addEventListener("click", () => {
      const look = pan.dataset.look;
      pans.forEach((p) => p.setAttribute("aria-pressed", String(p === pan)));
      details.forEach((d) => {
        d.hidden = d.dataset.look !== look;
        if (d.hidden) closeLookInfo(d);
      });
    });
  });

  // Tombol "Booking makeup X" mengisi pilihan di form
  document.querySelectorAll("[data-book]").forEach((link) => {
    link.addEventListener("click", () => {
      const select = document.getElementById("f-look");
      if (select) {
        select.value = link.dataset.book;
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
  });
}

/* ---------- Tata letak palet yang selalu muat ---------- */
// Nama look tidak boleh terpotong. Mulai dari tata letak paling rapat yang cocok
// untuk lebar layar, lalu pindah ke yang lebih lega kalau ada nama yang tidak muat
// (misalnya di HP kecil atau saat ukuran huruf sistem diperbesar).
function initPanLayout() {
  const pans = document.querySelector(".pans");
  const compact = document.querySelector(".compact");
  if (!pans || !compact) return;

  const MODES = ["", "is-pills", "is-list"];
  const phone = window.matchMedia("(max-width: 480px)");
  const overflows = () => [...pans.querySelectorAll(".pan-name")]
    .some((n) => n.scrollWidth > n.clientWidth + 1);

  const fit = () => {
    let i = phone.matches ? 1 : 0;
    for (; i < MODES.length; i += 1) {
      pans.classList.remove(...MODES.filter(Boolean));
      if (MODES[i]) pans.classList.add(MODES[i]);
      if (!overflows()) break;
    }
  };

  let lastWidth = 0;
  const onResize = () => {
    const w = compact.clientWidth;
    if (w === lastWidth) return;
    lastWidth = w;
    fit();
  };

  if ("ResizeObserver" in window) new ResizeObserver(onResize).observe(compact);
  else window.addEventListener("resize", onResize);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
  onResize();
}

/* ---------- "Lihat lebih banyak" (galeri & testimoni) ---------- */
// Di layar <= 960px galeri jadi 2 kolom, jadi per halaman 6 foto (3 baris).
const SMALL_SCREEN = window.matchMedia("(max-width: 960px)");

function createPager({ list, button, itemSelector, perPage, isIncluded = () => true }) {
  let pages = 1;
  const size = () => (SMALL_SCREEN.matches ? perPage.small : perPage.large);

  function apply() {
    const items = [...list.querySelectorAll(itemSelector)];
    const included = items.filter(isIncluded);
    const limit = pages * size();
    items.forEach((el) => { if (!included.includes(el)) el.hidden = true; });
    included.forEach((el, i) => { el.hidden = i >= limit; });
    const remaining = Math.max(0, included.length - limit);
    // Tanpa angka sisa: foto dengan link rusak baru ketahuan saat dimuat,
    // jadi angkanya bisa meleset.
    button.hidden = remaining === 0;
  }

  button.addEventListener("click", () => { pages += 1; apply(); });
  SMALL_SCREEN.addEventListener("change", apply);
  return { apply, reset() { pages = 1; apply(); } };
}

/* ---------- Portofolio ---------- */
let galleryPager = null;

function initGallery() {
  const list = document.querySelector(".gallery");
  const button = document.getElementById("gallery-load");
  if (!list || !button) return;
  galleryPager = createPager({ list, button, itemSelector: ".shot", perPage: { large: 9, small: 6 } });
  galleryPager.apply();
}

/* ---------- Testimoni ---------- */
let testiPager = null;

function initTestimonials() {
  const list = document.querySelector(".bubbles");
  const button = document.getElementById("testi-load");
  if (!list || !button) return;
  testiPager = createPager({ list, button, itemSelector: ":scope > .bubble", perPage: { large: 6, small: 4 } });
  testiPager.apply();
}

// Screenshot chat dianggap panjang kalau 20% lebih tinggi dari batas.
function markTall(img) {
  const fig = img.closest(".bubble-shot");
  if (!fig || fig.classList.contains("is-open")) return;
  const cap = parseFloat(getComputedStyle(fig).getPropertyValue("--shot-max")) || 420;
  fig.classList.toggle("is-tall", img.offsetHeight > cap * 1.2);
}

const tallObserver = "ResizeObserver" in window
  ? new ResizeObserver((entries) => entries.forEach((e) => markTall(e.target)))
  : null;

function toggleShot(fig, toggle) {
  const open = !fig.classList.contains("is-open");
  fig.classList.toggle("is-open", open);
  toggle.setAttribute("aria-expanded", String(open));
  toggle.textContent = open ? "Tutup" : "Lihat chat lengkap";
  if (!open && fig.getBoundingClientRect().top < 0) fig.scrollIntoView({ block: "start" });
}

/* ---------- Isi dari Google Sheets (portofolio & testimoni) ---------- */
// Parser CSV kecil: mendukung tanda kutip, koma, dan baris baru di dalam sel.
function parseCsv(text) {
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') quoted = false;
      else cell += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") { row.push(cell); cell = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cell); cell = "";
      rows.push(row); row = [];
    } else cell += c;
  }
  if (cell !== "" || row.length) { row.push(cell); rows.push(row); }
  return rows;
}

function csvToObjects(text) {
  const rows = parseCsv(text.replace(/^\uFEFF/, ""));
  if (rows.length < 2) return [];
  const head = rows[0].map((h) => h.trim().toLowerCase());
  return rows.slice(1)
    .filter((r) => r.some((v) => v.trim() !== ""))
    .map((r) => Object.fromEntries(head.map((h, i) => [h, (r[i] || "").trim()])));
}

async function fetchRows(url) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 7000);
  try {
    const res = await fetch(url, { signal: ctrl.signal });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const text = await res.text();
    if (/^\s*</.test(text)) throw new Error("Bukan CSV");
    return csvToObjects(text);
  } finally {
    clearTimeout(timer);
  }
}

// Link foto dari Google Drive (atau link https lain) -> alamat gambar yang bisa dipakai <img>.
function imageUrl(raw, width) {
  const v = (raw || "").trim();
  if (!v) return null;
  if (/^https:\/\/(drive|docs)\.google\.com\//.test(v)) {
    const m = v.match(/\/d\/([\w-]{10,})/) || v.match(/[?&]id=([\w-]{10,})/);
    return m ? `https://drive.google.com/thumbnail?id=${m[1]}&sz=w${width}` : null;
  }
  return /^https:\/\//.test(v) ? v : null;
}

function isHidden(row) {
  return /^(tidak|no|false|0|sembunyi)/i.test((row.tampil || "").trim());
}

function renderGallery(rows) {
  const list = document.querySelector(".gallery");
  if (!list) return;
  const items = [];
  rows.forEach((row) => {
    if (isHidden(row)) return;
    const src = imageUrl(row.foto, 900);
    if (!src) return;
    const caption = (row.keterangan || "").trim();

    const li = document.createElement("li");
    li.className = "shot";
    const fig = document.createElement("figure");
    const img = document.createElement("img");
    img.src = src;
    img.alt = caption || "Hasil makeup Natasya";
    img.width = 800;
    img.height = 1000;
    img.loading = "lazy";
    img.decoding = "async";
    img.referrerPolicy = "no-referrer";
    img.addEventListener("error", () => {
      li.remove();
      if (galleryPager) galleryPager.apply();
    });
    fig.append(img);
    if (caption) {
      const cap = document.createElement("figcaption");
      cap.textContent = caption;
      fig.append(cap);
    }
    li.append(fig);
    items.push(li);
  });
  if (!items.length) return;
  list.replaceChildren(...items);
  if (galleryPager) galleryPager.reset();
}

function renderTestimonials(rows) {
  const box = document.querySelector(".bubbles");
  if (!box) return;
  const items = [];
  rows.forEach((row) => {
    if (isHidden(row)) return;
    const src = imageUrl(row.foto, 900);
    if (src) {
      const fig = document.createElement("figure");
      fig.className = "bubble bubble-shot";
      const clip = document.createElement("div");
      clip.className = "shot-clip";
      const img = document.createElement("img");
      img.src = src;
      img.alt = row.nama ? `Chat testimoni dari ${row.nama}` : "Chat testimoni dari klien";
      img.loading = "lazy";
      img.decoding = "async";
      img.referrerPolicy = "no-referrer";
      img.addEventListener("error", () => {
        fig.remove();
        if (testiPager) testiPager.apply();
      });
      clip.append(img);
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "btn-text shot-toggle";
      toggle.textContent = "Lihat chat lengkap";
      toggle.setAttribute("aria-expanded", "false");
      toggle.addEventListener("click", () => toggleShot(fig, toggle));
      clip.addEventListener("click", () => {
        if (fig.classList.contains("is-tall")) toggleShot(fig, toggle);
      });
      fig.append(clip, toggle);
      if (row.nama) {
        const cap = document.createElement("figcaption");
        cap.textContent = row.nama;
        fig.append(cap);
      }
      if (tallObserver) tallObserver.observe(img);
      items.push(fig);
    } else if (row.teks) {
      const bq = document.createElement("blockquote");
      bq.className = "bubble";
      const p = document.createElement("p");
      p.textContent = row.teks;
      bq.append(p);
      if (row.nama) {
        const cite = document.createElement("cite");
        cite.textContent = row.nama;
        bq.append(cite);
      }
      items.push(bq);
    }
  });
  if (!items.length) return;
  box.replaceChildren(...items);
  if (testiPager) testiPager.reset();
}

/* Foto tetap: hero, foto Natasya di Tentang, dan foto tiap look. */
const PHOTO_SLOTS = {
  hero: { selector: ".hero-mirror img", alt: "Natasya, makeup artist Natasya Makeup", width: 800 },
  tentang: { selector: ".about-photo", alt: "Natasya, MUA di Depok", width: 900 },
};
Object.keys(LOOK_NAMES).forEach((key) => {
  PHOTO_SLOTS[`look-${key}`] = {
    selector: `.look-detail[data-look="${key}"] .look-photo img`,
    alt: `Contoh makeup ${LOOK_NAMES[key].toLowerCase()}`,
    width: 1000,
  };
});

// Gambar transparen 1x1: kotak foto tampil putih selama belum ada foto.
const EMPTY_IMAGE = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";

// Pasang foto dari Sheets. Kalau gagal dimuat, kembali jadi kotak putih.
// Kalau kotaknya sudah berisi foto bawaan (hero), foto baru diunduh dulu di belakang
// dan baru ditukar setelah siap, jadi tidak ada kedipan putih. Gagal = foto bawaan tetap.
function setPhoto(img, src, alt) {
  if (!img.classList.contains("is-empty")) {
    const pre = new Image();
    pre.referrerPolicy = "no-referrer";
    pre.addEventListener("load", () => {
      img.referrerPolicy = "no-referrer";
      img.src = src;
      img.alt = alt;
    }, { once: true });
    pre.src = src;
    return;
  }
  img.referrerPolicy = "no-referrer";
  img.addEventListener("load", () => {
    if (img.getAttribute("src") !== EMPTY_IMAGE) img.classList.remove("is-empty");
  }, { once: true });
  img.addEventListener("error", () => {
    img.src = EMPTY_IMAGE;
    img.alt = "";
    img.classList.add("is-empty");
  }, { once: true });
  img.src = src;
  img.alt = alt;
}

function renderPhotos(rows) {
  rows.forEach((row) => {
    const slot = PHOTO_SLOTS[(row.bagian || "").trim().toLowerCase()];
    if (!slot) return;
    const img = document.querySelector(slot.selector);
    const src = imageUrl(row.foto, slot.width);
    // Foto di Sheets sama dengan foto bawaan: tidak perlu diunduh ulang dari Drive.
    if (img && img.dataset.driveId && (row.foto || "").includes(img.dataset.driveId)) return;
    if (img && src) setPhoto(img, src, slot.alt);
  });
}

function sheetUrl(key) {
  const s = CONFIG.sheets;
  if (s.csvUrls && s.csvUrls[key]) return s.csvUrls[key];
  if (!s.spreadsheetId) return "";
  return `https://docs.google.com/spreadsheets/d/${encodeURIComponent(s.spreadsheetId)}` +
    `/gviz/tq?tqx=out:csv&headers=1&sheet=${encodeURIComponent(s.tabs[key])}`;
}

// Foto yang belum diisi di Sheets (atau kalau Sheets gagal dimuat) tampil sebagai
// kotak putih. Testimoni teks bawaan di index.html tetap tampil.
function initSheets() {
  const photos = sheetUrl("photos");
  const portfolio = sheetUrl("portfolio");
  const testimonials = sheetUrl("testimonials");
  if (photos) fetchRows(photos).then(renderPhotos).catch(() => {});
  if (portfolio) fetchRows(portfolio).then(renderGallery).catch(() => {});
  if (testimonials) fetchRows(testimonials).then(renderTestimonials).catch(() => {});
}

/* ---------- Form booking ke WhatsApp ---------- */
function todayISO() {
  const d = new Date();
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 10);
}

function formatTanggal(iso) {
  if (!iso) return "";
  const [y, m, d] = iso.split("-").map(Number);
  return new Intl.DateTimeFormat("id-ID", {
    weekday: "long", day: "numeric", month: "long", year: "numeric",
  }).format(new Date(y, m - 1, d));
}

function buildMessage(data) {
  const lines = [
    "Halo Kak Natasya, aku mau booking makeup.",
    "",
    `Nama: ${data.nama}`,
    `Jenis makeup: ${LOOK_NAMES[data.look] || data.look}`,
    `Tanggal acara: ${formatTanggal(data.tanggal)}`,
  ];
  if (data.jam) lines.push(`Makeup selesai jam: ${data.jam}`);
  lines.push(`Lokasi: ${data.lokasi}`);
  lines.push(`Jumlah orang: ${data.jumlah}`);
  if (data.sumber) lines.push(`Tahu Natasya Makeup dari: ${SUMBER_NAMES[data.sumber] || data.sumber}`);
  if (data.catatan) lines.push(`Catatan: ${data.catatan}`);
  lines.push("", "Apakah jadwalnya masih tersedia?");
  return lines.join("\n");
}

function waUrl(text) {
  return `https://wa.me/${CONFIG.waNumber}?text=${encodeURIComponent(text)}`;
}

function initBookingForm() {
  const form = document.getElementById("booking-form");
  const sendLink = document.getElementById("wa-send");
  if (!form || !sendLink) return;

  const fields = {
    nama: form.elements.nama,
    look: form.elements.look,
    tanggal: form.elements.tanggal,
    jam: form.elements.jam,
    kota: form.elements.kota,
    kecamatan: form.elements.kecamatan,
    lokasiLain: form.elements.lokasi_lain,
    jumlah: form.elements.jumlah,
    sumber: form.elements.sumber,
    catatan: form.elements.catatan,
  };

  fields.tanggal.min = todayISO();

  // Lokasi: pilih kota, lalu kecamatan. "Kota lain" mengganti kotak kecamatan dengan kolom ketik.
  LOKASI_MAKEUP.forEach(([kota]) => fields.kota.add(new Option(kota, kota)));
  fields.kota.add(new Option("Kota lain", KOTA_LAIN));
  const lokasiError = document.getElementById("e-lokasi");
  const isiKecamatan = () => {
    const kota = fields.kota.value;
    const lain = kota === KOTA_LAIN;
    const daftar = KECAMATAN[kota] || [];
    fields.kecamatan.replaceChildren(new Option("Kecamatan", ""));
    daftar.forEach((k) => fields.kecamatan.add(new Option(k, k)));
    fields.kecamatan.disabled = !daftar.length;
    fields.kecamatan.hidden = lain;
    fields.lokasiLain.hidden = !lain;
    if (!lain) fields.lokasiLain.value = "";
  };
  isiKecamatan();

  // Satu isian form = satu ID. Kirim ulang (misal setelah ganti tanggal) memperbarui
  // baris yang sama di spreadsheet; ID baru setelah form dikosongkan.
  const newId = () => (window.crypto && crypto.randomUUID
    ? crypto.randomUUID()
    : Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 12));
  let bookingId = newId();

  // Catat ke spreadsheet saat tombol kirim ditekan, walaupun pesan WA tidak jadi dikirim.
  // sendBeacon tetap terkirim meski halaman berpindah ke WhatsApp.
  const logBooking = (v) => {
    const url = CONFIG.booking && CONFIG.booking.logUrl;
    if (!url) return;
    const trap = form.elements.website;
    const body = JSON.stringify({
      id: bookingId,
      nama: v.nama,
      look: LOOK_NAMES[v.look] || v.look,
      tanggal: v.tanggal,
      jam: v.jam,
      lokasi: v.lokasi,
      jumlah: v.jumlah,
      sumber: SUMBER_NAMES[v.sumber] || v.sumber,
      catatan: v.catatan,
      website: trap ? trap.value : "",
    });
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(url, new Blob([body], { type: "text/plain;charset=utf-8" }))) return;
    } catch (_) { /* lanjut ke fetch */ }
    fetch(url, { method: "POST", mode: "no-cors", keepalive: true, body, headers: { "Content-Type": "text/plain;charset=utf-8" } })
      .catch(() => {});
  };

  const read = () => ({
    nama: fields.nama.value.trim(),
    look: fields.look.value,
    tanggal: fields.tanggal.value,
    jam: fields.jam.value,
    kota: fields.kota.value,
    kecamatan: fields.kecamatan.value,
    lokasi: fields.kota.value === KOTA_LAIN
      ? fields.lokasiLain.value.trim()
      : (fields.kota.value && fields.kecamatan.value ? `${fields.kecamatan.value}, ${fields.kota.value}` : ""),
    jumlah: fields.jumlah.value,
    sumber: fields.sumber.value,
    catatan: fields.catatan.value.trim(),
  });

  const rules = {
    nama: (v) => v.nama.length > 0,
    look: (v) => v.look in LOOK_NAMES,
    tanggal: (v) => v.tanggal !== "" && v.tanggal >= todayISO(),
    lokasi: (v) => (v.kota === KOTA_LAIN
      ? v.lokasi.length > 0
      : (KECAMATAN[v.kota] || []).includes(v.kecamatan)),
    jumlah: (v) => Number(v.jumlah) >= 1,
    sumber: (v) => v.sumber in SUMBER_NAMES,
  };

  // Kolom yang ditandai salah untuk lokasi: kota dulu, lalu kecamatan / kolom ketik.
  const lokasiTarget = () => {
    if (!fields.kota.value) return fields.kota;
    return fields.kota.value === KOTA_LAIN ? fields.lokasiLain : fields.kecamatan;
  };
  const targetOf = (name) => (name === "lokasi" ? lokasiTarget() : fields[name]);
  const ruleOf = (inputName) => ({ kota: "lokasi", kecamatan: "lokasi", lokasi_lain: "lokasi" }[inputName] || inputName);

  const setError = (name, show) => {
    const input = targetOf(name);
    if (name === "lokasi") {
      [fields.kota, fields.kecamatan, fields.lokasiLain].forEach((el) => {
        el.removeAttribute("aria-invalid");
        el.removeAttribute("aria-describedby");
      });
    }
    const msg = document.getElementById(`e-${name}`);
    input.setAttribute("aria-invalid", String(show));
    if (msg) {
      msg.hidden = !show;
      if (show) input.setAttribute("aria-describedby", msg.id);
      else input.removeAttribute("aria-describedby");
    }
  };

  const validate = () => {
    const values = read();
    let firstInvalid = null;
    Object.keys(rules).forEach((name) => {
      const ok = rules[name](values);
      setError(name, !ok);
      if (!ok && !firstInvalid) firstInvalid = targetOf(name);
    });
    return firstInvalid;
  };

  // Link selalu berisi pesan terbaru, jadi klik biasa langsung membuka WA.
  // Sekalian tulis lokasi lengkap di bawah dropdown (tampil di HP saja, lewat CSS).
  const lokasiLengkap = document.getElementById("lokasi-lengkap");
  const syncLink = () => {
    const v = read();
    sendLink.href = waUrl(buildMessage(v));
    if (lokasiLengkap) lokasiLengkap.textContent = v.kota && v.kota !== KOTA_LAIN && v.lokasi ? `Lokasi: ${v.lokasi}` : "";
  };

  form.addEventListener("input", (e) => {
    syncLink();
    const statusEl = document.getElementById("form-status");
    if (statusEl) statusEl.textContent = "";
    const name = ruleOf(e.target.name);
    if (rules[name] && (e.target.getAttribute("aria-invalid") === "true" || (name === "lokasi" && !lokasiError.hidden))) {
      setError(name, !rules[name](read()));
    }
  });
  fields.kota.addEventListener("change", () => {
    isiKecamatan();
    if (!lokasiError.hidden) setError("lokasi", !rules.lokasi(read()));
    if (fields.kota.value === KOTA_LAIN) fields.lokasiLain.focus();
  });
  form.addEventListener("change", syncLink);

  sendLink.addEventListener("click", (e) => {
    syncLink();
    const firstInvalid = validate();
    if (firstInvalid) {
      e.preventDefault();
      firstInvalid.focus();
      return;
    }
    logBooking(read());
  });

  // Tombol "Kosongkan form": nilai kembali ke default, error & link ikut bersih
  const status = document.getElementById("form-status");
  form.addEventListener("reset", () => {
    // tunggu browser selesai mengembalikan nilai default dulu
    setTimeout(() => {
      bookingId = newId();
      isiKecamatan();
      Object.keys(rules).forEach((name) => setError(name, false));
      syncLink();
      fields.nama.focus();
      if (status) status.textContent = "Form sudah dikosongkan.";
    }, 0);
  });

  // Tekan Enter di kolom isian = sama dengan tombol kirim. (Browser tidak mengirim form
  // ini lewat Enter dengan sendirinya karena tidak ada tombol submit.)
  form.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.isComposing && e.target.matches("input:not([type=checkbox]):not([type=radio])")) {
      e.preventDefault();
      sendLink.click();
    }
  });
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    sendLink.click();
  });

  syncLink();
}

/* ---------- Nomor WhatsApp dari CONFIG ---------- */
// 62895396797368 -> 0895-3967-97368
function formatWaDisplay(intl) {
  const local = `0${intl.replace(/^62/, "")}`;
  return `${local.slice(0, 4)}-${local.slice(4, 8)}-${local.slice(8)}`;
}

function initWaLinks() {
  document.querySelectorAll("[data-wa]").forEach((link) => {
    link.href = `https://wa.me/${CONFIG.waNumber}`;
    link.target = "_blank";
    link.rel = "noopener";
  });
  document.querySelectorAll("[data-wa-display]").forEach((el) => {
    el.textContent = formatWaDisplay(CONFIG.waNumber);
  });
}

// Data terstruktur untuk Google, dibuat dari CONFIG supaya nomornya tidak dobel
function injectStructuredData() {
  const b = CONFIG.business;
  const data = {
    "@context": "https://schema.org",
    "@type": "HealthAndBeautyBusiness",
    name: b.name,
    description: b.description,
    telephone: `+${CONFIG.waNumber}`,
    address: { "@type": "PostalAddress", addressLocality: b.city, addressRegion: b.region, addressCountry: "ID" },
    areaServed: b.areaServed,
    sameAs: b.instagram,
  };
  const script = document.createElement("script");
  script.type = "application/ld+json";
  script.textContent = JSON.stringify(data);
  document.head.appendChild(script);
}

/* ---------- Header & bar booking ---------- */
function initScrollUI() {
  const header = document.querySelector(".site-header");
  const bar = document.getElementById("booking-bar");
  const hero = document.getElementById("hero");
  const booking = document.getElementById("booking");

  const onScroll = () => {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 8);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (!bar || !hero || !booking || !("IntersectionObserver" in window)) return;

  const state = { hero: true, booking: false };
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.target === hero) state.hero = entry.isIntersecting;
      if (entry.target === booking) state.booking = entry.isIntersecting;
    });
    bar.classList.toggle("is-visible", !state.hero && !state.booking);
  }, { threshold: 0 });
  io.observe(hero);
  io.observe(booking);
}

/* ---------- Tombol WhatsApp melayang ---------- */
// Langsung membuka chat Natasya dengan draf pesan dari CONFIG.waChatText.
function initWaFloat() {
  const btn = document.getElementById("wa-float");
  if (!btn) return;
  btn.href = waUrl(CONFIG.waChatText.join("\n"));
  btn.target = "_blank";
  btn.rel = "noopener";

  // Di HP tombol disembunyikan selama kolom form diketik, supaya tidak menutupi
  // isian yang sedang diisi di atas keyboard.
  const isField = (el) => el instanceof Element && el.matches("input, select, textarea");
  const root = document.documentElement;
  document.addEventListener("focusin", (e) => { if (isField(e.target)) root.classList.add("is-typing"); });
  document.addEventListener("focusout", (e) => { if (isField(e.target)) root.classList.remove("is-typing"); });
}

/* ---------- Jalankan ---------- */
document.documentElement.classList.add("js");

document.addEventListener("DOMContentLoaded", () => {
  initPanLayout();
  initWaLinks();
  initWaFloat();
  injectStructuredData();
  initLooks();
  initLookMore();
  initGallery();
  initTestimonials();
  initSheets();
  initBookingForm();
  initScrollUI();
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
});
