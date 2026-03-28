# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A static HTML website for artist Samridhi Khandelwal, served at `samridhiart.uk.eu.org`. All pages are hand-written HTML/CSS/JS — no build system, no package manager, no templates, no dynamic backend.

Self-hosted fonts (Cormorant Garamond + Inter) in woff2 format. Zero external dependencies.

## Server Stack

```
Internet → relayd (port 443, TLS termination)
         → httpd (127.0.0.1:8080, static files)
         → /var/www/htdocs/
```

- **relayd** handles TLS (`/etc/relayd.conf`) and sets security headers (HSTS, CSP, etc.)
- **httpd** serves static files (`/etc/httpd.conf`); HTTP on port 80 redirects to HTTPS
- TLS certificate: `/etc/ssl/samridhiart.uk.eu.org:443.crt`, managed via ACME

A secondary virtual host `dav.samridhiart.uk.eu.org` proxies to Radicale (CalDAV/CardDAV) on port 5232.

## Branches and Deployment

- **`main`** — production; served from `/var/www/htdocs/`
- **`staging`** — development/testing; served from `/var/www/htdocs-staging/`

Work on `staging`, then merge to `main` when ready to go live.

## Common Operations

Reload web server config after editing `/etc/httpd.conf`:
```sh
doas rcctl reload httpd
```

Reload reverse proxy config after editing `/etc/relayd.conf`:
```sh
doas rcctl reload relayd
```

Renew TLS certificate (ACME):
```sh
doas acme-client samridhiart.uk.eu.org && doas rcctl reload relayd
```

## Content Structure

- `index.html` — homepage (full-bleed hero)
- `gallery/` — works page (grid of series cards)
- `breach-escape-miss/`, `empiricism-inside-out/`, `veils-of-thought/`, `can-you-see-me-can-you-feel-me/`, `trapped-with-shadows/`, `unknown-desires/`, `reciprocity-failure/`, `reciprocity-failure-2/`, `earlier-works/` — individual series pages
- `about/` — bio, artist statement, CV
- `contact/` — email + social links
- `wp-content/uploads/2024/` — artwork images (JPEG)
- `assets/css/style.css` — single stylesheet for the entire site
- `assets/js/main.js` — lightbox + mobile nav toggle
- `assets/fonts/` — self-hosted Cormorant Garamond and Inter (woff2)
- `assets/images/` — favicon and touch icon
- `bgplg/` — redirects to `/cgi-bin/bgplg` (OpenBGPD looking glass tool)

## Shared Page Template

All pages share the same structure:
- Fixed header with artist name (left) + nav links: Works, About, Contact
- Mobile hamburger menu (JS in `main.js`)
- Footer with copyright

The `active` class on nav links indicates the current page.

Every page `<head>` must include: charset, viewport, `<title>`, meta description, OG tags (`og:title`, `og:url`), canonical URL, favicon, apple-touch-icon, and the stylesheet link. Keep these consistent when creating or editing pages.

## Series Pages

Series pages (e.g. `breach-escape-miss/index.html`) display artwork images in a grid. Each image is wrapped in a `.artwork-item` div. The lightbox requires this HTML at the end of `<body>` (before the `<script>` tag):

```html
<div class="lightbox" id="lightbox">
  <button class="lightbox-close" aria-label="Close">&times;</button>
  <img src="" alt="">
</div>
```

## Design Tokens (CSS Custom Properties)

Defined in `assets/css/style.css`:
- `--bg: #fafaf8` (warm off-white background)
- `--text: #1a1a1a` (near-black text)
- `--accent: #8b7355` (warm bronze)
- `--accent-dark: #5a4a3a` (nav hover/links)
- `--serif: 'Cormorant Garamond'` (headings)
- `--sans: 'Inter'` (body/nav)

## Image Handling

- All artwork images live in `wp-content/uploads/2024/{09,10}/`
- No `?w=` query parameters — serve original files
- All `<img>` tags have `loading="lazy"` and descriptive `alt` text
- Lightbox: clicking `.artwork-item` opens image in overlay (ESC/click to close)
- See `THUMBNAILS.md` for how to change series thumbnail images on the Works page

## Key Notes

- The `mail` user owns the files in `/var/www/htdocs`.
- No external dependencies — all fonts, CSS, and JS are self-hosted.
- Each page is a complete standalone HTML file (no includes or templating).
