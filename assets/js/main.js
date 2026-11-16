/* =========================================================
   Natasya Makeup — main.js
   Fitur: pilih look, filter portofolio, form booking ke WhatsApp,
   bar booking di HP, header saat scroll.
   ========================================================= */

const CONFIG = {
  // SATU-SATUNYA tempat nomor WhatsApp. Semua link WA, teks nomor,
  // dan data SEO (JSON-LD) ikut nomor ini.
  // Format internasional: tanpa "+", tanpa 0 di depan.
  //
  // SEMENTARA: nomor tes milik developer.
  // Sebelum online, kembalikan ke nomor Natasya: "6285171502605"
  waNumber: "62895396797368",

  // Isi portofolio & testimoni bisa diubah Natasya lewat Google Sheets.
  // Isi dengan link "Publikasikan ke web" format CSV (lihat PANDUAN-NATASYA.md).
  // Kosong = website memakai isi bawaan di index.html.
  sheets: {
    portfolioCsv: "",
    testimonialsCsv: "",
  },

  business: {
    name: "Natasya Makeup",
    description: "MUA bersertifikat di Depok untuk wisuda, lamaran, akad, bridesmaid, tari, photoshoot, dan makeup fantasi.",
    city: "Depok",
    region: "Jawa Barat",
    areaServed: ["Depok", "Jabodetabek"],
    instagram: [
      "https://www.instagram.com/natasyamlsyhdll/",
      "https://www.instagram.com/makeupnatasya/",
    ],
  },
};

const LOOK_NAMES = {
  wisuda: "Wisuda",
  lamaran: "Lamaran",
  akad: "Akad",
  bridesmaid: "Bridesmaid",
  photoshoot: "Photoshoot & model",
  tari: "Tari",
  reguler: "Reguler",
  fantasi: "Fantasi",
};

