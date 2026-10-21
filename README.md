# narender.xyz

Personal site and blog for Narender Charan — SEO and GEO Specialist.

## File structure

```
narender-xyz/
├── index.html                  # Landing page
├── style.css                   # Shared styles for all pages
├── blog/
│   ├── index.html              # Blog listing
│   └── what-is-geo-.../
│       └── index.html          # First post (template for future posts)
└── README.md
```

## Adding a new blog post

1. Create a new folder inside /blog/ with a slug like `how-to-rank-defi-content`
2. Copy an existing post's index.html into it
3. Update the title, meta description, canonical URL, content, and schema JSON
4. Add the post card to blog/index.html

## Deploy

Hosted on Cloudflare Workers as an assets-only Worker (`wrangler.jsonc`).
Pushing to GitHub does NOT deploy. Deploy from this machine:

```bash
npm run deploy
```

That runs three steps in order:

1. `npm run build` copies the public files into `dist/` (`scripts/build.mjs`).
   It uses an allowlist, so `.env`, `node_modules` and the Python scripts
   never ship. **A new top-level public file must be added to the list in
   `scripts/build.mjs`**, or it will not be served. Anything under `blog/` or
   `img/` is picked up automatically.
2. `wrangler deploy` uploads `dist/`.
3. `npm run smoke` checks page content on https://narender.xyz, and checks
   that `.env` and the source files return 404.

`npm run smoke -- https://narender-xyz.nscharan007.workers.dev` checks the
workers.dev copy. Cache headers live in `_headers`.

Cloudflare serves `/blog/` from `blog/index.html` and redirects `/blog` to
`/blog/` itself (`html_handling: auto-trailing-slash`). No rewrites needed.

---

## Before going live — remember to

- [ ] Replace YOUR-HANDLE in footer links with your real LinkedIn and X URLs
- [ ] Submit narender.xyz to Google Search Console
- [ ] Add narender.xyz to Bing Webmaster Tools
- [ ] Verify ownership in Google Search Console (TXT record already on the Cloudflare zone)
