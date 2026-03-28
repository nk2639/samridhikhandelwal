---
name: art-page
description: "Create or repair artwork/series pages. Usage: /art-page add (new series) or /art-page repair <page-name> (reformat existing page to match design system)."
user_invocable: true
---

# Art Page

Creates or repairs painting/artwork series pages for samridhiart.uk.eu.org.

## Arguments

- `/art-page add` — create a new series page (interview-style questions)
- `/art-page repair <page-name>` — reformat an existing page to match the current design system (e.g. `/art-page repair breach-escape-miss`)
- `/art-page repair all` — repair all painting pages

If no argument given, ask: **"Add a new series or repair an existing page?"**

---

## /art-page repair

When repairing an existing page, do NOT ask the gather-information questions. Infer everything from the existing HTML.

1. **Read the existing page** at `/var/www/htdocs-staging/<page-name>/index.html` — extract:
   - Title, medium, dimensions, year from `.series-header`
   - All image paths and alt text
   - Any captions from `.artwork-caption` elements or blockquotes
   - Any description/statement text
   - Whether installation views exist (separate from individual artworks)
   - Current prev/next links

2. **Read a reference page** (e.g. `/var/www/htdocs-staging/the-distance-i-carry/index.html`) to get the exact current nav dropdown HTML and page structure.

3. **Determine painting orientation** — portrait (taller than wide) or landscape (wider than tall) based on dimensions in metadata.

4. **Assign size classes** based on dimensions:
   - `small`: under ~10"
   - `medium`: ~10–20"
   - `large`: over ~20"
   - Display/documentation photos: no data-size

5. **Rewrite the page** using the page structure template below. Preserve ALL content:
   - Every image must be kept — count before and after
   - All text/descriptions preserved
   - Installation views go above the painting grid in `artwork-grid three-col`
   - Individual artworks go in `painting-grid portrait|landscape`
   - Description moves below the grid in `.series-statement` with repeated title
   - Captions move from visible grid text to `data-caption` attributes (lightbox only)
   - Ensure lightbox has nav arrows and caption support
   - Ensure nav dropdown matches current site state
   - Ensure prev/next links are correct

6. **Verify** — count all images before and after. Nothing dropped.

---

## /art-page add

Create a new series page. Ask these questions **one at a time** (interview style — wait for each answer before asking the next):

1. "What's the title of the series?"
2. "What's the medium and dimensions?" (e.g. Watercolour on paper, 5.75" × 4")
3. "What year?" (e.g. 2024–ongoing)
4. "Where are the images? (zip file path, folder, etc.)"
5. "Are there any installation views? (photos showing the work displayed in a gallery/space)"
6. "Is there an artist statement or description? (can be a text file with the images, or you can paste it)"
7. "Do individual paintings have different titles and sizes, or are they all the same?"
8. "Where should this appear in the work order?" (show the current list and ask where to insert)

Then follow these steps:

### Extract and prepare images

- Extract images to `/var/www/htdocs-staging/assets/{slug}/`
- Rename files to clean, web-friendly names: lowercase, hyphens, no spaces/quotes/special chars
- Keep a text file (like `statement.txt`) if one exists in the archive
- Note: OpenBSD doesn't have `unzip` — use `python3 -c "import zipfile; ..."` to extract
- **Count all images and verify none are lost during extraction**

### Create the page

Create `/var/www/htdocs-staging/{slug}/index.html` using the page structure template below.

### Update navigation across ALL pages

Add the new series to the Works dropdown on **every page**. The dropdown lives inside `<nav class="site-nav">` in the header.

Add `<a href="/{slug}/">{Title}</a>` in the correct position within every `.nav-dropdown-menu`.

Files to update (all in `/var/www/htdocs-staging/`):
- `index.html`, `gallery/index.html`, `about/index.html`, `cv/index.html`, `contact/index.html`
- All series page directories: `veils-of-presence/`, `the-distance-i-carry/`, `can-you-see-me-can-you-feel-me/`, `reciprocity-failure/`, `unknown-desires/`, `empiricism-inside-out/`, `breach-escape-miss/`, `reciprocity-failure-2/`, `trapped-with-shadows/`, `veils-of-thought/`, `earlier-works/`
- Plus any other series pages that exist

### Update prev/next links

The new page inserts into the work sequence. Update:
- The **new page's** prev/next to point to its neighbours
- The **previous work's** "next" link to point to the new page
- The **next work's** "prev" link to point to the new page

