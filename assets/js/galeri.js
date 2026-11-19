/* ==========================================================================
   Natasya Makeup — tampilan foto besar di Portofolio
   Klik / Enter pada foto portofolio membuka foto besar (PhotoSwipe 5,
   disimpan di assets/vendor/photoswipe). Library dan CSS-nya baru dimuat
   saat foto pertama dibuka, jadi tidak memperlambat halaman.
   Data foto diambil dari atribut yang dipasang renderGallery() di main.js:
   data-full (foto 1600px) dan data-caption (keterangan).
   ========================================================================== */

const GALERI_BASE = document.currentScript.src;
const PSWP_JS = new URL("../vendor/photoswipe/photoswipe.esm.min.js", GALERI_BASE).href;
const PSWP_CSS = new URL("../vendor/photoswipe/photoswipe.css", GALERI_BASE).href;
const FULL_WIDTH = 1600;

let viewer = null;      // PhotoSwipe yang sedang terbuka
let opening = false;    // sedang memuat library (cegah klik dobel)
let cssReady = null;

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

function captionText(caption, n, total) {
  return caption ? `${caption} · ${n} / ${total}` : `${n} / ${total}`;
}

function loadCss() {
  if (!cssReady) {
    cssReady = new Promise((resolve) => {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = PSWP_CSS;
      link.onload = link.onerror = () => resolve();
      document.head.append(link);
    });
  }
  return cssReady;
}

async function openViewer(index) {
  if (viewer || opening || index < 0) return;
  opening = true;
  try {
    const [{ default: PhotoSwipe }] = await Promise.all([import(PSWP_JS), loadCss()]);
    const dataSource = galleryImages().map(slideFrom);
    if (!dataSource.length) return;

    const pswp = new PhotoSwipe({
      dataSource,
      index: Math.min(index, dataSource.length - 1),
      loop: true,
      counter: false,
      bgOpacity: 1,
      showHideAnimationType: "fade",
      // Ruang kosong di sekitar foto: bawah untuk keterangan, atas untuk tombol,
      // kiri-kanan (layar lebar) untuk tombol panah.
      paddingFn: (viewport) => (viewport.x < 700
        ? { top: 56, bottom: 64, left: 0, right: 0 }
        : { top: 56, bottom: 64, left: 72, right: 72 }),
      closeTitle: "Tutup",
      zoomTitle: "Perbesar",
      arrowPrevTitle: "Foto sebelumnya",
      arrowNextTitle: "Foto berikutnya",
      errorMsg: "Foto tidak bisa dimuat",
      closeOnVerticalDrag: true,        // geser ke bawah untuk menutup
      doubleTapAction: "zoom",          // ketuk 2x untuk zoom
      imageClickAction: "zoom-or-close",
    });

    // Ukuran foto yang belum pernah termuat hanya perkiraan (4:5). Setelah foto besar
    // termuat, pakai ukuran aslinya supaya tidak gepeng.
    pswp.on("loadComplete", ({ content }) => {
      const img = content.element;
      if (!img || !img.naturalWidth) return;
      const d = content.data;
      const ratio = img.naturalWidth / img.naturalHeight;
      if (Math.abs(ratio - d.width / d.height) / ratio > 0.01) {
        d.width = img.naturalWidth;
        d.height = img.naturalHeight;
        pswp.refreshSlideContent(content.index);
      }
    });

    // Foto dari Google Drive dimuat tanpa referrer, sama seperti di galeri.
    pswp.on("contentLoadImage", ({ content }) => {
      if (content.element) content.element.referrerPolicy = "no-referrer";
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
          pswp.on("change", () => {
            const data = pswp.currSlide ? pswp.currSlide.data : {};
            el.textContent = captionText(data.caption, pswp.currIndex + 1, pswp.getNumItems());
          });
        },
      });
    });

    // Tombol back HP menutup foto, bukan keluar dari website.
    let closedByBack = false;
    const onBack = () => { closedByBack = true; pswp.close(); };
    history.pushState({ natasyaFoto: true }, "");
    window.addEventListener("popstate", onBack);
    pswp.on("close", () => {
      window.removeEventListener("popstate", onBack);
      if (!closedByBack && history.state && history.state.natasyaFoto) history.back();
    });

    pswp.on("destroy", () => { viewer = null; });
    viewer = pswp;
    pswp.init();
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
    openViewer(galleryImages().indexOf(img));
  });
  list.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const img = target(e);
    if (!img) return;
    e.preventDefault();
    openViewer(galleryImages().indexOf(img));
  });
}

initGalleryViewer();
