#!/usr/bin/env python3
"""
narender.xyz Blog Publisher
- Uses DeepSeek to generate SEO/GEO/Web3 blog posts
- Saves posts as static HTML to blog/[slug]/index.html
- Auto-updates sitemap.xml after each run
- Interactive: shows candidates, you pick, confirm, generate
"""

import os
import re
import time
import random
import math
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_KEY"]
CANDIDATE_COUNT  = int(os.environ.get("CANDIDATE_COUNT", "12"))
AUTO_MODE        = os.environ.get("AUTO_MODE", "false").lower() == "true"
POSTS_PER_RUN    = int(os.environ.get("POSTS_PER_RUN", "3"))

SITE_ROOT   = Path(__file__).parent
BLOG_DIR    = SITE_ROOT / "blog"
SITEMAP     = SITE_ROOT / "sitemap.xml"
SITE_URL    = "https://narender.xyz"

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)


# ── Cover image generator ──────────────────────────────────────────────────────

COVER_SCRIPT = SITE_ROOT / "generate-cover.js"

def generate_cover(title, category, out_dir):
    """
    Calls generate-cover.js via Node to render a branded cover.jpg.
    Returns cover_path or None on failure.
    """
    import subprocess
    cover_path = out_dir / "cover.jpg"
    try:
        result = subprocess.run(
            ["node", str(COVER_SCRIPT), title, category, str(cover_path)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"  Cover error: {result.stderr.strip()}")
            return None
        print(f"  Cover generated: {cover_path.name}")
        return cover_path
    except Exception as e:
        print(f"  Cover error: {e}")
        return None


# ── Topic bank ─────────────────────────────────────────────────────────────────

TOPICS = [

    # ── HIRING / INTERVIEW CLUSTER ────────────────────────────────────────────
    # Pillar: questions to ask before hiring a GEO specialist
    # Each post answers one question in full depth, written as the expert being hired

    {
        "slug": "questions-to-ask-before-hiring-geo-specialist",
        "title": "10 Questions to Ask Before Hiring a GEO Specialist",
        "category": "geo",
        "type": "pillar",
        "angle": """
This is the pillar post for the hiring cluster. Cover all 10 questions:
1. What brands are winning in AI search right now, and why?
2. If you had zero backlink budget, how would you improve visibility in ChatGPT and Perplexity?
3. What content types are most likely to be cited by LLMs?
4. How do you measure GEO success when AI referral traffic is hard to track?
5. What does your first 90-day GEO roadmap look like?
6. What role do entities play in modern SEO and AI search?
7. What on our site would you remove, merge, rewrite, or expand first?
8. How do you make our brand the source AI systems quote instead of competitors?
9. Which third-party sites would you want us mentioned on in the next six months?
10. If you were launching our company from scratch today knowing AI search exists, what would you do differently?
For each question, give a 2-3 sentence framing of what a strong answer looks like versus a weak one.
End with the bonus question: if given $10,000 with one KPI — maximize the probability ChatGPT recommends our brand in six months — how would you spend it?
""",
    },
    {
        "slug": "what-brands-are-winning-in-ai-search-and-why",
        "title": "What Brands Are Winning in AI Search Right Now, and Why",
        "category": "geo",
        "type": "deep-dive",
        "angle": """
Answer question 1 from the hiring cluster in full depth.
The brands winning in AI search share specific traits: original research, consistent entity presence across the web,
structured content, high-authority third-party mentions, and FAQ-formatted pages.
Give real examples. Analyse why AI systems cite them. Make it actionable.
""",
    },
    {
        "slug": "how-to-improve-ai-search-visibility-without-backlink-budget",
        "title": "How to Improve Your Visibility in ChatGPT and Perplexity Without a Backlink Budget",
        "category": "geo",
        "type": "deep-dive",
        "angle": """
Answer question 2 from the hiring cluster. Zero budget, maximum GEO impact.
Cover: fixing technical foundations (sitemap, robots.txt, llms.txt, agents.md, schema),
restructuring existing content for AI retrieval, entity consistency across platforms,
Reddit presence as credibility signal, comparison content as AI-friendly format,
FAQ sections that map to how people prompt AI systems.
""",
    },
    {
        "slug": "what-content-types-do-llms-actually-cite",
        "title": "What Content Types Do LLMs Actually Cite? The Honest Answer",
        "category": "geo",
        "type": "deep-dive",
        "angle": """
Answer question 3 from the hiring cluster.
Types AI systems cite most: original research with specific numbers, comparison pages,
definitions and explainers, FAQ content, industry statistics, first-person experience posts,
structured how-to guides with clear steps.
Types that rarely get cited: generic listicles, thin aggregator content, hype-driven copy,
content without a clear author entity, Twitter threads repurposed as blog posts.
Be specific. Give examples of each type. Make the distinction clear.
""",
    },
    {
        "slug": "how-to-measure-geo-success",
        "title": "How to Measure GEO Success When AI Referral Traffic Is Impossible to Track",
        "category": "geo",
        "type": "deep-dive",
        "angle": """
Answer question 4 from the hiring cluster. This is a real pain point — GA4 does not show ChatGPT referrals cleanly.
Metrics that actually work: branded search volume growth in GSC, share of voice in AI answers
(manual testing with prompts), third-party mention tracking, citation tracking by asking AI systems directly,
conversion rate from branded traffic, newsletter signups from organic.
Explain each metric, how to track it, and what movement means.
""",
    },
    {
        "slug": "90-day-geo-roadmap",
        "title": "The 90-Day GEO Roadmap: What I Do in the First Three Months",
        "category": "geo",
        "type": "deep-dive",
        "angle": """
Answer question 5 from the hiring cluster. Written in first person as Narender Charan.
Month 1: Technical foundations. sitemap.xml, robots.txt, llms.txt, agents.md, GSC setup,
schema markup, canonical URLs, entity consistency audit across all platforms.
Month 2: Content restructuring. Audit existing pages, add FAQ sections, rewrite intros to answer
the implied question in paragraph one, build first comparison posts, start Reddit presence.
Month 3: Authority building. Guest posts, directory listings, Product Hunt, G2, Alternatives.co,
digital PR outreach, first original research piece.
Be specific about timelines, tools, and what done looks like for each phase.
""",
    },
    {
        "slug": "how-to-make-your-brand-the-source-ai-quotes",
        "title": "How to Make Your Brand the Source AI Systems Quote Instead of Your Competitors",
        "category": "geo",
        "type": "deep-dive",
        "angle": """
Answer question 8 from the hiring cluster — one of the most important.
This comes down to: differentiation through original data and opinions, being the primary source
not an aggregator, entity presence that AI can verify across multiple platforms,
structured content that is easy to extract, and third-party mentions that corroborate your authority.
Cover each in depth. Include the concept of becoming a "citable entity" not just a "ranked page".
""",
    },
    {
        "slug": "the-10000-dollar-geo-bet",
        "title": "If You Gave Me $10,000 to Make ChatGPT Recommend My Brand in Six Months",
        "category": "geo",
        "type": "opinion",
        "angle": """
The bonus question from the hiring cluster, treated as a standalone opinion piece.
Written in first person as Narender Charan. How would I actually spend $10,000 with one KPI:
maximize probability that ChatGPT recommends my brand in six months?
Break it down: original research piece with real data ($2k), digital PR campaign targeting
industry publications ($3k), structured comparison content built in-house ($0, just time),
directory and review platform presence ($500), Reddit community presence ($0, time),
entity building across platforms ($0, time), technical GEO foundations ($0, time),
remaining budget for one strong guest post on a high-authority domain ($2k).
Be opinionated. Explain the reasoning behind each allocation.
""",
    },

    # ── GEO PRINCIPLES CLUSTER ────────────────────────────────────────────────

    {
        "slug": "stop-thinking-keywords-start-thinking-prompts",
        "title": "Stop Thinking in Keywords. Start Thinking in Prompts.",
        "category": "geo",
        "type": "opinion",
        "angle": """
The fundamental mindset shift for GEO. Keywords are what people type into Google.
Prompts are what people ask AI. They are longer, more conversational, more intent-specific.
"best seo tool" is a keyword. "what SEO tool should I use if I am a solo founder with no budget" is a prompt.
Optimising for the keyword gets you a ranking. Optimising for the prompt gets you a citation.
Cover how to research prompts (ask AI what people ask about your topic),
how to structure content around prompt intent, and why this changes everything about
how you write titles, intros, and FAQ sections.
""",
    },
    {
        "slug": "seo-foundation-geo-building",
        "title": "SEO Is the Foundation. GEO Is What You Build on Top of It.",
        "category": "geo",
        "type": "explainer",
        "angle": """
The relationship between SEO and GEO is not competitive, it is sequential.
You cannot have good GEO without SEO foundations: indexable pages, clean structure,
authoritative content, entity signals. GEO adds the layer that AI systems read:
FAQ structure, entity clarity, citable claims, prompt-aligned content.
A site with good SEO but no GEO gets found by Google but not cited by AI.
A site with GEO attempts but broken SEO foundations gets neither.
Explain the full stack with concrete examples of what each layer looks like in practice.
""",
    },
    {
        "slug": "reverse-engineer-the-ai-answer",
        "title": "Reverse-Engineer the AI Answer: How to Build Content That Gets Cited",
        "category": "geo",
        "type": "how-to",
        "angle": """
The core GEO content strategy. Start with the question a potential client asks AI.
"Who is a good GEO specialist for a DeFi protocol?" Then ask: what would the ideal AI answer
to that question look like? Then build content that IS that answer.
Walk through the full process: identifying the prompts your buyers use,
mapping them to content gaps, structuring content so the first paragraph answers the question,
and testing whether it works by asking AI systems directly.
""",
    },
    {
        "slug": "entity-before-content",
        "title": "Entity Before Content: Why AI Cannot Cite a Brand It Cannot Verify",
        "category": "geo",
        "type": "explainer",
        "angle": """
Most brands start with content. They should start with entity.
An entity is how AI systems understand who you are: your name, role, credentials,
consistent presence across platforms, third-party corroboration.
If your name appears differently on your site, LinkedIn, Twitter, and guest posts,
AI systems cannot confidently attribute content to you. The result: you write great content
that gets cited without your name attached, or not cited at all.
Cover what entity building looks like in practice: consistent bio, consistent positioning,
platform presence, Wikipedia/Wikidata consideration, schema markup, author pages.
""",
    },
    {
        "slug": "specificity-is-the-signal",
        "title": "Specificity Is the Signal: Why Vague Content Never Gets Cited by AI",
        "category": "geo",
        "type": "explainer",
        "angle": """
The single most actionable GEO principle. AI systems extract and cite specific, verifiable claims.
They skip vague generalisations. "Increase your traffic" is noise. "10,000 impressions in three weeks
on a zero-DA domain" is a citation. Cover why specificity signals authority to AI,
how to audit your existing content for vague claims and replace them with specific ones,
and how to build a habit of writing with numbers, names, timeframes, and concrete outcomes.
Include examples of vague vs specific versions of the same claim.
""",
    },
    {
        "slug": "reddit-is-credibility-not-a-backlink",
        "title": "Reddit Is Credibility, Not a Backlink: How to Build GEO Authority on Reddit",
        "category": "geo",
        "type": "how-to",
        "angle": """
One of the most counterintuitive and important GEO insights.
AI systems train heavily on Reddit. A genuine, credible presence in relevant subreddits
builds the kind of third-party corroboration that makes AI confident in citing you.
Cover: which subreddits matter (r/SEO, r/entrepreneur, r/web3, r/defi, r/startups),
what kind of posts work (real wins with specifics, honest failures, learnings, not link drops),
the "I built X here's the link" trap and why it backfires,
and how to think about Reddit as a long-term credibility signal, not a traffic hack.
Written from personal experience. Include the hard-learned lesson.
""",
    },
    {
        "slug": "comparison-content-is-ai-catnip",
        "title": "Comparison Content Is AI Catnip: How to Write Pages That Get Cited Every Time",
        "category": "seo",
        "type": "how-to",
        "angle": """
AI systems love structured, factual, side-by-side content because it is easy to extract and cite.
Cover the three formats: 1 vs 1 (Brand A vs Brand B), many vs one (all competitors vs your brand),
category roundup (best tools for X). For each format, explain what makes it citable:
specific comparison criteria, honest pros and cons, clear structure with headers,
tables where appropriate. Include how to choose what to compare, how to be fair enough
to be credible but clear enough to be useful. Comparison content also has a long shelf life —
update it quarterly and it compounds.
""",
    },
    {
        "slug": "backlinks-are-grunt-work",
        "title": "Backlinks Are Grunt Work, Not Budget Work: The Honest Guide to Building Authority",
        "category": "seo",
        "type": "how-to",
        "angle": """
Most people think backlinks require money. They require consistency.
Cover the full hierarchy: low-hanging fruit first (Product Hunt, Trustpilot, G2,
Alternatives.co, Crunchbase, relevant directories — all free, done in a week),
then the medium effort plays (podcast guest spots, community contributions, forum expertise),
then the long game (guest posts on industry publications, original research that gets cited,
digital PR). For each tier, explain what done looks like, how long it takes, and what to expect.
The point: none of this requires budget. All of it requires showing up daily.
""",
    },
    {
        "slug": "first-paragraph-is-your-geo-bet",
        "title": "The First Paragraph Is Your Entire GEO Bet. Do Not Waste It.",
        "category": "geo",
        "type": "opinion",
        "angle": """
AI systems often pull the opening of a page when generating answers.
If your first paragraph does not directly answer the implied question, you lose the citation
to whoever's does. Cover the before/after: most blog posts start with throat-clearing,
context-setting, or a story. GEO-optimised posts start with the answer.
Show examples of both. Explain how to rewrite a slow intro into a citation-ready first paragraph.
Include the principle: write for the AI summary, not the full read. Structure every post
so someone who only reads the AI's three-sentence summary still gets your core argument
and your name attached to it.
""",
    },
    {
        "slug": "geo-is-distribution-not-just-content",
        "title": "GEO Is a Distribution Strategy, Not Just a Content Strategy",
        "category": "geo",
        "type": "opinion",
        "angle": """
The common mistake: treating GEO as a writing style. It is that, but it is also where your content
lives beyond your own site. AI systems build confidence in entities through corroboration:
your site says you are an expert, Reddit confirms it, a guest post on an industry publication
agrees, your G2 profile exists, your LinkedIn bio matches. All of these signals together make
an AI comfortable citing you. A single well-written page on your own site is not enough.
Cover the full distribution checklist: own site, LinkedIn, X, Reddit, guest posts,
directories, review platforms, podcast mentions. Each one is a GEO signal, not just an SEO play.
""",
    },

    # ── WEB3 SPECIFIC CLUSTER ─────────────────────────────────────────────────

    {
        "slug": "why-web3-content-never-gets-cited-by-ai",
        "title": "Why Web3 Content Almost Never Gets Cited by AI (and How to Fix It)",
        "category": "web3",
        "type": "explainer",
        "angle": """
Most crypto content is written for Twitter: threads, hype, price speculation, community updates.
None of that gets cited by AI. AI systems want structured, factual, entity-clear content.
Cover the specific Web3 content mistakes: anonymous authorship (no entity to cite),
hype-driven copy (no verifiable claims), thread-first content (bad structure for retrieval),
no schema markup, no FAQ sections. Then cover what Web3 GEO looks like done right:
technical explainers with clear definitions, comparison pages for protocols,
named authorship, structured documentation, FAQ sections on every product page.
""",
    },
    {
        "slug": "geo-for-defi-protocols",
        "title": "GEO for DeFi Protocols: How to Get ChatGPT to Recommend Your Protocol",
        "category": "web3",
        "type": "how-to",
        "angle": """
Specific GEO playbook for DeFi protocols. The opportunity: most DeFi projects have zero GEO strategy.
The window to establish authority early is open.
Cover: protocol documentation structured for AI retrieval, comparison pages vs competitors,
tokenomics explainers written as definitions not marketing copy, FAQ sections on every feature page,
named authorship on technical content, third-party mentions through DeFi publications and forums.
Include how to think about entity building for a protocol (the protocol as entity, key contributors as entities).
""",
    },
    {
        "slug": "growing-crypto-twitter-from-zero",
        "title": "How I Grew a Bitcoin DeFi Protocol's X Account from Zero to 100k: The Actual Strategy",
        "category": "web3",
        "type": "case-study",
        "angle": """
First-person case study from Narender Charan's work at Velar.
No paid promos. No follow-for-follow. No giveaway farming.
The actual strategy: narrative-driven content that explained the protocol to non-technical users,
consistent posting cadence (3-5 posts per day), thread format for technical explainers,
community engagement that was genuine not transactional, timing posts around market events,
cross-promotion through protocol partnerships.
What did not work: generic crypto content, price commentary, hype without substance.
Be specific about what was posted, how often, what got traction, what flopped.
""",
    },

]


# ── Helpers ────────────────────────────────────────────────────────────────────

def estimate_read_time(text):
    words = len(text.split())
    return max(4, math.ceil(words / 200))


def get_published_slugs():
    return {p.parent.name for p in BLOG_DIR.glob("*/index.html")
            if p.parent.name != "what-is-geo-generative-engine-optimisation"}


def format_date_display(dt):
    return dt.strftime("%B %Y")


def format_date_iso(dt):
    return dt.strftime("%Y-%m-%d")


def slug_to_email_subject(title):
    return title.replace(" ", "%20").replace("?", "").replace(":", "")[:60]


CAT_CLASSES = {
    "geo":   "cat-geo",
    "seo":   "cat-seo",
    "web3":  "cat-web3",
    "gtm":   "cat-gtm",
}

CAT_LABELS = {
    "geo":  "GEO",
    "seo":  "SEO",
    "web3": "Web3",
    "gtm":  "GTM",
}


# ── Prompt builder ─────────────────────────────────────────────────────────────

VOICE_PRINCIPLES = """
VOICE AND TONE — follow these exactly:

You are writing as Narender Charan: SEO and GEO specialist, Web3 content strategist, crypto degen.
8 years building audiences and ranking content. Grew Velar's X account from zero to 100k followers.
Ranked RemoteStack at number one for its core keyword in weeks on a new domain with zero backlinks.
Earned organic citations in ChatGPT, Perplexity, and Gemini. Remote-first since 2017.

WRITING PRINCIPLES:
1. Answer the question in the first paragraph. No preamble, no context-setting, no throat-clearing.
   The first sentence should be the core answer. AI systems pull opening paragraphs — make yours citable.
2. Be specific. Numbers, names, timeframes, and concrete outcomes beat vague generalisations every time.
   "Increase traffic" is noise. "10,000 impressions in three weeks on a zero-DA domain" is a citation.
3. First-person where relevant. This is written by someone who has done the work, not an observer.
4. No fluff. Every sentence should add information. If a sentence could be cut without losing meaning, cut it.
5. Actionable, not theoretical. End sections with something the reader can do, not just think about.
6. Direct and confident. Not aggressive, not humble-bragging. Just clear.
7. No em-dashes. Use commas, colons, or restructure the sentence.
8. No AI-sounding language: do not use "delve", "leverage", "game-changer", "paradigm", "holistic",
   "robust", "cutting-edge", "foster", "streamline", or any similar corporate filler words.
9. Short paragraphs. Two to four sentences maximum. White space is your friend.
10. Write for the AI summary. Structure content so the three-sentence AI summary of your post
    still contains your core argument and your name.

OUTBOUND LINKS — include 2 to 4 naturally within the body:
Link to authoritative external sources where relevant. Use proper <a href="..." target="_blank" rel="noopener">anchor text</a> inline.
Good sources to link to depending on topic:
- SEO/GEO: Google Search Central (developers.google.com/search), Moz Blog (moz.com/blog),
  Ahrefs Blog (ahrefs.com/blog), Search Engine Journal (searchenginejournal.com),
  Perplexity (perplexity.ai), Google Search Console (search.google.com/search-console)
- Web3: Ethereum Foundation (ethereum.org), Messari (messari.io), DeFi Llama (defillama.com),
  CoinDesk (coindesk.com), The Block (theblock.co)
- General: Wikipedia for definitions, Reddit threads where genuinely relevant
Anchor text should be descriptive and natural, never "click here" or "read more".
Example: according to <a href="https://developers.google.com/search/docs/fundamentals/how-search-works" target="_blank" rel="noopener">Google's documentation on how search works</a>


- Stop thinking in keywords, start thinking in prompts
- SEO is the foundation, GEO is the building on top
- Reverse-engineer the AI answer — imagine what a buyer asks ChatGPT, then be that answer
- Entity before content — be a verifiable, consistent entity across the web
- Specificity is the signal — vague content never gets cited
- Reddit is credibility, not a backlink channel
- Comparison content is AI catnip
- Backlinks are grunt work, not budget work
- The first paragraph is your GEO bet
- GEO is a distribution strategy, not just a content strategy
"""

def build_prompt(topic):
    return f"""
{VOICE_PRINCIPLES}

---

TASK: Write a complete blog post for narender.xyz.

Title: {topic['title']}
Category: {CAT_LABELS.get(topic['category'], 'SEO')}
Type: {topic['type']}

CONTENT ANGLE AND STRUCTURE:
{topic['angle'].strip()}

---

OUTPUT FORMAT — return a JSON object with exactly these keys:

{{
  "body": "the full HTML body content as a string",
  "cover_alt": "descriptive alt text for the cover image, 10-15 words, describes the visual concept and includes the core topic keyword naturally — written as if describing what someone would see, not just the post title",
  "screenshot_hints": ["short description of screenshot 1 that would add value", "short description of screenshot 2"]
}}

BODY content rules:
- Start directly with the first paragraph that answers the core question. No preamble.
- Use <h2> tags for section headings.
- Use <h3> tags for sub-sections if needed.
- Use <p> tags for paragraphs.
- Use <ul> and <li> for lists.
- Use <strong> for emphasis on key phrases (sparingly).
- Use <blockquote><p>...</p></blockquote> for standout quotes or key insights.
- Where a screenshot would add value, insert this exact placeholder on its own line:
  <!-- SCREENSHOT: brief description | alt: suggested alt text -->
- Do not include the post title as a heading — it is in the HTML template already.
- Do not include a CTA — the template adds it.
- Write between 800 and 1200 words of body content.

Return ONLY the raw JSON. No markdown fences, no explanation.
"""


# ── HTML template ──────────────────────────────────────────────────────────────

def build_html(topic, body, dt, cover=None, cover_alt=""):
    slug      = topic["slug"]
    title     = topic["title"]
    category  = topic["category"]
    cat_class = CAT_CLASSES.get(category, "cat-seo")
    cat_label = CAT_LABELS.get(category, "SEO")
    date_disp = format_date_display(dt)
    date_iso  = format_date_iso(dt)
    read_time = estimate_read_time(body)
    url       = f"{SITE_URL}/blog/{slug}/"
    subj      = slug_to_email_subject(f"Read your post: {title}")

    # Extract first sentence for meta description
    plain = re.sub(r'<[^>]+>', '', body)
    first_sentence = plain.strip().split('.')[0][:160].strip()

    # Cover image block
    if cover:
        img_alt = cover_alt if cover_alt else f"Branded cover image for the post: {title}"
        cover_html = f"""
<div class="post-cover">
  <img src="/blog/{slug}/cover.jpg" alt="{img_alt}" width="1200" height="630" loading="eager">
</div>"""
    else:
        cover_html = ""

    # Convert screenshot placeholders to figure tags
    def replace_screenshot(match):
        full     = match.group(0)
        desc     = re.search(r'SCREENSHOT:\s*(.+?)\s*\|', full)
        alt      = re.search(r'alt:\s*(.+?)\s*-->', full)
        desc_txt = desc.group(1).strip() if desc else "screenshot"
        alt_txt  = alt.group(1).strip() if alt else desc_txt
        img_name = re.sub(r'[^a-z0-9]+', '-', desc_txt.lower())[:40].strip('-')
        return f"""<figure class="post-figure">
  <img src="/blog/{slug}/{img_name}.jpg" alt="{alt_txt}" loading="lazy" width="800" height="450" onerror="this.classList.add('hidden')">
  <figcaption>{alt_txt}</figcaption>
</figure>"""

    body = re.sub(r'<!--\s*SCREENSHOT:.+?-->', replace_screenshot, body)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Narender Charan</title>
  <meta name="description" content="{first_sentence}.">
  <meta name="author" content="Narender Charan">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{first_sentence}.">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE_URL}/blog/{slug}/cover.jpg">
  <meta property="article:author" content="Narender Charan">
  <meta property="article:published_time" content="{date_iso}">
  <link rel="canonical" href="{url}">
  <link rel="stylesheet" href="/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{title}",
    "author": {{ "@type": "Person", "name": "Narender Charan", "url": "https://narender.xyz" }},
    "datePublished": "{date_iso}",
    "publisher": {{ "@type": "Person", "name": "Narender Charan" }},
    "description": "{first_sentence}.",
    "url": "{url}",
    "image": "{SITE_URL}/blog/{slug}/cover.jpg"
  }}
  </script>
