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

Push to main branch. Vercel auto-deploys.

---

## Setup commands (run these once)

```bash
# 1. Go into the project folder
cd ~/Desktop/narender-xyz    # or wherever you saved it

# 2. Initialise git
git init
git add .
git commit -m "Initial commit — narender.xyz"

# 3. Create repo on GitHub (do this in browser: github.com/new)
#    Name it: narender-xyz
#    Keep it private if you want
#    Do NOT initialise with README

# 4. Connect and push
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/narender-xyz.git
git branch -M main
git push -u origin main

# 5. Go to vercel.com
#    Sign in with GitHub
#    Click "Add New Project"
#    Import narender-xyz repo
#    Framework preset: Other (it's plain HTML)
#    Click Deploy

# 6. In Vercel dashboard: Settings > Domains > Add narender.xyz
#    Vercel gives you nameservers like:
#      ns1.vercel-dns.com
#      ns2.vercel-dns.com
#    Go to your domain registrar and replace existing nameservers with these

# DNS propagates in 10 to 30 minutes. HTTPS is automatic.
```

## After setup — every future update

```bash
# Make your changes to any file, then:
git add .
git commit -m "describe what you changed"
git push

# Vercel detects the push and deploys in ~30 seconds
```

## Before going live — remember to

- [ ] Replace YOUR-HANDLE in footer links with your real LinkedIn and X URLs
- [ ] Submit narender.xyz to Google Search Console
- [ ] Add narender.xyz to Bing Webmaster Tools
- [ ] Verify ownership in Google Search Console (Vercel makes this easy via DNS)
