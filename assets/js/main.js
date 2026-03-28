/* ========== Mobile Nav Toggle ========== */
const navToggle = document.querySelector('.nav-toggle');
const siteNav = document.querySelector('.site-nav');

if (navToggle && siteNav) {
  navToggle.addEventListener('click', () => {
    siteNav.classList.toggle('open');
    const expanded = siteNav.classList.contains('open');
    navToggle.setAttribute('aria-expanded', expanded);
  });
}

/* ========== Works Dropdown (desktop hover only) ========== */

/* ========== Lightbox with navigation ========== */
const lightbox = document.getElementById('lightbox');
const lightboxImg = lightbox ? lightbox.querySelector('img') : null;
const lightboxCaption = lightbox ? lightbox.querySelector('.lightbox-caption') : null;
const lightboxPrev = lightbox ? lightbox.querySelector('.lb-prev') : null;
const lightboxNext = lightbox ? lightbox.querySelector('.lb-next') : null;
const items = Array.from(document.querySelectorAll('.artwork-item'));
let currentIndex = 0;

function showImage(index) {
  if (index < 0 || index >= items.length) return;
  const item = items[index];
  const img = item.querySelector('img');
  if (!img || !lightboxImg) return;

  currentIndex = index;
  /* Load full-size image in lightbox (strip -thumb from thumbnail path) */
  lightboxImg.src = img.src.replace(/-thumb\.webp$/, '.webp');
  lightboxImg.alt = img.alt;

  /* Size class for proportional painting display */
  lightboxImg.classList.remove('lb-large', 'lb-medium', 'lb-small');
  const size = item.dataset.size;
  if (size) {
    lightboxImg.classList.add('lb-' + size);
  }

  /* Caption */
  if (lightboxCaption) {
    lightboxCaption.textContent = item.dataset.caption || '';
  }
}

function openLightbox(index) {
  if (!lightbox) return;
  showImage(index);
  lightbox.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeLightbox() {
  if (!lightbox) return;
  lightbox.classList.remove('active');
  document.body.style.overflow = '';
}

function prevImage(e) {
  if (e) { e.stopPropagation(); e.preventDefault(); }
  showImage(currentIndex > 0 ? currentIndex - 1 : items.length - 1);
}

function nextImage(e) {
  if (e) { e.stopPropagation(); e.preventDefault(); }
  showImage(currentIndex < items.length - 1 ? currentIndex + 1 : 0);
}

/* Click on artwork to open */
items.forEach((item, i) => {
  item.addEventListener('click', () => openLightbox(i));
});

/* Navigation buttons — stop propagation so overlay doesn't close */
if (lightboxPrev) {
  lightboxPrev.addEventListener('click', prevImage);
}
if (lightboxNext) {
  lightboxNext.addEventListener('click', nextImage);
}

/* Close button */
const closeBtn = lightbox ? lightbox.querySelector('.lightbox-close') : null;
if (closeBtn) {
  closeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    closeLightbox();
  });
}

/* Click overlay to close — only when clicking the dark background itself */
if (lightbox) {
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      closeLightbox();
    }
  });
}

/* Keyboard navigation */
document.addEventListener('keydown', (e) => {
  if (!lightbox || !lightbox.classList.contains('active')) return;
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowLeft') prevImage();
  if (e.key === 'ArrowRight') nextImage();
});
