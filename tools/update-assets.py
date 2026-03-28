#!/usr/bin/env python3
"""
update-assets.py — Remove WordPress.com dependencies from all HTML files.

Phase 1: Replace external CSS/JS URLs with local paths.
Phase 2: Strip tracking, ads, and WordPress boilerplate.

Run from any directory; it finds HTML files relative to its own location.
"""

import os
import re
import sys

HTDOCS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ──────────────────────────────────────────────────────────────────────────────
# CSS URL → local path mapping
# Key: URL base (without query string, matched by startswith)
# Value: local href to substitute
# ──────────────────────────────────────────────────────────────────────────────

# The base bundles (??-eJ*) contain ONLY tracking/ads/marketing-bar CSS
# (WordAds, EU cookie law, marketing bar, related posts).
# They should be REMOVED, not replaced.
DROP_CSS_URL_PREFIXES = [
    # all-css-0-1 homepage bundle: wordads + eu-cookie + marketing-bar
    "https://s1.wp.com/_static/??-eJxljUsO",
    # all-css-0-1 pages bundle: wordads + eu-cookie + related-posts + marketing-bar
    "https://s1.wp.com/_static/??-eJx9jtEK",
    # all-css-28-1 / all-css-40-1 theme extras: reblogging + geo-location
    "https://s1.wp.com/_static/??-eJzTLy",
    # mediaelement + bbpress (WordPress-specific players, not used in static site)
    "https://s1.wp.com/_static/??/wp-content/mu-plugins/core-compat/wp-mediaelement.css",
    # assembler theme standalone (homepage only) — content is already in wp-theme-bundle.css
    "https://s1.wp.com/wp-content/themes/pub/assembler/style.css",
    # contact form CSS from Jetpack — will be dropped (new form has no external CSS)
    "https://s2.wp.com/wp-content/mu-plugins/jetpack-plugin/moon/jetpack_vendor/automattic/jetpack-forms/dist/contact-form/css/grunion.css",
    # opensearch link (points to wp.com)
    "https://s1.wp.com/opensearch.xml",
]

# CSS URLs to keep as local assets
CSS_URL_MAP = {
    # navigation block CSS
    "https://s1.wp.com/wp-content/plugins/gutenberg-core/v20.6.0/build/block-library/blocks/navigation/style.css":
        "/assets/css/wp-navigation.css",
    # slideshow block CSS (homepage)
    "https://s0.wp.com/wp-content/mu-plugins/jetpack-plugin/moon/_inc/blocks/slideshow/view.css":
        "/assets/css/wp-slideshow.css",
    # social links block CSS
    "https://s1.wp.com/wp-content/plugins/gutenberg-core/v20.6.0/build/block-library/blocks/social-links/style.css":
        "/assets/css/wp-social-links.css",
    # gallery block CSS (standalone link, e.g. unknown-desires)
    "https://s1.wp.com/wp-content/plugins/gutenberg-core/v20.6.0/build/block-library/blocks/gallery/style.css":
        "/assets/css/wp-gallery.css",
    # comment-likes + noticons + assembler bundle (most non-home pages)
    "https://s0.wp.com/_static/??/wp-content/mu-plugins/comment-likes/css/comment-likes.css":
        "/assets/css/wp-theme-bundle.css",
    # h4 global CSS
    "https://s2.wp.com/wp-content/themes/h4/global.css":
        "/assets/css/wp-h4-global.css",
    # all-css-10-1: gallery + carousel CSS (breach-escape, earlier-works, reciprocity, etc.)
    "https://s1.wp.com/_static/??-eJytjEs":
        "/assets/css/wp-bundle-series.css",
    # all-css-8-1: tiled-gallery + carousel CSS (can-you-see-me, empiricism, unknown-desires)
    "https://s0.wp.com/_static/??-eJylzNE":
        "/assets/css/wp-bundle-series2.css",
    # all-css-24-1: carousel CSS (about page)
    "https://s0.wp.com/_static/??-eJyljFs":
        "/assets/css/wp-bundle-about.css",
}

