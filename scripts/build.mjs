// Copies the public files into dist/. An allowlist, not a denylist:
// the repo root holds .env, node_modules and source PNGs that must never ship.
import { cpSync, rmSync, mkdirSync, existsSync } from 'node:fs';

const PUBLIC = [
  'index.html',
  'style.css',
  'home-v2.css',
  'home-v3.css',
  'favicon.svg',
  'og-home.jpg',
  'robots.txt',
  'sitemap.xml',
  'llms.txt',
  'agents.md',
  'img',
  'blog',
  '_headers',
];

rmSync('dist', { recursive: true, force: true });
mkdirSync('dist');
for (const p of PUBLIC) {
  if (!existsSync(p)) throw new Error(`missing public file: ${p}`);
  cpSync(p, `dist/${p}`, { recursive: true, filter: (src) => !src.endsWith('.DS_Store') });
}
console.log(`dist/ built from ${PUBLIC.length} entries`);
