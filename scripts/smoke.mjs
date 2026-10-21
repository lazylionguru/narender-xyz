// Checks page CONTENT, not just status: a 200 can still be an error shell.
// Usage: node scripts/smoke.mjs [baseUrl]   (default https://narender.xyz)
const base = (process.argv[2] || 'https://narender.xyz').replace(/\/$/, '');

const checks = [
  ['/', 'I build things. I rank them.'],
  ['/blog/', 'what-is-geo-generative-engine-optimisation'],
  ['/blog/what-is-geo-generative-engine-optimisation/', 'application/ld+json'],
  ['/style.css', '{'],
  ['/home-v3.css', '{'],
  ['/sitemap.xml', '<urlset'],
  ['/robots.txt', 'Sitemap'],
  ['/llms.txt', 'Narender'],
  ['/agents.md', 'Narender Charan'],
];

async function get(url) {
  for (let i = 0; i < 3; i++) {
    try {
      const r = await fetch(url, { redirect: 'follow' });
      return { status: r.status, body: await r.text() };
    } catch (e) {
      if (i === 2) return { status: 0, body: String(e) };
      await new Promise((r) => setTimeout(r, 1000));
    }
  }
}

let failed = 0;
for (const [path, needle] of checks) {
  const { status, body } = await get(base + path);
  const ok = status === 200 && body.includes(needle);
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${status} ${path}${ok ? '' : `  (wanted "${needle}")`}`);
}

// Secrets and sources must 404, never be served.
for (const path of ['/.env', '/blog.py', '/package.json', '/node_modules/']) {
  const { status } = await get(base + path);
  const ok = status === 404;
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${status} ${path} (must be 404)`);
}

console.log(failed ? `\n${failed} check(s) failed` : '\nall checks passed');
process.exit(failed ? 1 : 0);