</head>
<body>

<nav>
  <div class="nav-inner">
    <a class="nav-logo" href="/">narender<em>.xyz</em></a>
    <div class="nav-right">
      <a class="nav-link" href="/#services">Services</a>
      <a class="nav-link keep" href="/blog/" style="color:var(--text)">Blog</a>
      <a class="nav-cta" href="mailto:nscharan007@gmail.com?subject=Let%27s%20work%20together&body=Hi%20Narender%2C%0A%0AI%20found%20your%20site%20and%20I%27m%20interested%20in%20working%20with%20you.%0A%0AHere%27s%20what%20I%27m%20looking%20for%3A">Get in touch ↗</a>
    </div>
  </div>
</nav>

<div class="post-hero">
  <div class="container">
    <span class="blog-cat {cat_class}" style="margin-bottom:1.5rem;display:inline-block;">{cat_label}</span>
    <h1 style="font-size:clamp(1.8rem,4vw,2.8rem);max-width:720px;">{title}</h1>
    <div class="post-meta">
      <span style="color:var(--muted);font-weight:500;">Narender Charan</span>
      <span class="blog-dot"></span>
      <span>{date_disp}</span>
      <span class="blog-dot"></span>
      <span>{read_time} min read</span>
    </div>
  </div>
</div>
{cover_html}
<div class="post-body container">
{body}
</div>