# JS URLs to KEEP (replace with local path)
JS_URL_MAP = {
    "https://s0.wp.com/wp-content/plugins/gutenberg-core/v20.6.0/build/hooks/index.min.js":
        "/assets/js/wp-hooks.js",
    "https://s0.wp.com/wp-content/plugins/gutenberg-core/v20.6.0/build/i18n/index.min.js":
        "/assets/js/wp-i18n.js",
    "https://s1.wp.com/wp-content/plugins/gutenberg-core/v20.6.0/build-module/block-library/navigation/view.min.js":
        "/assets/js/wp-navigation.js",
    # interactivity module (appears in modulepreload link and importmap)
    "https://s0.wp.com/wp-content/plugins/gutenberg-core/v20.6.0/build-module/interactivity/index.min.js":
        "/assets/js/wp-interactivity.js",
}

# JS URLs to DROP entirely (tracking, ads, WordPress-only widgets)
DROP_JS_URL_PREFIXES = [
    # All _static/?? JS bundles — they bundle tracking/ads/WP-internals
    "https://s0.wp.com/_static/??",
    "https://s1.wp.com/_static/??",
    "https://s2.wp.com/_static/??",
    # gravatar hovercards
    "https://s2.wp.com/wp-content/mu-plugins/gravatar-hovercards/wpgroho.js",
    # mobile user agent utility
    "https://s1.wp.com/wp-content/js/mobile-useragent-info.js",
    # wordpress analytics beacon
    "http://stats.wp.com/w.js",
    # wordads + eu-cookie-law bundle
    "https://s2.wp.com/_static/??/wp-content/blog-plugins/wordads-classes/js/watl-v2.js",
    # jetpack accessible-form JS (replaced by native HTML5 form)
    "https://s1.wp.com/wp-content/mu-plugins/jetpack-plugin/moon/jetpack_vendor/automattic/jetpack-forms/dist/contact-form/js/accessible-form.js",
    # dom-ready and escape-html (WordPress internals, not needed)
    "https://s0.wp.com/wp-content/plugins/gutenberg-core/v20.6.0/build/dom-ready/index.min.js",
    "https://s0.wp.com/wp-content/plugins/gutenberg-core/v20.6.0/build/escape-html/index.min.js",
    # eu-cookie-law standalone script (appears in some GET.html files)
    "https://s2.wp.com/wp-content/mu-plugins/widgets/eu-cookie-law/",
]


def remove_balanced_div(content, id_attr):
    """Remove a <div id="..."> ... </div> block, tracking nesting depth."""
    import re as _re
    pattern = rf'<div\s[^>]*id="{id_attr}"[^>]*>'
    m = _re.search(pattern, content)
    if not m:
        return content
    start = content.rfind('\n', 0, m.start())
    if start == -1:
        start = 0
    pos = m.end()
    depth = 1
    end = None
    while pos < len(content) and depth > 0:
        next_open = content.find('<div', pos)
        next_close = content.find('</div>', pos)
        if next_open != -1 and (next_close == -1 or next_open < next_close):
            depth += 1
            pos = next_open + 4
        elif next_close != -1:
            depth -= 1
            if depth == 0:
                end = next_close + len('</div>')
                break
            pos = next_close + 6
        else:
            break
    if end:
        content = content[:start] + content[end:]
    return content


def url_matches_prefix(url, prefixes):
    """Return True if url starts with any of the given prefixes (after stripping query)."""
    # Normalise the URL: decode &amp; entities
    url = url.replace("&amp;", "&")
    for pfx in prefixes:
        if url.startswith(pfx):
            return True
    return False


def url_local_path(url, url_map):
    """Return local path for url if found in url_map, else None."""
    url = url.replace("&amp;", "&")
    for prefix, local in url_map.items():
        if url.startswith(prefix):
            return local
    return None


def remove_block(content, start_pattern, end_pattern, flags=re.DOTALL):
    """Remove everything from start_pattern to end_pattern (inclusive)."""
    return re.sub(start_pattern + r'.*?' + end_pattern, '', content, flags=flags)


