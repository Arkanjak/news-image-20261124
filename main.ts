// news-image-20261124 — "24 November 2026: Huang Is Back"
// Entry point (Node 22, standard library only, no network, deterministic).
// The image ships beside this file as entry.png; this program validates it
// against the competition gate and copies it byte-for-byte to the output
// directory the grader provides (MAKEFUN_OUTPUT_DIR, else /output).
//
// Validation, in order: the file exists and opens with the PNG signature;
// it is at most 1 MiB; its chunk stream is well formed — IHDR first with a
// matching CRC-32, at least one IDAT chunk, IEND last with a matching
// CRC-32 and nothing after it; dimensions are non-zero and at most
// 1024 px on an edge; bit depth 8 and colour type RGB (2) or RGBA (6).
// Any failure exits non-zero with a message on stderr.
//
// Path rule (the 21 Nov intake rejection): entry.png is resolved against
// import.meta.dirname, never against the working directory — the grader
// runs this file from another cwd, where a bare "entry.png" throws ENOENT.
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { createHash } from "node:crypto";

const MAX_BYTES = 1048576; // 1 MiB gate limit
const MAX_EDGE = 1024; // 1024x1024 gate limit
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

// CRC-32 (IEEE 802.3, polynomial 0xEDB88320), table-driven.
function buildCrcTable() {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
}

const CRC_TABLE = buildCrcTable();

function crc32(buf) {
  let c = 0xffffffff;
  for (const b of buf) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function fail(msg) {
  console.error(`error: ${msg}`);
  process.exit(1);
}

// The CRC of a chunk covers its 4-byte type plus its data, not its length.
function chunkCrc(data, at, len) {
  return crc32(data.subarray(at + 4, at + 8 + len));
}

// Validate the PNG chunk stream; returns [width, height] on success.
function validatePng(data) {
  if (data.length < 8 || !data.subarray(0, 8).equals(PNG_SIG)) {
    fail("entry.png does not start with the PNG signature");
  }
  if (data.length > MAX_BYTES) {
    fail(`entry.png is ${data.length} bytes, over the ${MAX_BYTES} byte limit`);
  }
  let width = 0;
  let height = 0;
  let sawData = false;
  let pos = 8;
  let first = true;
  while (pos + 8 <= data.length) {
    const len = data.readUInt32BE(pos);
    const type = data.toString("latin1", pos + 4, pos + 8);
    const end = pos + 8 + len + 4;
    if (end > data.length) fail(`chunk ${type} at ${pos} is truncated`);
    if (first && type !== "IHDR") {
      fail(`first chunk is ${type}, expected IHDR`);
    }
    first = false;
    if (type === "IHDR") {
      if (len !== 13) fail(`IHDR length ${len}, expected 13`);
      if (data.readUInt32BE(pos + 8 + len) !== chunkCrc(data, pos, len)) {
        fail("IHDR CRC-32 mismatch");
      }
      width = data.readUInt32BE(pos + 8);
      height = data.readUInt32BE(pos + 12);
      if (width === 0 || height === 0) {
        fail("image dimensions must be non-zero");
      }
      if (width > MAX_EDGE || height > MAX_EDGE) {
        fail(`dimensions ${width}x${height} exceed the ${MAX_EDGE}x${MAX_EDGE} limit`);
      }
      if (data[pos + 16] !== 8) fail(`bit depth ${data[pos + 16]}, expected 8`);
      const colour = data[pos + 17];
      if (colour !== 2 && colour !== 6) {
        fail(`colour type ${colour}, expected 2 (RGB) or 6 (RGBA)`);
      }
    }
    if (type === "IDAT") {
      if (len === 0) fail("empty IDAT chunk");
      sawData = true;
    }
    if (type === "IEND") {
      if (len !== 0) fail("IEND chunk must be empty");
      if (data.readUInt32BE(pos + 8 + len) !== chunkCrc(data, pos, len)) {
        fail("IEND CRC-32 mismatch");
      }
      if (end !== data.length) fail("trailing bytes after the IEND chunk");
      if (!sawData) fail("no IDAT chunk: entry.png carries no image data");
      return [width, height];
    }
    pos = end;
  }
  fail("no complete IEND chunk found");
}

function main() {
  const src = join(import.meta.dirname, "entry.png");
  let data;
  try {
    data = readFileSync(src);
  } catch {
    fail(`cannot read ${src}`);
  }
  const [width, height] = validatePng(data);
  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  mkdirSync(outDir, { recursive: true });
  const dest = join(outDir, "entry.png");
  copyFileSync(src, dest);
  if (statSync(dest).size !== data.length) {
    fail("copy size mismatch after writing the output");
  }
  const sha = createHash("sha256").update(data).digest("hex");
  console.log(`ok: entry.png ${width}x${height}, ${data.length} bytes, sha256 ${sha} -> ${dest}`);
}

main();