/* ---------- Pilih look (palet) ---------- */
function initLooks() {
  const pans = document.querySelectorAll(".pan");
  const details = document.querySelectorAll(".look-detail");
  if (!pans.length) return;

  pans.forEach((pan) => {
    pan.addEventListener("click", () => {
      const look = pan.dataset.look;
      pans.forEach((p) => p.setAttribute("aria-pressed", String(p === pan)));
      details.forEach((d) => { d.hidden = d.dataset.look !== look; });
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

/* ---------- Filter portofolio ---------- */
function applyGalleryFilter() {
  const active = document.querySelector('.chip[aria-pressed="true"]');
  const filter = active ? active.dataset.filter : "semua";
  document.querySelectorAll(".shot").forEach((shot) => {
    shot.hidden = filter !== "semua" && shot.dataset.category !== filter;
  });
}

function initGalleryFilter() {
  const chips = document.querySelectorAll(".chip");
  if (!chips.length) return;

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
      applyGalleryFilter();
    });
  });
}

/* ---------- Isi dari Google Sheets (portofolio & testimoni) ---------- */
const GALLERY_CATEGORIES = ["wisuda", "lamaran", "bridesmaid", "tari", "lainnya"];
const CATEGORY_ALIASES = {
  akad: "lamaran",
  "lamaran & akad": "lamaran",
  "lamaran dan akad": "lamaran",
  fantasi: "tari",
  "tari & fantasi": "tari",
  photoshoot: "lainnya",
  reguler: "lainnya",
  regular: "lainnya",
};
const CATEGORY_LABELS = {
  wisuda: "Wisuda",
  lamaran: "Lamaran & akad",
  bridesmaid: "Bridesmaid",
  tari: "Tari & fantasi",
  lainnya: "Lainnya",
};

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
    return csvToObjects(await res.text());
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

function normalizeCategory(raw) {
  const k = (raw || "").trim().toLowerCase();
  if (GALLERY_CATEGORIES.includes(k)) return k;
  return CATEGORY_ALIASES[k] || "lainnya";
}

function renderGallery(rows) {
  const list = document.querySelector(".gallery");
  if (!list) return;
  const items = [];
  rows.forEach((row) => {
    if (isHidden(row)) return;
    const src = imageUrl(row.foto, 900);
    if (!src) return;
    const category = normalizeCategory(row.kategori);
    const caption = row.keterangan || CATEGORY_LABELS[category];

    const li = document.createElement("li");
    li.className = "shot";
    li.dataset.category = category;
    const fig = document.createElement("figure");
    const img = document.createElement("img");
    img.src = src;
    img.alt = row.keterangan ? row.keterangan : `Hasil makeup ${CATEGORY_LABELS[category].toLowerCase()}`;
    img.width = 800;
    img.height = 1000;
    img.loading = "lazy";
    img.decoding = "async";
    img.referrerPolicy = "no-referrer";
    img.addEventListener("error", () => li.remove());
    const cap = document.createElement("figcaption");
    cap.textContent = caption;
    fig.append(img, cap);
    li.append(fig);
    items.push(li);
  });
  if (!items.length) return;
  list.replaceChildren(...items);
  applyGalleryFilter();
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
      const img = document.createElement("img");
      img.src = src;
      img.alt = row.nama ? `Chat testimoni dari ${row.nama}` : "Chat testimoni dari klien";
      img.loading = "lazy";
      img.decoding = "async";
      img.referrerPolicy = "no-referrer";
      img.addEventListener("error", () => fig.remove());
      fig.append(img);
      if (row.nama) {
        const cap = document.createElement("figcaption");
        cap.textContent = row.nama;
        fig.append(cap);
      }
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
}

// Kalau link Sheets kosong, gagal dimuat, atau isinya kosong,
// isi bawaan di index.html tetap tampil.
function initSheets() {
  const { portfolioCsv, testimonialsCsv } = CONFIG.sheets;
  if (portfolioCsv) fetchRows(portfolioCsv).then(renderGallery).catch(() => {});
  if (testimonialsCsv) fetchRows(testimonialsCsv).then(renderTestimonials).catch(() => {});
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
    lokasi: form.elements.lokasi,
    jumlah: form.elements.jumlah,
    catatan: form.elements.catatan,
  };

  fields.tanggal.min = todayISO();

  const read = () => ({
    nama: fields.nama.value.trim(),
    look: fields.look.value,
    tanggal: fields.tanggal.value,
    jam: fields.jam.value,
    lokasi: fields.lokasi.value.trim(),
    jumlah: fields.jumlah.value,
    catatan: fields.catatan.value.trim(),
  });

  const rules = {
    nama: (v) => v.nama.length > 0,
    look: (v) => v.look in LOOK_NAMES,
    tanggal: (v) => v.tanggal !== "" && v.tanggal >= todayISO(),
    lokasi: (v) => v.lokasi.length > 0,
    jumlah: (v) => Number(v.jumlah) >= 1,
  };

  const setError = (name, show) => {
    const input = fields[name];
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
      if (!ok && !firstInvalid) firstInvalid = fields[name];
    });
    return firstInvalid;
  };

  // Link selalu berisi pesan terbaru, jadi klik biasa langsung membuka WA
  const syncLink = () => { sendLink.href = waUrl(buildMessage(read())); };

  form.addEventListener("input", (e) => {
    syncLink();
    const statusEl = document.getElementById("form-status");
    if (statusEl) statusEl.textContent = "";
    const name = e.target.name;
    if (rules[name] && e.target.getAttribute("aria-invalid") === "true") {
      setError(name, !rules[name](read()));
    }
  });
  form.addEventListener("change", syncLink);

  sendLink.addEventListener("click", (e) => {
    syncLink();
    const firstInvalid = validate();
    if (firstInvalid) {
      e.preventDefault();
      firstInvalid.focus();
    }
  });

  // Tombol "Kosongkan form": nilai kembali ke default, error & link ikut bersih
  const status = document.getElementById("form-status");
  form.addEventListener("reset", () => {
    // tunggu browser selesai mengembalikan nilai default dulu
    setTimeout(() => {
      Object.keys(rules).forEach((name) => setError(name, false));
      syncLink();
      fields.nama.focus();
      if (status) status.textContent = "Form sudah dikosongkan.";
    }, 0);
  });

  // Tekan Enter di form = sama dengan tombol kirim
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

/* ---------- Jalankan ---------- */
document.documentElement.classList.add("js");

document.addEventListener("DOMContentLoaded", () => {
  initPanLayout();
  initWaLinks();
  injectStructuredData();
  initLooks();
  initGalleryFilter();
  initSheets();
  initBookingForm();
  initScrollUI();
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
});
