/* ==========================================================================
   Natasya Makeup — tampilan foto besar di Portofolio
   Klik / Enter pada foto portofolio membuka foto besar (PhotoSwipe 5,
   disimpan di assets/vendor/photoswipe). Library dan CSS-nya baru dimuat
   saat foto pertama dibuka, jadi tidak memperlambat halaman.
   Data foto diambil dari atribut yang dipasang renderGallery() di main.js:
   data-full (foto 1600px) dan data-caption (keterangan).
   ========================================================================== */

// Dibungkus supaya nama-nama di file ini tidak bentrok dengan main.js.
(() => {
const GALERI_BASE = document.currentScript.src;
const PSWP_JS = new URL("../vendor/photoswipe/photoswipe.esm.min.js", GALERI_BASE).href;
const PSWP_CSS = new URL("../vendor/photoswipe/photoswipe.css", GALERI_BASE).href;
const FULL_WIDTH = 1600;

let viewer = null;      // PhotoSwipe yang sedang terbuka
let opening = false;    // sedang memuat library (cegah klik dobel)
let cssReady = null;
let retries = 0;        // dinaikkan tiap kali library gagal dimuat (alamat baru = unduh ulang)

function galleryImages() {
  return [...document.querySelectorAll(".gallery .shot img[data-full]")];
}

// Ukuran sementara dari foto kecil yang sudah termuat; kalau belum termuat, anggap 4:5.
function slideFrom(img) {
  const loaded = img.complete && img.naturalWidth > 0;
  return {
    src: img.dataset.full,
    msrc: loaded ? img.currentSrc || img.src : undefined,
    width: FULL_WIDTH,
    height: loaded ? Math.round(FULL_WIDTH * img.naturalHeight / img.naturalWidth) : 2000,
    alt: img.alt,
    caption: img.dataset.caption || "",
  };
}

// Ukuran foto yang belum pernah termuat hanya perkiraan (4:5). Setelah foto besar
// termuat, pakai ukuran aslinya supaya tidak gepeng.
function fitToImage(pswp, content) {
  const img = content.element;
  if (!img || !img.naturalWidth) return;
  const d = content.data;
  const ratio = img.naturalWidth / img.naturalHeight;
  if (Math.abs(ratio - d.width / d.height) / ratio <= 0.01) return;
  d.width = content.width = img.naturalWidth;
  d.height = content.height = img.naturalHeight;
  if (content.slide && !pswp.isDestroying) pswp.refreshSlideContent(content.index);
}

function captionText(caption, n, total) {
  return caption ? `${caption} · ${n} / ${total}` : `${n} / ${total}`;
}

// Tulis keterangan + nomor maksimal 2 baris. Keterangan yang terlalu panjang dipendekkan
// dengan "…", nomornya selalu utuh.
const MAX_LINES = 2;
function fitCaption(el, caption, n, total) {
  const count = `${n} / ${total}`;
  const set = (text) => { if (el.textContent !== text) el.textContent = text; };
  set(captionText(caption, n, total));
  if (!caption) return;
  const cs = getComputedStyle(el);
  const maxH = parseFloat(cs.lineHeight) * MAX_LINES + 1;
  const textH = () => el.scrollHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  if (textH() <= maxH) return;
  const cut = (len) => `${caption.slice(0, len).trimEnd()}… · ${count}`;
  let lo = 0, hi = caption.length - 1;
  while (lo < hi) {
    const mid = Math.ceil((lo + hi) / 2);
    el.textContent = cut(mid);
    if (textH() <= maxH) lo = mid; else hi = mid - 1;
  }
  // Potong di batas kata supaya tidak berhenti di tengah kata (tetap muat karena lebih pendek).
  const space = caption.slice(0, lo + 1).lastIndexOf(" ");
  set(cut(space > lo * 0.6 ? space : lo));
}

function loadCss() {
  if (!cssReady) {
    cssReady = new Promise((resolve, reject) => {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = PSWP_CSS;
      link.onload = () => resolve();
      link.onerror = () => { link.remove(); reject(new Error("CSS galeri gagal dimuat")); };
      document.head.append(link);
    });
  }
  return cssReady;
}

function loadLibrary() {
  const js = retries ? `${PSWP_JS}?coba=${retries}` : PSWP_JS;
  return Promise.all([import(js), loadCss()]).catch((err) => {
    retries += 1;
    cssReady = null;
    throw err;
  });
}

async function openViewer(clicked) {
  if (viewer || opening) return;
  opening = true;
  try {
    let PhotoSwipe;
    try {
      [{ default: PhotoSwipe }] = await loadLibrary();
    } catch (err) {
      console.warn("Galeri: tampilan foto besar gagal dimuat, ketuk foto lagi untuk mencoba.", err);
      return;
    }
    // Urutan dihitung setelah library siap: galeri bisa berubah selama menunggu
    // (misalnya foto rusak terhapus).
    const images = galleryImages();
    const index = images.indexOf(clicked);
    if (index < 0) return;
    const dataSource = images.map(slideFrom);

    const pswp = new PhotoSwipe({
      dataSource,
      index,
      loop: true,
      counter: false,
      bgOpacity: 1,
      showHideAnimationType: "fade",
      // Ruang kosong di sekitar foto: bawah untuk keterangan, atas untuk tombol,
      // kiri-kanan (layar lebar) untuk tombol panah.
      paddingFn: (viewport) => (viewport.x < 700
        ? { top: 56, bottom: 76, left: 0, right: 0 }
        : { top: 56, bottom: 76, left: 72, right: 72 }),
      closeTitle: "Tutup",
      zoomTitle: "Perbesar",
      arrowPrevTitle: "Foto sebelumnya",
      arrowNextTitle: "Foto berikutnya",
      errorMsg: "Foto tidak bisa dimuat",
      closeOnVerticalDrag: true,        // geser ke bawah untuk menutup
      doubleTapAction: "zoom",          // ketuk 2x untuk zoom
      imageClickAction: "zoom-or-close",
    });

    pswp.on("contentLoadImage", ({ content }) => {
      const img = content.element;
      if (!img) return;
      // Foto dari Google Drive dimuat tanpa referrer, sama seperti di galeri.
      img.referrerPolicy = "no-referrer";
      // Didengarkan langsung di <img> karena PhotoSwipe tidak memberi kabar untuk foto
      // yang dimuat duluan (tetangga) sebelum slide-nya dibuat.
      img.addEventListener("load", () => fitToImage(pswp, content), { once: true });
    });

    // Keterangan + nomor di bawah foto
    pswp.on("uiRegister", () => {
      pswp.ui.registerElement({
        name: "caption-bar",
        className: "pswp__caption-bar",
        appendTo: "root",
        order: 9,
        isButton: false,
        onInit: (el) => {
          el.setAttribute("aria-live", "polite");
          const update = () => {
            const data = pswp.currSlide ? pswp.currSlide.data : {};
            fitCaption(el, data.caption, pswp.currIndex + 1, pswp.getNumItems());
          };
          pswp.on("change", update);
          pswp.on("resize", update);
        },
      });
    });

    // Tombol back HP menutup foto, bukan keluar dari website.
    let closedByBack = false;
    const onBack = () => {
      closedByBack = true;
      // Selama animasi buka, PhotoSwipe mengabaikan close(); tutup begitu animasinya selesai.
      if (pswp.opener.isOpen) pswp.close();
      else pswp.on("openingAnimationEnd", () => pswp.close());
    };
    history.pushState({ natasyaFoto: true }, "");
    window.addEventListener("popstate", onBack);
    pswp.on("close", () => {
      window.removeEventListener("popstate", onBack);
      if (!closedByBack && history.state && history.state.natasyaFoto) history.back();
    });

    pswp.on("destroy", () => { viewer = null; });
    viewer = pswp;
    pswp.init();

    // Pembaca layar: nama dialog dan label berbahasa Indonesia
    pswp.element.setAttribute("aria-label", "Foto portofolio");
    pswp.element.setAttribute("aria-modal", "true");
    pswp.element.querySelectorAll('[aria-roledescription="carousel"]')
      .forEach((el) => el.setAttribute("aria-roledescription", "galeri foto"));
    pswp.element.querySelectorAll('[aria-roledescription="slide"]')
      .forEach((el) => el.setAttribute("aria-roledescription", "foto"));
  } finally {
    opening = false;
  }
}

function initGalleryViewer() {
  const list = document.querySelector(".gallery");
  if (!list) return;
  const target = (e) => e.target.closest && e.target.closest("img[data-full]");

  list.addEventListener("click", (e) => {
    const img = target(e);
    if (!img) return;
    e.preventDefault();
    openViewer(img);
  });
  list.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const img = target(e);
    if (!img) return;
    e.preventDefault();
    openViewer(img);
  });
}

initGalleryViewer();
})();
