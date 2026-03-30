import PhotoSwipeLightbox from '/assets/vendor/photoswipe/photoswipe-lightbox.esm.min.js';
import PhotoSwipe from '/assets/vendor/photoswipe/photoswipe.esm.min.js';

/* Find all gallery containers on the page */
const selectors = [
  '.painting-grid',
  '.artwork-grid',
  '.inst-photo-grid',
  '.vop-photo-grid',
  '.vop-photo-pair',
];

const galleries = document.querySelectorAll(selectors.join(', '));
if (galleries.length) {
  /* Collect all artwork items across all galleries for unified navigation */
  const allItems = [];
  galleries.forEach(g => {
    g.querySelectorAll('.artwork-item').forEach(item => allItems.push(item));
  });

  /*
   * Proportional sizing — paintings with data-size get constrained
   * so their lightbox size reflects physical scale:
   *   large  (>20"):  75vh / 85vw
   *   medium (10-20"): 55vh / 70vw
   *   small  (<10"):  40vh / 55vw
   *   no size (installation/display photos): full size
   */
  const sizeConstraints = {
    large:  { maxH: 0.75, maxW: 0.85 },
    medium: { maxH: 0.55, maxW: 0.70 },
    small:  { maxH: 0.40, maxW: 0.55 },
  };

  function constrainDimensions(naturalW, naturalH, sizeClass) {
    if (!sizeClass || !sizeConstraints[sizeClass]) {
      return { w: naturalW, h: naturalH };
    }
    const c = sizeConstraints[sizeClass];
    const maxW = window.innerWidth * c.maxW;
    const maxH = window.innerHeight * c.maxH;
    const ratio = naturalW / naturalH;

    /* Scale to fill the constraint box —
       ensures all paintings of the same size class display equally */
    let w, h;
    if (maxW / maxH > ratio) {
      h = maxH; w = h * ratio;
    } else {
      w = maxW; h = w / ratio;
    }
    return { w: Math.round(w), h: Math.round(h) };
  }

  const lightbox = new PhotoSwipeLightbox({
    pswpModule: PhotoSwipe,
    bgOpacity: 0.92,
    padding: { top: 20, bottom: 20, left: 20, right: 20 },
    wheelToZoom: true,
  });

  /* Build data source from all artwork items */
  lightbox.addFilter('numItems', () => allItems.length);

  lightbox.addFilter('itemData', (itemData, index) => {
    const el = allItems[index];
    if (!el) return itemData;
    const img = el.querySelector('img');
    if (!img) return itemData;

    const thumbSrc = img.src;
    const fullSrc = thumbSrc.replace(/-thumb\.webp$/, '.webp');
    const caption = el.getAttribute('data-caption') || '';
    const sizeClass = el.getAttribute('data-size') || null;

    /* Use thumbnail's natural dimensions for aspect ratio,
       then apply size constraints immediately */
    const natW = img.naturalWidth || 1200;
    const natH = img.naturalHeight || 800;
    const { w, h } = constrainDimensions(natW, natH, sizeClass);

    return {
      src: fullSrc,
      msrc: thumbSrc,
      alt: img.alt || '',
      caption: caption,
      sizeClass: sizeClass,
      element: el,
      w: w,
      h: h,
    };
  });

  /* When the full-size image loads, reapply the same constraint
     using its actual dimensions (same aspect ratio, so result is identical,
     but guards against thumbnails that weren't loaded yet) */
  lightbox.on('contentLoad', (e) => {
    const { content } = e;
    if (content.type !== 'image') return;

    const sizeClass = content.data.sizeClass || null;

    const img = new Image();
    img.onload = () => {
      const { w, h } = constrainDimensions(img.naturalWidth, img.naturalHeight, sizeClass);
      content.width = w;
      content.height = h;
      content.updateSize(true);
    };
    img.src = content.data.src;
  });

  /* Caption support */
  lightbox.on('uiRegister', () => {
    lightbox.pswp.ui.registerElement({
      name: 'caption',
      order: 9,
      isButton: false,
      appendTo: 'root',
      onInit: (el) => {
        el.style.cssText = 'position:absolute; bottom:0; left:0; right:0; text-align:center; padding:16px 20px; color:rgba(255,255,255,0.75); font-size:13px; font-family:Inter,-apple-system,system-ui,sans-serif; background:linear-gradient(transparent, rgba(0,0,0,0.4)); pointer-events:none;';
        lightbox.pswp.on('change', () => {
          const caption = lightbox.pswp.currSlide.data.caption;
          el.textContent = caption || '';
          el.style.display = caption ? 'block' : 'none';
        });
      },
    });
  });

  lightbox.init();

  /* Attach click handlers to each artwork item */
  allItems.forEach((item, i) => {
    item.style.cursor = 'pointer';
    item.addEventListener('click', (e) => {
      e.preventDefault();
      lightbox.loadAndOpen(i);
    });
  });
}
