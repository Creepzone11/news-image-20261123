// Round 2 entrypoint (Node 22, standard library only).
// The image is the entry.png beside this file; the program writes it to
// /output/entry.png (or $MAKEFUN_OUTPUT_DIR when set, for local runs).
// Deterministic: a plain byte copy, no timestamps, no re-encoding, so the
// output is byte-identical to the source on every run.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(
  new URL("./entry.png", import.meta.url),
  join(outDir, "entry.png"),
);
