#!/usr/bin/env node
/**
 * Generates og-home.jpg — the social share image for narender.xyz homepage
 * 1200x630, branded, no post title
 */
const puppeteer = require("puppeteer");
const path = require("path");

const html = `<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>*{margin:0;padding:0;box-sizing:border-box}html,body{width:1200px;height:630px;overflow:hidden;background:#0a0a0a}</style>
</head><body>
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="630" fill="#0a0a0a"/>
  <line x1="0" y1="105" x2="1200" y2="105" stroke="#fff" stroke-opacity="0.04"/>
  <line x1="0" y1="210" x2="1200" y2="210" stroke="#fff" stroke-opacity="0.04"/>
  <line x1="0" y1="315" x2="1200" y2="315" stroke="#fff" stroke-opacity="0.04"/>
  <line x1="0" y1="420" x2="1200" y2="420" stroke="#fff" stroke-opacity="0.04"/>
  <line x1="0" y1="525" x2="1200" y2="525" stroke="#fff" stroke-opacity="0.04"/>
  <line x1="200" y1="0" x2="200" y2="630" stroke="#fff" stroke-opacity="0.04"/>
  <line x1="400" y1="0" x2="400" y2="630" stroke="#fff" stroke-opacity="0.04"/>
  <line x1="600" y1="0" x2="600" y2="630" stroke="#fff" stroke-opacity="0.04"/>
  <line x1="800" y1="0" x2="800" y2="630" stroke="#fff" stroke-opacity="0.04"/>
  <line x1="1000" y1="0" x2="1000" y2="630" stroke="#fff" stroke-opacity="0.04"/>

  <circle cx="980" cy="315" r="290" fill="none" stroke="#d4a843" stroke-width="1" stroke-opacity="0.12"/>
  <circle cx="980" cy="315" r="220" fill="none" stroke="#d4a843" stroke-width="1" stroke-opacity="0.1"/>
  <circle cx="980" cy="315" r="150" fill="none" stroke="#d4a843" stroke-width="80" stroke-opacity="0.04"/>
  <circle cx="980" cy="315" r="60"  fill="#d4a843" fill-opacity="0.07"/>
  <circle cx="980" cy="315" r="22"  fill="#d4a843" fill-opacity="0.25"/>

  <circle cx="100" cy="315" r="200" fill="none" stroke="#d4a843" stroke-width="1" stroke-opacity="0.06"/>
  <circle cx="100" cy="315" r="140" fill="none" stroke="#d4a843" stroke-width="1" stroke-opacity="0.05"/>

  <text x="72" y="220" font-family="Inter,-apple-system,sans-serif" font-size="80" font-weight="800" fill="#ede9e0" letter-spacing="-3">narender</text>
  <text x="72" y="310" font-family="Inter,-apple-system,sans-serif" font-size="80" font-weight="800" fill="#d4a843" letter-spacing="-3">.xyz</text>

  <line x1="72" y1="352" x2="280" y2="352" stroke="#d4a843" stroke-width="1.5" stroke-opacity="0.4"/>

  <text x="72" y="412" font-family="Inter,-apple-system,sans-serif" font-size="24" font-weight="400" fill="#7a7670">SEO and GEO Specialist</text>
  <text x="72" y="448" font-family="Inter,-apple-system,sans-serif" font-size="20" font-weight="400" fill="#444240">Web3 content strategist · Remote since 2017</text>

  <text x="72" y="560" font-family="Inter,-apple-system,sans-serif" font-size="14" fill="#444240">100k+ followers built from zero  ·  #1 ranking in weeks  ·  Cited in ChatGPT and Perplexity</text>
</svg>
</body></html>`;

(async () => {
  const browser = await puppeteer.launch({ headless: "new", args: ["--no-sandbox", "--disable-setuid-sandbox"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 630, deviceScaleFactor: 2 });
  await page.setContent(html, { waitUntil: "domcontentloaded" });
  const out = path.resolve(__dirname, "og-home.jpg");
  await page.screenshot({ path: out, type: "jpeg", quality: 92, clip: { x: 0, y: 0, width: 1200, height: 630 } });
  await browser.close();
  console.log(`og-home.jpg: ${out}`);
})();