def process_html(content, filepath):
    """Apply all transformations to an HTML file's content."""
    rel = filepath.replace(HTDOCS, '')

    # ── 1. Remove HTTrack comments ────────────────────────────────────────────
    # Opening comment: <!-- Mirrored from ... -->
    content = re.sub(r'<!-- Mirrored from[^-]+-+>', '', content, flags=re.DOTALL)
    # Added by HTTrack meta block
    content = re.sub(r'<!-- Added by HTTrack -->.*?<!-- /Added by HTTrack -->', '', content, flags=re.DOTALL)
    # Closing HTTrack comment at end
    content = re.sub(r'\n  <!-- Mirrored from[^\n]+\n', '\n', content)

    # ── 2. Remove all <link rel="dns-prefetch"> tags ─────────────────────────
    content = re.sub(r'\s*<link\s+rel="dns-prefetch"[^>]*/?\s*>', '', content)

    # ── 3. Remove addLoadEvent inline script ─────────────────────────────────
    content = re.sub(
        r'\s*<script type="text/javascript">\s*/\* <!\[CDATA\[ \*/\s*function addLoadEvent.*?/\* \]\]> \*/\s*</script>',
        '', content, flags=re.DOTALL)

    # ── 4. Remove _wpemojiSettings + emoji detection script ──────────────────
    content = re.sub(
        r'\s*<script>\s*window\._wpemojiSettings\s*=.*?</script>',
        '', content, flags=re.DOTALL)

    # ── 5. Remove wp-shortlink link ───────────────────────────────────────────
    content = re.sub(r"\s*<link\s+rel='shortlink'[^>]*/?>", '', content)
    content = re.sub(r'\s*<link\s+rel="shortlink"[^>]*/?\s*>', '', content)

    # ── 6. Remove OEmbed discovery links ─────────────────────────────────────
    content = re.sub(r'\s*<link\s+rel="alternate"[^>]*type="application/json\+oembed"[^>]*/?\s*>', '', content)
    content = re.sub(r'\s*<link\s+rel="alternate"[^>]*type="text/xml\+oembed"[^>]*/?\s*>', '', content)

    # ── 7. Remove apple-touch-icon (wp.com) and favicon (wp.com) ─────────────
    content = re.sub(r'\s*<link\s+rel="apple-touch-icon"\s+href="https://s2\.wp\.com[^"]*"[^>]*/?\s*>', '', content)
    content = re.sub(r'\s*<link[^>]*href="https://s1\.wp\.com/i/favicon\.ico"[^>]*/?\s*>', '', content)

    # Add local favicon + apple-touch-icon after </title> if not already present
    if '/assets/images/favicon.ico' not in content and '<title>' in content:
        favicon_html = (
            '\n    <link rel="shortcut icon" type="image/x-icon" href="/assets/images/favicon.ico" sizes="16x16 24x24 32x32 48x48" />'
            '\n    <link rel="icon" type="image/x-icon" href="/assets/images/favicon.ico" />'
            '\n    <link rel="apple-touch-icon" href="/assets/images/webclip.png" />'
        )
        content = content.replace('</title>', '</title>' + favicon_html, 1)

    # ── 8. Remove opensearch link (points to s1.wp.com) ──────────────────────
    content = re.sub(r'\s*<link\s+rel="search"[^>]*s1\.wp\.com[^>]*/?\s*>', '', content)

    # ── 9. Replace / remove external CSS <link> tags ─────────────────────────
    def replace_css_link(m):
        full_tag = m.group(0)
        href = m.group(1)

        # Check drop list first
        if url_matches_prefix(href, DROP_CSS_URL_PREFIXES):
            return ''

        # Check replacement map
        local = url_local_path(href, CSS_URL_MAP)
        if local:
            return f'<link rel="stylesheet" href="{local}" type="text/css" media="all" />'

        return full_tag  # keep unchanged if not in either list

    content = re.sub(
        r'<link\s[^>]*href="(https://[^"]*(?:s0|s1|s2)\.wp\.com[^"]*)"[^>]*rel="stylesheet"[^>]*/?\s*>',
        replace_css_link, content)
    content = re.sub(
        r'<link\s[^>]*rel="stylesheet"[^>]*href="(https://[^"]*(?:s0|s1|s2)\.wp\.com[^"]*)"[^>]*/?\s*>',
        replace_css_link, content)

    # ── 10. Replace / remove external JS <script src> tags ───────────────────
    def replace_script_src(m):
        full_tag = m.group(0)
        src = m.group(1)

        # Check drop list
        if url_matches_prefix(src, DROP_JS_URL_PREFIXES):
            return ''

        # Check replacement map
        local = url_local_path(src, JS_URL_MAP)
        if local:
            # Preserve attributes: type=module, defer, async
            attrs = ''
            if 'type="module"' in full_tag:
                attrs += ' type="module"'
            if 'defer' in full_tag:
                attrs += ' defer'
            if 'async' in full_tag:
                attrs += ' async'
            return f'<script src="{local}"{attrs}></script>'

        return full_tag

    content = re.sub(
        r'<script\s[^>]*src="(https://[^"]*(?:s0|s1|s2)\.wp\.com[^"]*)"[^>]*>\s*</script>',
        replace_script_src, content)
    # Also handle the stats.wp.com w.js (http:// not https://)
    content = re.sub(
        r'\s*<script\s[^>]*src="http://stats\.wp\.com/[^"]*"[^>]*>\s*</script>',
        '', content)

    # ── 11. Replace interactivity modulepreload link ──────────────────────────
    content = re.sub(
        r'<link\s[^>]*rel="modulepreload"[^>]*href="https://s0\.wp\.com/[^"]*build-module/interactivity[^"]*"[^>]*/?\s*>',
        '<link rel="modulepreload" href="/assets/js/wp-interactivity.js" />',
        content)

    # ── 12. Update importmap for @wordpress/interactivity ────────────────────
    # The file content has literal \/ sequences (JSON escaping of /)
    # So we need to match and replace that pattern
    content = re.sub(
        r'("@wordpress\\/interactivity":\s*")https:[^"]+interactivity[^"]*(")',
        r'\1/assets/js/wp-interactivity.js\2',
        content)

    # ── 13. Remove inline scripts referencing wp.com that aren't needed ──────

    # Jetpack block assets base URL
    content = re.sub(
        r'\s*<script\s+id="jetpack-blocks-assets-base-url-js-before">\s*var\s+Jetpack_Block_Assets_Base_Url\s*=.*?</script>',
        '', content, flags=re.DOTALL)

    # actionbar data
    content = re.sub(
        r'\s*<script\s+id="wpcom-actionbar-placeholder-js-extra">\s*var\s+actionbardata\s*=.*?</script>',
        '', content, flags=re.DOTALL)

    # Jetpack MU wpcom settings
    content = re.sub(
        r'\s*<script\s+id="jetpack-mu-wpcom-settings-js-before">\s*var\s+JETPACK_MU_WPCOM_SETTINGS\s*=.*?</script>',
        '', content, flags=re.DOTALL)

    # rltInitialize call (from rlt-proxy-js-after)
    content = re.sub(
        r'\s*<script\s+id="rlt-proxy-js-after">\s*rltInitialize\(.*?\);\s*</script>',
        '', content, flags=re.DOTALL)

    # wp.i18n setLocaleData – keep this one (harmless inline)

    # _tkq / _stq analytics script (stats/tracking)
    content = re.sub(
        r'\s*<script[^>]*>\s*_tkq\s*=.*?_stq\.push\(\["clickTrackerInit"[^\]]*\]\);\s*</script>',
        '', content, flags=re.DOTALL)

    # wpcom_reblog function (WordPress-specific share functionality)
    content = re.sub(
        r'\s*<script[^>]*>\s*\(function\s*\(\)\s*\{\s*var\s+wpcom_reblog\s*=.*?window\.wpcom_reblog\s*=\s*wpcom_reblog;\s*\}\)\(\);\s*</script>',
        '', content, flags=re.DOTALL)

    # Actionbar dynamic loader (loads actionbar.css + actionbar.js on load)
    content = re.sub(
        r'\s*<script>\s*window\.addEventListener\("load",\s*function\s*\(event\)\s*\{.*?actionbar.*?\}\s*\);\s*</script>',
        '', content, flags=re.DOTALL)

    # marketingbar script (_tkq recordEvent)
    content = re.sub(
        r'\s*<script[^>]*>\s*window\._tkq\s*=.*?document\.querySelectorAll\("#marketingbar.*?\}\);\s*</script>',
        '', content, flags=re.DOTALL)

    # getMobileUserAgentInfo script (fires pixel.wp.com beacon)
    content = re.sub(
        r'\s*<script>\s*\(function\s*\(\)\s*\{\s*function\s+getMobileUserAgentInfo.*?document\.addEventListener\("DOMContentLoaded",\s*getMobileUserAgentInfo\);\s*\}\)\(\);\s*</script>',
        '', content, flags=re.DOTALL)

    # bilmur performance measurement script tag
    content = re.sub(
        r'\s*<script\s[^>]*id="bilmur"[^>]*src="[^"]*bilmur[^"]*"[^>]*>\s*</script>',
        '', content)

    # ── 14. Remove pixel.wp.com tracking image + noscript wrapper ────────────
    content = re.sub(
        r'\s*<noscript\s*>\s*<img\s+src="https://pixel\.wp\.com/[^"]*"[^>]*/?\s*>\s*</noscript>',
        '', content, flags=re.DOTALL)
    content = re.sub(
        r'\s*<img\s+src="https://pixel\.wp\.com/[^"]*"[^>]*/?\s*>',
        '', content)

    # ── 15. Remove marketingbar div + contents ───────────────────────────────
    content = re.sub(
        r'\s*<div\s+id="marketingbar"[^>]*>.*?</div>\s*(?=\n|<)',
        '', content, flags=re.DOTALL)

    # ── 16. Remove EU cookie law widget ──────────────────────────────────────
    content = re.sub(
        r'\s*<div\s+class="widget widget_eu_cookie_law_widget">.*?</div>\s*</div>',
        '', content, flags=re.DOTALL)

    # ── 17. Remove CCPA disclosure boilerplate ────────────────────────────────
    content = re.sub(
        r'\s*<!-- CCPA \[start\] -->.*?<!-- CCPA \[end\] -->',
        '', content, flags=re.DOTALL)

    # ── 18. Remove og:image pointing to s0.wp.com/i/blank.jpg ────────────────
    content = re.sub(
        r'\s*<meta\s+property="og:image"\s+content="https://s0\.wp\.com/i/blank\.jpg"[^>]*/?\s*>',
        '', content)
    content = re.sub(
        r'\s*<meta\s+property="og:image:alt"[^>]*/?\s*>',
        '', content)

    # ── 19. Remove WordPress.com generator meta ───────────────────────────────
    content = re.sub(r'\s*<meta\s+name="generator"\s+content="WordPress\.com"[^>]*/?\s*>', '', content)

    # ── 20. Remove EditURI/RSD link ───────────────────────────────────────────
    content = re.sub(r'\s*<link\s+rel="EditURI"[^>]*/?\s*>', '', content)

    # ── 21. Remove fb:app_id meta (Facebook tracking) ────────────────────────
    content = re.sub(r'\s*<meta\s+property="fb:app_id"[^>]*/?\s*>', '', content)

    # ── 22. Remove WordPress.com actionbar (follow/subscribe bar) ────────────
    content = remove_balanced_div(content, 'actionbar')

    # ── 23a. Remove comment-like-js-extra script (loads swipe.js from wp.com) ─
    content = re.sub(
        r'\s*<script\s+id="comment-like-js-extra">.*?</script>',
        '', content, flags=re.DOTALL)

    # ── 23b. Remove jetpack carousel configuration script ─────────────────────
    content = re.sub(
        r'\s*<script\s+id="jetpack-carousel-js-extra">.*?</script>',
        '', content, flags=re.DOTALL)

    # Remove any remaining inline scripts that load wp.com resources dynamically
    # (jetpackSwiperLibraryPath, etc.)
    content = re.sub(
        r'\s*<script[^>]*>\s*var\s+jetpackSwiperLibraryPath\s*=.*?</script>',
        '', content, flags=re.DOTALL)

    # ── 24. Remove TTF font references to s2.wp.com in inline @font-face ─────
    # Remove just the TTF src line(s) from @font-face rules
    content = re.sub(
        r'\s*src:\s*url\("https://s2\.wp\.com/[^"]*\.ttf[^"]*"\)\s*format\("truetype"\)\s*;?',
        '', content)

    # ── 25. Deduplicate consecutive blank lines ───────────────────────────────
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content


def main():
    # Find all HTML files to process (exclude backup/, assets/, tools/)
    skip_dirs = {'backup', 'assets', 'tools', 'bgplg'}

    html_files = []
    for dirpath, dirnames, filenames in os.walk(HTDOCS):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if fn.endswith('.html'):
                html_files.append(os.path.join(dirpath, fn))

    html_files.sort()
    print(f"Processing {len(html_files)} HTML files...")

    changed = 0
    for fpath in html_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            original = f.read()

        processed = process_html(original, fpath)

        if processed != original:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(processed)
            print(f"  UPDATED: {fpath.replace(HTDOCS, '')}")
            changed += 1
        else:
            print(f"  unchanged: {fpath.replace(HTDOCS, '')}")

    print(f"\nDone. {changed}/{len(html_files)} files updated.")


if __name__ == '__main__':
    main()
