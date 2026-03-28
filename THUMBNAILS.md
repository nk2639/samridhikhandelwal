# Changing Series Thumbnails on the Works Page

The Works page (`gallery/index.html`) displays a grid of 9 cards, each linking to a series page. Each card shows a thumbnail image.

## To change a thumbnail

1. Open `gallery/index.html`
2. Find the `<a class="work-card">` block for the series you want to update
3. Change the `src` attribute of the `<img>` tag inside that block

The image path should be relative to the site root, e.g.:
```
/wp-content/uploads/2024/10/img_0914-1.jpg
```

All artwork images are in `wp-content/uploads/2024/09/` or `wp-content/uploads/2024/10/`.

## Current thumbnail assignments

| Series | Thumbnail path |
|--------|---------------|
| Can You See Me, Can You Feel Me | `/wp-content/uploads/2024/10/img_0914-1.jpg` |
| Unveiling the Veil | `/wp-content/uploads/2024/10/img_9073-12dff.jpg` |
| Unaware Desires | `/wp-content/uploads/2024/09/img_2302-1.jpg` |
| Empiricism (Inside Out) | `/wp-content/uploads/2024/10/2e9164b0-5208-4b97-9d28-d9649fc83c09-1.jpg` |
| Breach, Escape, Miss | `/wp-content/uploads/2024/10/img_5022-12dff.jpg` |
| Reciprocity Failure | `/wp-content/uploads/2024/09/img_50102dff.jpg` |
| Trapped with Shadows | `/wp-content/uploads/2024/10/img_7261-12dff.jpg` |
| Veils of Thought | `/wp-content/uploads/2024/09/samridhi_khandelwal_veils_of_thought_screen_print_on_paper-12dff.jpg` |
| Earlier Works | `/wp-content/uploads/2024/10/img_1175-12dff.jpg` |
