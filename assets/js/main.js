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
function initGalleryFilter() {
  const chips = document.querySelectorAll(".chip");
  const shots = document.querySelectorAll(".shot");
  if (!chips.length) return;

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const filter = chip.dataset.filter;
      chips.forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
      shots.forEach((shot) => {
        shot.hidden = filter !== "semua" && shot.dataset.category !== filter;
      });
    });
  });
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
  initBookingForm();
  initScrollUI();
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
});
