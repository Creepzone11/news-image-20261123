// ONE DAY ON EARTH — Monday 23 November 2026.
//
// Node 22, standard library only. The front page ships pre-drawn as
// entry.png (1024x1024, produced by draw.py in this same directory).
// This program makes sure the file is a complete, valid PNG inside the
// competition's size gate, copies it into the output directory, and
// leaves a small deterministic dossier.json next to it describing the
// entry.
//
// Run it as: MAKEFUN_OUTPUT_DIR=out node main.ts

import { createHash as hashOf } from "node:crypto";
import {
  copyFileSync as copy,
  mkdirSync as mkdir,
  readFileSync as read,
  statSync as stat,
  writeFileSync as write,
} from "node:fs";
import { dirname as dirOf, join as joinPath } from "node:path";
import { fileURLToPath as urlToPath } from "node:url";

const here = dirOf(urlToPath(import.meta.url));
const pngPath = joinPath(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR === undefined
  ? "/output"
  : process.env.MAKEFUN_OUTPUT_DIR;

function die(message) {
  throw new Error(message);
}

// --- CRC-32, PNG flavour (polynomial 0xedb88320) ---
function makeCrcTable() {
  const crcTable = new Uint32Array(256);
  for (let start = 0; start < crcTable.length; start++) {
    let value = start;
    for (let bit = 0; bit < 8; bit++) {
      value = (value & 1) !== 0 ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
    }
    crcTable[start] = value >>> 0;
  }
  return crcTable;
}
const CRC = makeCrcTable();

function crcOf(bytes) {
  let running = 0xffffffff;
  for (const byte of bytes) {
    running = CRC[(running ^ byte) & 0xff] ^ (running >>> 8);
  }
  return (running ^ 0xffffffff) >>> 0;
}

// --- the file has to be a genuine PNG with the right dimensions ---
const png = read(pngPath);
const magic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!png.subarray(0, 8).equals(magic)) die("entry.png is not a PNG");

const pngWidth = png.readUInt32BE(16);
const pngHeight = png.readUInt32BE(20);
if (pngWidth !== 1024 || pngHeight !== 1024) {
  die(`entry.png must be 1024x1024, got ${pngWidth}x${pngHeight}`);
}

const pngBytes = stat(pngPath).size;
if (pngBytes > 1_048_576) {
  die(`entry.png exceeds 1,048,576 bytes (got ${pngBytes})`);
}

// --- walk the chunks, checking every CRC and finding IEND ---
let cursor = 8;
let foundIend = false;
while (cursor + 8 <= png.length && !foundIend) {
  const chunkLen = png.readUInt32BE(cursor);
  const chunkType = png.toString("ascii", cursor + 4, cursor + 8);
  if (cursor + 12 + chunkLen > png.length) {
    die(`PNG chunk ${chunkType} is truncated`);
  }
  const storedCrc = png.readUInt32BE(cursor + 8 + chunkLen);
  const realCrc = crcOf(png.subarray(cursor + 4, cursor + 8 + chunkLen));
  if (storedCrc !== realCrc) die(`PNG chunk ${chunkType} has a bad CRC`);
  cursor += 12 + chunkLen;
  if (chunkType === "IEND") foundIend = true;
}
if (!foundIend) die("entry.png has no IEND chunk");

// --- copy the image out and write the dossier (identical every run) ---
mkdir(outDir, { recursive: true });
const outPng = joinPath(outDir, "entry.png");
copy(pngPath, outPng);

const dossier = {};
dossier.title = "ONE DAY ON EARTH - Monday 23 November 2026";
dossier.competition = "news-image-20261123";
dossier.image = "entry.png";
dossier.width = pngWidth;
dossier.height = pngHeight;
dossier.bytes = pngBytes;
dossier.sha256 = hashOf("sha256").update(png).digest("hex");
dossier.stories = 35;
dossier.regions = 7;
dossier.pictured = 13;
write(joinPath(outDir, "dossier.json"), JSON.stringify(dossier, null, 2) + "\n");

console.log(`wrote ${outPng} (${pngBytes} bytes, sha256 ${dossier.sha256.slice(0, 16)}...)`);
