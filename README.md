# Samridhi Khandelwal — Art Portfolio

Personal portfolio website for **Samridhi Khandelwal**, an interdisciplinary contemporary artist from India, currently based in the USA. The site is live at [samridhiart.uk.eu.org](https://samridhiart.uk.eu.org).

---

## About the Artist

Samridhi Khandelwal holds an MFA in Painting from Coventry University, UK (2018) and a BFA in Painting from Amity University, India (2015). Her practice explores the interplay between personal experience and inner consciousness — using shadows, urban landscapes, and a palette of earthly and neutral tones to evoke existential questioning and deep emotional response.

She works across painting, laser cutting, collage, and printmaking, drawing from Freudian insights into the unconscious to examine the continuum between conscious and unconscious perception. In 2018 she was honoured with the **Finext National Award**.

> *"Unexpressed emotions will never die; they are buried alive and will come forth later."* — Anaïs Nin

---

## Series & Works

| Series | Description |
|--------|-------------|
| [Gallery](gallery/) | Main portfolio overview |
| [Earlier Works](earlier-works/) | Formative works |
| [Reciprocity Failure](reciprocity-failure/) | Laser cut & oil on wood |
| [Reciprocity Failure 2](reciprocity-failure-2/) | Continuation of the series |
| [Veils of Thought](veils-of-thought/) | Screen prints on paper |
| [Empiricism Inside Out](empiricism-inside-out/) | Exploration of perception |
| [Trapped with Shadows](trapped-with-shadows/) | Shadow & urban landscape |
| [Unknown Desires](unknown-desires/) | The unconscious rendered visible |
| [Breach / Escape / Miss](breach-escape-miss/) | Identity and rupture |
| [Can You See Me, Can You Feel Me](can-you-see-me-can-you-feel-me/) | Presence and absence |

---

## Technical Stack

The site is a **static HTML website** self-hosted on OpenBSD, originally mirrored from WordPress.com using HTTrack (May 2025).

```
Internet → relayd (port 443, TLS termination)
         → httpd (127.0.0.1:8080, static files)
         → /var/www/htdocs/
```

- **relayd** — TLS termination and security headers (HSTS, CSP)
- **httpd** — static file serving; HTTP redirects to HTTPS
- **TLS** — managed via ACME (`acme-client`)
- No build system, no package manager, no backend — plain `.html` files edited directly

---

## Repository Structure

```
/
├── gallery/                  # Main portfolio gallery
├── earlier-works/            # Older works
├── breach-escape-miss/       # Series pages (each self-contained)
├── empiricism-inside-out/
├── veils-of-thought/
├── can-you-see-me-can-you-feel-me/
├── trapped-with-shadows/
├── unknown-desires/
├── reciprocity-failure/
├── reciprocity-failure-2/
├── about/                    # Artist biography
├── contact/                  # Contact page
├── assets/                   # Local CSS, JS, and images
└── wp-content/uploads/       # Artwork images (JPEG)
```

---

## Contact

Visit the [contact page](https://samridhiart.uk.eu.org/contact/) on the live site.
# website
# website
# website
