#!/usr/bin/env node
/**
 * generate-cover.js
 * Renders a branded 1200x630 cover image for a blog post.
 * Usage: node generate-cover.js "Post Title Here" "geo" "/path/to/output/cover.jpg"
 */

const puppeteer = require("puppeteer");
const path      = require("path");

const [,, title, category, outPath] = process.argv;

if (!title || !category || !outPath) {
  console.error("Usage: node generate-cover.js <title> <category> <output-path>");
  process.exit(1);
}

const COLORS = {
  geo:  { accent: "#52b788", label: "GEO"  },
  seo:  { accent: "#d4a843", label: "SEO"  },
  web3: { accent: "#a89fe8", label: "WEB3" },
  gtm:  { accent: "#e05252", label: "GTM"  },
};

const cat    = COLORS[category.toLowerCase()] || COLORS.geo;
const accent = cat.accent;
const label  = cat.label;

// Split title into lines — max ~28 chars per line at 60px
function splitTitle(text) {
  const words = text.split(" ");
  const lines = [];
  let current = "";
  for (const word of words) {
    const test = current ? current + " " + word : word;
    if (test.length > 28 && current) {
      lines.push(current);
      current = word;
    } else {
      current = test;
    }
  }
  if (current) lines.push(current);
  return lines;
}

const lines     = splitTitle(title);
const lastLine  = lines.pop();
const bodyLines = lines;

// Build line SVG elements — body lines white, last line accented
const LINE_START_Y  = 240;
const LINE_HEIGHT   = 80;

let titleSVG = "";
bodyLines.forEach((line, i) => {
  const y = LINE_START_Y + i * LINE_HEIGHT;
  titleSVG += `<text x="72" y="${y}" font-family="Inter, -apple-system, sans-serif" font-size="60" font-weight="800" fill="#ede9e0" letter-spacing="-2">${escapeXml(line)}</text>\n`;
});

const lastY = LINE_START_Y + bodyLines.length * LINE_HEIGHT;
titleSVG += `<text x="72" y="${lastY}" font-family="Inter, -apple-system, sans-serif" font-size="60" font-weight="800" fill="${accent}" letter-spacing="-2">${escapeXml(lastLine)}</text>\n`;

const separatorY = lastY + 52;
const metaY      = separatorY + 94;
const subY       = metaY + 26;

function escapeXml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

const pillWidth = label.length * 9 + 36;

const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 1200px; height: 630px; overflow: hidden; background: #0a0a0a; }
</style>
</head>
<body>
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">

  <rect width="1200" height="630" fill="#0a0a0a"/>

  <!-- Grid lines horizontal -->
  <line x1="0" y1="105" x2="1200" y2="105" stroke="#ffffff" stroke-opacity="0.04"/>
  <line x1="0" y1="210" x2="1200" y2="210" stroke="#ffffff" stroke-opacity="0.04"/>
  <line x1="0" y1="315" x2="1200" y2="315" stroke="#ffffff" stroke-opacity="0.04"/>
  <line x1="0" y1="420" x2="1200" y2="420" stroke="#ffffff" stroke-opacity="0.04"/>
  <line x1="0" y1="525" x2="1200" y2="525" stroke="#ffffff" stroke-opacity="0.04"/>

  <!-- Grid lines vertical -->
  <line x1="200" y1="0" x2="200" y2="630" stroke="#ffffff" stroke-opacity="0.04"/>
  <line x1="400" y1="0" x2="400" y2="630" stroke="#ffffff" stroke-opacity="0.04"/>
  <line x1="600" y1="0" x2="600" y2="630" stroke="#ffffff" stroke-opacity="0.04"/>
  <line x1="800" y1="0" x2="800" y2="630" stroke="#ffffff" stroke-opacity="0.04"/>
  <line x1="1000" y1="0" x2="1000" y2="630" stroke="#ffffff" stroke-opacity="0.04"/>

  <!-- Concentric rings -->
  <circle cx="980" cy="315" r="280" fill="none" stroke="${accent}" stroke-width="1" stroke-opacity="0.12"/>
  <circle cx="980" cy="315" r="210" fill="none" stroke="${accent}" stroke-width="1" stroke-opacity="0.1"/>
  <circle cx="980" cy="315" r="140" fill="none" stroke="${accent}" stroke-width="80" stroke-opacity="0.04"/>
  <circle cx="980" cy="315" r="56"  fill="${accent}" fill-opacity="0.07"/>
  <circle cx="980" cy="315" r="20"  fill="${accent}" fill-opacity="0.25"/>

  <!-- Category pill -->
  <rect x="72" y="68" rx="20" ry="20" width="${pillWidth}" height="28"
    fill="${accent}" fill-opacity="0.12"
    stroke="${accent}" stroke-opacity="0.3" stroke-width="1"/>
  <text x="${72 + pillWidth / 2}" y="87"
    font-family="Inter, -apple-system, sans-serif"
    font-size="11" font-weight="600" fill="${accent}"
    text-anchor="middle" letter-spacing="1.5">${label}</text>

  <!-- Title lines -->
  ${titleSVG}

  <!-- Separator -->
  <line x1="72" y1="${separatorY}" x2="240" y2="${separatorY}"
    stroke="${accent}" stroke-width="1.5" stroke-opacity="0.4"/>

  <!-- Bottom left meta -->
  <text x="72" y="${metaY}"
    font-family="Inter, -apple-system, sans-serif"
    font-size="16" fill="#7a7670">narender.xyz</text>
  <text x="72" y="${subY}"
    font-family="Inter, -apple-system, sans-serif"
    font-size="13" fill="#444240">SEO and GEO Specialist</text>

  <!-- Bottom right tag -->
  <text x="1128" y="610"
    font-family="Inter, -apple-system, sans-serif"
    font-size="12" font-weight="600" fill="${accent}"
    text-anchor="end" letter-spacing="1">narender.xyz</text>

</svg>
</body>
</html>`;

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 630, deviceScaleFactor: 2 });
  await page.setContent(html, { waitUntil: "networkidle0" });

  const absPath = path.resolve(outPath);
  await page.screenshot({
    path: absPath,
    type: "jpeg",
    quality: 92,
    clip: { x: 0, y: 0, width: 1200, height: 630 },
  });

  await browser.close();
  console.log(`cover: ${absPath}`);
})();
