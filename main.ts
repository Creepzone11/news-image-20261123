// ONE DAY ON EARTH - Monday 23 November 2026.
// Node 22, standard library only. The front page is pre-drawn (entry.png,
// 1024x1024, PIL) and this program copies it to the output directory after
// checking it is a whole, valid PNG inside the competition's gate, then
// writes a small deterministic dossier.json describing the entry.
//
//   MAKEFUN_OUTPUT_DIR=out node main.ts
import { createHash } from "node:crypto";
import { copyFileSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

// --- the bytes must be a real PNG of the right shape ---
const buf = readFileSync(src);
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!buf.subarray(0, 8).equals(PNG_SIG)) {
  throw new Error("entry.png is not a PNG");
}
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png must be 1024x1024, got ${width}x${height}`);
}
const size = statSync(src).size;
if (size > 1_048_576) {
  throw new Error(`entry.png exceeds 1,048,576 bytes (got ${size})`);
}

// --- every PNG chunk must be whole, with a matching CRC ---
const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();
function crc32(bytes) {
  let c = 0xffffffff;
  for (const b of bytes) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
let off = 8;
let sawIEND = false;
while (off + 8 <= buf.length) {
  const len = buf.readUInt32BE(off);
  const type = buf.toString("ascii", off + 4, off + 8);
  if (off + 12 + len > buf.length) throw new Error(`PNG chunk ${type} is truncated`);
  const stored = buf.readUInt32BE(off + 8 + len);
  const actual = crc32(buf.subarray(off + 4, off + 8 + len));
  if (stored !== actual) throw new Error(`PNG chunk ${type} has a bad CRC`);
  off += 12 + len;
  if (type === "IEND") {
    sawIEND = true;
    break;
  }
}
if (!sawIEND) throw new Error("entry.png has no IEND chunk");

// --- copy + deterministic dossier (same bytes on every run) ---
mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, "entry.png"));
const dossier = {
  title: "ONE DAY ON EARTH - Monday 23 November 2026",
  competition: "news-image-20261123",
  image: "entry.png",
  width,
  height,
  bytes: size,
  sha256: createHash("sha256").update(buf).digest("hex"),
  stories: 35,
  regions: 7,
  pictured: 13,
};
writeFileSync(join(outDir, "dossier.json"), JSON.stringify(dossier, null, 2) + "\n");
console.log(`wrote ${join(outDir, "entry.png")} (${size} bytes, sha256 ${dossier.sha256.slice(0, 16)}...)`);