<div class="post-footer container">
  <h3>Work with Narender Charan</h3>
  <p>SEO and GEO specialist available for freelance and full-time remote work. If you want your content to rank on Google and get cited by AI, one email is the start.</p>
  <a class="cta-sm" href="mailto:nscharan007@gmail.com?subject={subj}&body=Hi%20Narender%2C%0A%0AI%20read%20your%20post%20and%20I%27d%20like%20to%20talk.%0A%0AHere%27s%20what%20I%27m%20working%20on%3A%0A%0A">Email me ↗</a>
</div>

<footer>
  <div class="foot-inner">
    <div class="foot-left">© 2026 Narender Charan · narender.xyz · SEO and GEO Specialist · Remote since 2017</div>
    <div class="foot-links">
      <a href="https://linkedin.com/in/lazylion" target="_blank">LinkedIn</a>
      <a href="https://x.com/0xnarender" target="_blank">X / Twitter</a>
      <a href="mailto:nscharan007@gmail.com">Email</a>
    </div>
  </div>
</footer>

</body>
</html>
"""


# ── Save post ──────────────────────────────────────────────────────────────────

def save_post(topic, html):
    slug    = topic["slug"]
    out_dir = BLOG_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / "index.html"
    filepath.write_text(html, encoding="utf-8")
    print(f"  Saved: {filepath}")
    return filepath


# ── Sitemap updater ────────────────────────────────────────────────────────────

def update_sitemap(new_slugs, dt):
    today = format_date_iso(dt)

    if not SITEMAP.exists():
        print("  sitemap.xml not found, skipping update")
        return

    content = SITEMAP.read_text(encoding="utf-8")

    for slug in new_slugs:
        url = f"{SITE_URL}/blog/{slug}/"
        if url in content:
            continue
        entry = f"""
  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""
        content = content.replace("</urlset>", entry + "\n</urlset>")

    SITEMAP.write_text(content, encoding="utf-8")
    print(f"  sitemap.xml updated with {len(new_slugs)} new URL(s)")


