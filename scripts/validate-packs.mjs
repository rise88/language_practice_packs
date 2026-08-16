#!/usr/bin/env node
/**
 * Validate Vocalis packs for multi-L2:
 * - every pack JSON + catalog entry has `lang`
 * - every seed item has headword `l2` or legacy `fr`
 * - non-French packs should use `l2` (warn if only `fr`)
 * - catalog versions / ids match pack files
 *
 * Usage: node scripts/validate-packs.mjs
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];
const warnings = [];

function loadJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

const catalog = loadJson(path.join(root, "catalog.json"));
if (!Array.isArray(catalog.languages) || !catalog.languages.length) {
  errors.push(`catalog.json: missing top-level languages array (e.g. ["fr","es","ru"])`);
}
if (!Array.isArray(catalog.locales) || !catalog.locales.length) {
  warnings.push(`catalog.json: missing top-level locales array (gloss UI languages)`);
}
const catalogById = new Map();
for (const entry of catalog.packs || []) {
  if (!entry.id) errors.push(`catalog entry missing id`);
  else if (catalogById.has(entry.id)) errors.push(`duplicate catalog id: ${entry.id}`);
  else catalogById.set(entry.id, entry);
  if (!entry.lang || typeof entry.lang !== "string") {
    errors.push(`catalog ${entry.id || "?"}: missing lang`);
  }
}

const packFiles = fs
  .readdirSync(root)
  .filter((f) => f.endsWith(".json") && f !== "catalog.json" && f !== "_template.json");

const packIds = new Set();

for (const file of packFiles) {
  const full = path.join(root, file);
  let pack;
  try {
    pack = loadJson(full);
  } catch (e) {
    errors.push(`${file}: invalid JSON (${e.message})`);
    continue;
  }

  if (!pack.id) errors.push(`${file}: missing id`);
  else {
    if (packIds.has(pack.id)) errors.push(`${file}: duplicate pack id ${pack.id}`);
    packIds.add(pack.id);
  }

  if (!pack.lang || typeof pack.lang !== "string") {
    errors.push(`${file}: missing lang`);
  }

  const seed = pack.seed || [];
  seed.forEach((card, i) => {
    const hasL2 = typeof card.l2 === "string" && card.l2.length > 0;
    const hasFr = typeof card.fr === "string" && card.fr.length > 0;
    if (!hasL2 && !hasFr) {
      errors.push(`${file}: seed[${i}] (${card.id || "?"}) missing l2 or fr`);
    }
    if (pack.lang && pack.lang !== "fr" && !hasL2 && hasFr) {
      warnings.push(`${file}: seed[${i}] non-French pack should use l2 (has fr only)`);
    }
    if (pack.lang === "fr" && hasFr && !hasL2) {
      warnings.push(`${file}: seed[${i}] French pack should dual-write l2 (has fr only)`);
    }
  });

  const entry = catalogById.get(pack.id);
  if (!entry) {
    errors.push(`${file}: id ${pack.id} not listed in catalog.json`);
  } else {
    if (entry.lang !== pack.lang) {
      errors.push(`${file}: catalog lang "${entry.lang}" !== pack lang "${pack.lang}"`);
    }
    if (entry.version !== pack.version) {
      errors.push(`${file}: catalog version ${entry.version} !== pack version ${pack.version}`);
    }
    const expectedUrl = `./${file}`;
    if (entry.url && entry.url !== expectedUrl) {
      warnings.push(`${file}: catalog url ${entry.url} (expected ${expectedUrl})`);
    }
  }
}

for (const id of catalogById.keys()) {
  if (!packIds.has(id)) errors.push(`catalog lists ${id} but no pack JSON found`);
}

if (warnings.length) {
  console.warn("Warnings:");
  for (const w of warnings) console.warn(" -", w);
}

if (errors.length) {
  console.error("Validation failed:");
  for (const e of errors) console.error(" -", e);
  process.exit(1);
}

console.log(
  `OK: ${packFiles.length} packs, ${catalog.packs.length} catalog entries; languages=${(catalog.languages || []).join(",")}; all have lang; all seed items have l2 or fr.`
);