Current work order:
1. Veils of Presence (`/veils-of-presence/`)
2. The Distance I Carry (`/the-distance-i-carry/`)
3. Can You See Me, Can You Feel Me (`/can-you-see-me-can-you-feel-me/`)
4. Unveiling the Veil (`/reciprocity-failure/`)
5. Unaware Desires (`/unknown-desires/`)
6. Empiricism (Inside Out) (`/empiricism-inside-out/`)
7. Breach, Escape, Miss (`/breach-escape-miss/`)
8. Reciprocity Failure (`/reciprocity-failure-2/`)
9. Trapped with Shadows (`/trapped-with-shadows/`)
10. Veils of Thought (`/veils-of-thought/`)
11. Earlier Works (`/earlier-works/`)

The list wraps: Earlier Works → Veils of Presence.

### Add to gallery/works page

Add a work card to `/var/www/htdocs-staging/gallery/index.html`:

```html
<a class="work-card" href="/{slug}/">
  <img src="/assets/{slug}/{best-thumbnail}" alt="{Title}" loading="lazy">
  <div class="work-card-info">
    <h3>{Title}</h3>
    <p>{Medium}, {year}</p>
  </div>
</a>
```

### Update homepage (if applicable)

If this is a "current work", update the homepage card in `/var/www/htdocs-staging/index.html`.

### Final verification

- Count images on the page vs source — **nothing dropped**
- All nav dropdowns updated across all pages
- Prev/next links form a complete chain
- Lightbox works: arrows navigate, captions show, sizes are proportional
- Breadcrumb shows correctly
- Gallery page has the new card

---

## Page structure template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Samridhi Khandelwal — {Title}</title>
  <meta name="description" content="{Title} — {short description} by Samridhi Khandelwal.">
  <meta property="og:title" content="Samridhi Khandelwal — {Title}">
  <meta property="og:url" content="https://samridhiart.uk.eu.org/{slug}/">
  <link rel="canonical" href="https://samridhiart.uk.eu.org/{slug}/">
  <link rel="icon" href="/assets/images/cropped-img_2200-1-32x32.jpg" sizes="32x32">
  <link rel="apple-touch-icon" href="/assets/images/cropped-img_2200-1-180x180.jpg">
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
  <!-- HEADER: Copy exact nav from a current page — includes Works dropdown -->
  <header class="site-header">...</header>

  <main>
    <div class="container">
      <div class="breadcrumb"><a href="/gallery/">Works</a> &rsaquo; {Title}</div>
      <div class="series-header">
        <h1>{Title}</h1>
        <p class="series-meta">{Medium}, {dimensions}, {year}</p>
      </div>

      <!-- Installation views (if available) — above the painting grid -->
      <h2 style="text-align:center; margin-bottom:1.5rem;">Installation Views</h2>
      <div class="artwork-grid three-col" style="margin-bottom:3rem;">
        <div class="artwork-item"><img src="..." alt="..." loading="lazy"></div>
      </div>

      <!-- Painting grid -->
      <div class="painting-grid {portrait|landscape}">
        <!-- Order: small → medium → large → display photos -->
        <div class="artwork-item" data-caption="{Title}, {Medium}, {dimensions}" data-size="{small|medium|large}">
          <img src="..." alt="..." loading="lazy">
        </div>
      </div>

      <!-- Description (optional) — BELOW grid, title repeated -->
      <div class="series-statement">
        <h2>{Title}</h2>
        <p class="series-meta">{Medium}, {dimensions}, {year}</p>
        <div class="series-description">
          <p>...</p>
        </div>
      </div>
    </div>

    <nav class="work-nav">
      <a href="/{prev-slug}/" class="prev">
        <span class="nav-label">&larr; Previous</span>
        <span class="nav-title">{Previous Title}</span>
      </a>
      <a href="/{next-slug}/" class="next">
        <span class="nav-label">Next &rarr;</span>
        <span class="nav-title">{Next Title}</span>
      </a>
    </nav>
  </main>

  <div class="lightbox" id="lightbox">
    <button class="lightbox-close" aria-label="Close">&times;</button>
    <button class="lightbox-nav lb-prev" aria-label="Previous">&#8249;</button>
    <button class="lightbox-nav lb-next" aria-label="Next">&#8250;</button>
    <div class="lightbox-content">
      <img src="" alt="">
      <p class="lightbox-caption"></p>
    </div>
  </div>

  <footer class="site-footer">
    &copy; 2025 Samridhi Khandelwal. All rights reserved.
  </footer>

  <script src="/assets/js/main.js"></script>
</body>
</html>
```

## Key rules

- **Grid class**: `painting-grid portrait` (taller than wide) or `painting-grid landscape` (wider than tall)
- **No captions** in the grid — captions only in lightbox via `data-caption`
- **Order**: small → medium → large → display photos
- **data-size**: `small` (<10"), `medium` (10–20"), `large` (>20"). Display photos: no data-size.
- **Single image**: CSS `:only-child` auto-centers — no spacer divs
- **Installation views**: separate `artwork-grid three-col` above the painting grid, no data-caption/data-size, larger than individual artwork thumbnails