# ── Blog index updater ─────────────────────────────────────────────────────────

def update_blog_index(new_topics, dt):
    """Prepends new post cards to blog/index.html"""
    index_path = BLOG_DIR / "index.html"
    if not index_path.exists():
        print("  blog/index.html not found, skipping index update")
        return

    content = index_path.read_text(encoding="utf-8")
    date_disp = format_date_display(dt)
    cards = ""

    for topic in reversed(new_topics):
        slug      = topic["slug"]
        title     = topic["title"]
        category  = topic["category"]
        cat_class = CAT_CLASSES.get(category, "cat-seo")
        cat_label = CAT_LABELS.get(category, "SEO")
        read_time = 7

        cards += f"""
    <article class="bi-card" data-cat="{category}">
      <a class="bi-card-img" href="/blog/{slug}/">
        <img src="/blog/{slug}/cover.jpg" alt="Cover for {title}" loading="lazy" onerror="this.parentElement.classList.add('no-img')">
      </a>
      <div class="bi-card-body">
        <span class="blog-cat {cat_class}">{cat_label}</span>
        <a class="bi-card-title" href="/blog/{slug}/">{title}</a>
        <div class="bi-meta">
          <span>{date_disp}</span>
          <span class="blog-dot"></span>
          <span>{read_time} min</span>
        </div>
      </div>
    </article>
"""

    insert_marker = '<div class="bi-grid" id="bi-grid">'
    featured_end  = '</article>'

    idx_grid  = content.find(insert_marker)
    idx_feat  = content.find(featured_end, idx_grid)

    if idx_grid != -1 and idx_feat != -1:
        insert_at = idx_feat + len(featured_end)
        content   = content[:insert_at] + cards + content[insert_at:]
        index_path.write_text(content, encoding="utf-8")
        print(f"  blog/index.html updated with {len(new_topics)} new card(s)")
    else:
        print("  Could not find insertion point in blog/index.html")


