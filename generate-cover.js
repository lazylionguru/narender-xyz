#!/usr/bin/env node
/**
 * generate-cover.js
 * Renders two branded images per post:
 *   cover.jpg — 1200x630 full cover with title text (used on post pages)
 *   thumb.jpg — 600x600 square, unique shape per category, no text (blog index)
 *
 * Shapes:
 *   geo  — concentric circles (radar/signal)
 *   seo  — nested diamonds (ranked/structured)
 *   web3 — hexagon cluster (decentralised network)
 *   gtm  — funnel trapezoids (go-to-market)
 *
 * Usage: node generate-cover.js "Post Title" "geo" "/path/to/post/folder"
 */

const puppeteer = require("puppeteer");
const path      = require("path");

const [,, title, category, outDir] = process.argv;

if (!title || !category || !outDir) {
  console.error("Usage: node generate-cover.js <title> <category> <output-dir>");
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
const pillW  = label.length * 9 + 36;

function escapeXml(str) {
  return str
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

function splitTitle(text) {
  const words = text.split(" ");
  const lines = [];
  let current = "";
  for (const word of words) {
    const test = current ? current + " " + word : word;
    if (test.length > 28 && current) { lines.push(current); current = word; }
    else { current = test; }
  }
  if (current) lines.push(current);
  return lines;
}

// ── Thumb shapes ──────────────────────────────────────────────────────────────

function thumbShapeGeo(a) {
  return `
  <circle cx="300" cy="300" r="260" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.15"/>
  <circle cx="300" cy="300" r="205" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.12"/>
  <circle cx="300" cy="300" r="150" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.09"/>
  <circle cx="300" cy="300" r="105" fill="none" stroke="${a}" stroke-width="50" stroke-opacity="0.05"/>
  <circle cx="300" cy="300" r="56"  fill="${a}" fill-opacity="0.09"/>
  <circle cx="300" cy="300" r="24"  fill="${a}" fill-opacity="0.35"/>`;
}

function thumbShapeSeo(a) {
  return `
  <rect x="300" y="40"  width="186" height="186" rx="4" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.15" transform="rotate(45 300 300)"/>
  <rect x="300" y="80"  width="140" height="140" rx="3" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.12" transform="rotate(45 300 300)"/>
  <rect x="300" y="116" width="98"  height="98"  rx="3" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.09" transform="rotate(45 300 300)"/>
  <rect x="300" y="148" width="60"  height="60"  rx="2" fill="${a}" fill-opacity="0.07" stroke="${a}" stroke-width="1" stroke-opacity="0.2" transform="rotate(45 300 300)"/>
  <rect x="300" y="173" width="26"  height="26"  rx="2" fill="${a}" fill-opacity="0.4"  transform="rotate(45 300 300)"/>`;
}

function thumbShapeWeb3(a) {
  // Hex grid — centre hex + 6 surrounding
  const hex = (cx, cy, r, opacity, fill) => {
    const pts = [];
    for (let i = 0; i < 6; i++) {
      const angle = Math.PI / 180 * (60 * i - 30);
      pts.push(`${(cx + r * Math.cos(angle)).toFixed(1)},${(cy + r * Math.sin(angle)).toFixed(1)}`);
    }
    const poly = `points="${pts.join(' ')}"`;
    return fill
      ? `<polygon ${poly} fill="${a}" fill-opacity="${opacity}"/>`
      : `<polygon ${poly} fill="none" stroke="${a}" stroke-width="1" stroke-opacity="${opacity}"/>`;
  };
  const R = 80; const gap = R * 1.78;
  const offsets = [[0,0],[gap,0],[-gap,0],[gap/2, gap*0.866],[-gap/2,gap*0.866],[gap/2,-gap*0.866],[-gap/2,-gap*0.866]];
  let out = "";
  offsets.forEach(([dx,dy], i) => {
    const cx = 300 + dx; const cy = 300 + dy;
    if (i === 0) {
      out += hex(cx, cy, R * 1.05, 0.15, false);
      out += hex(cx, cy, R * 0.72, 0.12, false);
      out += hex(cx, cy, R * 0.42, 0.1, true);
      out += hex(cx, cy, R * 0.18, 0.4, true);
    } else {
      out += hex(cx, cy, R * 0.88, 0.08, false);
      out += hex(cx, cy, R * 0.55, 0.06, false);
    }
  });
  return out;
}

function thumbShapeGtm(a) {
  return `
  <polygon points="80,70  520,70  460,160 140,160" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.15" transform="scale(0.5) translate(300,130)"/>
  <polygon points="100,95  500,95  445,170 155,170" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.12" transform="scale(0.5) translate(300,130)"/>

  <polygon points="90,80 510,80 455,175 145,175"   fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.15"/>
  <polygon points="120,115 480,115 435,190 165,190" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.12"/>
  <polygon points="155,148 445,148 415,205 185,205" fill="none" stroke="${a}" stroke-width="1" stroke-opacity="0.1"/>
  <polygon points="188,176 412,176 395,210 205,210" fill="${a}" fill-opacity="0.07" stroke="${a}" stroke-width="1" stroke-opacity="0.2"/>
  <polygon points="220,200 380,200 368,218 232,218" fill="${a}" fill-opacity="0.25"/>

  <line x1="300" y1="220" x2="300" y2="360" stroke="${a}" stroke-width="1.5" stroke-opacity="0.25"/>
  <line x1="300" y1="310" x2="220" y2="390" stroke="${a}" stroke-width="1"   stroke-opacity="0.15"/>
  <line x1="300" y1="310" x2="380" y2="390" stroke="${a}" stroke-width="1"   stroke-opacity="0.15"/>
  <circle cx="300" cy="362" r="12" fill="${a}" fill-opacity="0.3"/>
  <circle cx="218" cy="392" r="8"  fill="${a}" fill-opacity="0.2"/>
  <circle cx="382" cy="392" r="8"  fill="${a}" fill-opacity="0.2"/>`;
}

function thumbShape(cat, accent) {
  switch (cat) {
    case "seo":  return thumbShapeSeo(accent);
    case "web3": return thumbShapeWeb3(accent);
    case "gtm":  return thumbShapeGtm(accent);
    default:     return thumbShapeGeo(accent);
  }
}

// ── Grid lines helper ─────────────────────────────────────────────────────────

function gridLines(w, h, step, op) {
  let out = "";
  for (let x = step; x < w; x += step)
    out += `<line x1="${x}" y1="0" x2="${x}" y2="${h}" stroke="#fff" stroke-opacity="${op}"/>`;
  for (let y = step; y < h; y += step)
    out += `<line x1="0" y1="${y}" x2="${w}" y2="${y}" stroke="#fff" stroke-opacity="${op}"/>`;
  return out;
}

// ── Cover HTML (1200x630) ─────────────────────────────────────────────────────

const lines    = splitTitle(title);
const lastLine = lines.pop();
const bodyLines = lines;
const LINE_START_Y = 240;
const LINE_HEIGHT  = 80;

let titleSVG = "";
bodyLines.forEach((line, i) => {
  const y = LINE_START_Y + i * LINE_HEIGHT;
  titleSVG += `<text x="72" y="${y}" font-family="Inter,-apple-system,sans-serif" font-size="60" font-weight="800" fill="#ede9e0" letter-spacing="-2">${escapeXml(line)}</text>\n`;
});
const lastY      = LINE_START_Y + bodyLines.length * LINE_HEIGHT;
const separatorY = lastY + 52;
const metaY      = separatorY + 94;
const subY       = metaY + 26;
titleSVG += `<text x="72" y="${lastY}" font-family="Inter,-apple-system,sans-serif" font-size="60" font-weight="800" fill="${accent}" letter-spacing="-2">${escapeXml(lastLine)}</text>\n`;

const coverHtml = `<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>*{margin:0;padding:0;box-sizing:border-box}html,body{width:1200px;height:630px;overflow:hidden;background:#0a0a0a}</style>
</head><body>
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="630" fill="#0a0a0a"/>
  ${gridLines(1200, 630, 105, "0.04")}
  <circle cx="980" cy="315" r="280" fill="none" stroke="${accent}" stroke-width="1" stroke-opacity="0.12"/>
  <circle cx="980" cy="315" r="210" fill="none" stroke="${accent}" stroke-width="1" stroke-opacity="0.1"/>
  <circle cx="980" cy="315" r="140" fill="none" stroke="${accent}" stroke-width="80" stroke-opacity="0.04"/>
  <circle cx="980" cy="315" r="56"  fill="${accent}" fill-opacity="0.07"/>
  <circle cx="980" cy="315" r="20"  fill="${accent}" fill-opacity="0.25"/>
  <rect x="72" y="68" rx="20" ry="20" width="${pillW}" height="28" fill="${accent}" fill-opacity="0.12" stroke="${accent}" stroke-opacity="0.3" stroke-width="1"/>
  <text x="${72 + pillW / 2}" y="87" font-family="Inter,-apple-system,sans-serif" font-size="11" font-weight="600" fill="${accent}" text-anchor="middle" letter-spacing="1.5">${label}</text>
  ${titleSVG}
  <line x1="72" y1="${separatorY}" x2="240" y2="${separatorY}" stroke="${accent}" stroke-width="1.5" stroke-opacity="0.4"/>
  <text x="72" y="${metaY}" font-family="Inter,-apple-system,sans-serif" font-size="16" fill="#7a7670">narender.xyz</text>
  <text x="72" y="${subY}" font-family="Inter,-apple-system,sans-serif" font-size="13" fill="#444240">SEO and GEO Specialist</text>
  <text x="1128" y="610" font-family="Inter,-apple-system,sans-serif" font-size="12" font-weight="600" fill="${accent}" text-anchor="end" letter-spacing="1">narender.xyz</text>
</svg></body></html>`;

// ── Thumb HTML (600x600) ──────────────────────────────────────────────────────

const thumbHtml = `<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>*{margin:0;padding:0;box-sizing:border-box}html,body{width:600px;height:600px;overflow:hidden;background:#0a0a0a}</style>
</head><body>
<svg width="600" height="600" xmlns="http://www.w3.org/2000/svg">
  <rect width="600" height="600" fill="#0a0a0a"/>
  ${gridLines(600, 600, 100, "0.04")}
  ${thumbShape(category.toLowerCase(), accent)}
  <rect x="20" y="20" rx="16" ry="16" width="${pillW}" height="26" fill="${accent}" fill-opacity="0.12" stroke="${accent}" stroke-opacity="0.3" stroke-width="1"/>
  <text x="${20 + pillW / 2}" y="38" font-family="Inter,-apple-system,sans-serif" font-size="10" font-weight="600" fill="${accent}" text-anchor="middle" letter-spacing="1.2">${label}</text>
  <text x="580" y="584" font-family="Inter,-apple-system,sans-serif" font-size="10" font-weight="600" fill="${accent}" fill-opacity="0.3" text-anchor="end" letter-spacing="1">narender.xyz</text>
</svg></body></html>`;

// ── Render both ───────────────────────────────────────────────────────────────

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const page = await browser.newPage();

  const coverPath = path.resolve(outDir, "cover.jpg");
  await page.setViewport({ width: 1200, height: 630, deviceScaleFactor: 2 });
  await page.setContent(coverHtml, { waitUntil: "domcontentloaded" });
  await page.screenshot({ path: coverPath, type: "jpeg", quality: 92, clip: { x: 0, y: 0, width: 1200, height: 630 } });
  console.log(`cover: ${coverPath}`);

  const thumbPath = path.resolve(outDir, "thumb.jpg");
  await page.setViewport({ width: 600, height: 600, deviceScaleFactor: 2 });
  await page.setContent(thumbHtml, { waitUntil: "domcontentloaded" });
  await page.screenshot({ path: thumbPath, type: "jpeg", quality: 90, clip: { x: 0, y: 0, width: 600, height: 600 } });
  console.log(`thumb: ${thumbPath}`);

  await browser.close();
})();