# ── Generate ───────────────────────────────────────────────────────────────────

def generate_post(topic):
    prompt   = build_prompt(topic)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3500,
        temperature=0.72,
    )
    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if DeepSeek wraps in them anyway
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: treat entire response as body, no image metadata
        print("  Warning: could not parse JSON, treating response as plain body")
        return raw, "", []

    body             = data.get("body", raw)
    cover_alt        = data.get("cover_alt", "")
    screenshot_hints = data.get("screenshot_hints", [])

    return body, cover_alt, screenshot_hints


# ── Topic picker ───────────────────────────────────────────────────────────────

def pick_candidates(n=12):
    published = get_published_slugs()
    available = [t for t in TOPICS if t["slug"] not in published]

    if not available:
        print("All topics have been published!")
        return []

    print(f"  {len(available)} unpublished topics out of {len(TOPICS)} total")

    by_type = {}
    for t in available:
        by_type.setdefault(t["type"], []).append(t)
    for k in by_type:
        random.shuffle(by_type[k])

    candidates, types = [], list(by_type.keys())
    random.shuffle(types)
    while len(candidates) < n and any(by_type.values()):
        for t in types:
            if by_type.get(t) and len(candidates) < n:
                candidates.append(by_type[t].pop(0))

    return candidates[:n]


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    now = datetime.now(timezone.utc)
    print(f"\n[{now.isoformat()}] narender.xyz Blog Publisher starting...")

    candidates = pick_candidates(CANDIDATE_COUNT)
    if not candidates:
        return

    print(f"\n{'='*65}")
    print(f"  TOPIC SUGGESTIONS")
    print(f"{'='*65}")
    for i, t in enumerate(candidates, 1):
        print(f"  {i:2}. [{t['category'].upper():<5} {t['type']:<12}] {t['title']}")
    print(f"{'='*65}")

    if AUTO_MODE:
        topics = candidates[:POSTS_PER_RUN]
        print(f"\nAuto mode: publishing top {POSTS_PER_RUN}")
    else:
        print(f"\nEnter numbers to generate (e.g. 1,3,7) or 'a' for top {POSTS_PER_RUN}:")
        choice = input("> ").strip().lower()
        if choice == "a":
            topics = candidates[:POSTS_PER_RUN]
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                topics  = [candidates[i] for i in indices if 0 <= i < len(candidates)]
            except Exception:
                print("Invalid input, aborting.")
                return

        if not topics:
            print("No topics selected.")
            return

        print(f"\nSelected:")
        for t in topics:
            print(f"  - {t['title']}")
        if input("\nGenerate? (y/n): ").strip().lower() != "y":
            print("Aborted.")
            return

    print(f"\nGenerating {len(topics)} post(s)...\n")
    generated, failed, new_slugs, new_topics = 0, 0, [], []

    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{len(topics)}] {topic['title']}")
        try:
            body, cover_alt, screenshot_hints = generate_post(topic)
            print(f"  Generated {len(body)} chars, ~{estimate_read_time(body)} min read")

            # Generate branded cover image
            out_dir = BLOG_DIR / topic["slug"]
            out_dir.mkdir(parents=True, exist_ok=True)
            cover = generate_cover(topic["title"], topic["category"], out_dir)

            # Print screenshot hints for manual action
            if screenshot_hints:
                print(f"  Screenshot suggestions:")
                for hint in screenshot_hints:
                    print(f"    - {hint}")

            html = build_html(topic, body, now, cover, cover_alt)
            save_post(topic, html)
            new_slugs.append(topic["slug"])
            new_topics.append(topic)
            generated += 1
            if i < len(topics):
                print("  Waiting 4s...")
                time.sleep(4)
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    if new_slugs:
        print()
        update_sitemap(new_slugs, now)
        update_blog_index(new_topics, now)

    print(f"\nDone. Generated: {generated} | Failed: {failed}")
    if generated:
        print(f"""
Next steps:
  cd ~/narender-xyz
  git add .
  git commit -m "blog: add {generated} new post(s)"
  git push
  Live on Vercel in ~30 seconds.
""")


if __name__ == "__main__":
    main()