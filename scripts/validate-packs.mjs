#!/usr/bin/env node
/**
 * Validate Vocalis packs for multi-L2:
 * - every pack JSON + catalog entry has `lang`
 * - packs live under `<lang>/<id>.json` (or legacy root `./<id>.json`)
 * - every seed item has headword `l2` or legacy `fr`
 * - non-French packs should use `l2` (warn if only `fr`)
 * - catalog versions / ids / urls match pack files
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

function listPackFiles() {
  const files = [];
  const skipRoot = new Set(["catalog.json", "_template.json"]);
  for (const name of fs.readdirSync(root)) {
    const full = path.join(root, name);
    const st = fs.statSync(full);
    if (st.isFile() && name.endsWith(".json") && !skipRoot.has(name)) {
      files.push({ rel: name, full, langHint: null });
    } else if (st.isDirectory() && /^[a-z]{2}(-[a-z]{2})?$/i.test(name) && name !== "scripts") {
      for (const child of fs.readdirSync(full)) {
        if (!child.endsWith(".json")) continue;
        files.push({
          rel: path.posix.join(name, child),
          full: path.join(full, child),
          langHint: name.toLowerCase(),
        });
      }
    }
  }
  return files.sort((a, b) => a.rel.localeCompare(b.rel));
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
  if (entry.url && entry.lang && entry.id) {
    const preferred = `./${entry.lang}/${entry.id}.json`;
    const legacy = `./${entry.id}.json`;
    if (entry.url !== preferred && entry.url !== legacy) {
      warnings.push(`catalog ${entry.id}: url ${entry.url} (preferred ${preferred})`);
    }
  }
}

const packFiles = listPackFiles();
const packIds = new Set();

for (const { rel, full, langHint } of packFiles) {
  let pack;
  try {
    pack = loadJson(full);
  } catch (e) {
    errors.push(`${rel}: invalid JSON (${e.message})`);
    continue;
  }

  if (!pack.id) errors.push(`${rel}: missing id`);
  else {
    if (packIds.has(pack.id)) errors.push(`${rel}: duplicate pack id ${pack.id}`);
    packIds.add(pack.id);
  }

  if (!pack.lang || typeof pack.lang !== "string") {
    errors.push(`${rel}: missing lang`);
  } else if (langHint && pack.lang !== langHint) {
    errors.push(`${rel}: pack lang "${pack.lang}" does not match folder "${langHint}"`);
  }

  const seed = pack.seed || [];
  seed.forEach((card, i) => {
    const hasL2 = typeof card.l2 === "string" && card.l2.length > 0;
    const hasFr = typeof card.fr === "string" && card.fr.length > 0;
    if (!hasL2 && !hasFr) {
      errors.push(`${rel}: seed[${i}] (${card.id || "?"}) missing l2 or fr`);
    }
    if (pack.lang && pack.lang !== "fr" && !hasL2 && hasFr) {
      warnings.push(`${rel}: seed[${i}] non-French pack should use l2 (has fr only)`);
    }
    if (pack.lang === "fr" && hasFr && !hasL2) {
      warnings.push(`${rel}: seed[${i}] French pack should dual-write l2 (has fr only)`);
    }
  });

  const locales = Array.isArray(catalog.locales) ? catalog.locales : ["en", "es", "ru"];
  (pack.seed || []).forEach((card, i) => {
    const gloss = card.gloss || {};
    for (const loc of locales) {
      if (!(gloss[loc] || (loc === "en" && card.en))) {
        warnings.push(`${rel}: seed[${i}] missing gloss.${loc}`);
        break;
      }
    }
  });
  for (const lesson of pack.grammar || []) {
    const why = lesson.why;
    if (why && typeof why === "object" && !why.fr) {
      warnings.push(`${rel}: grammar ${lesson.id || "?"} why missing fr`);
    }
    for (const q of lesson.questions || []) {
      if (!q.gloss || typeof q.gloss !== "object") {
        warnings.push(`${rel}: grammar question ${q.id || q.prompt || "?"} missing gloss`);
        break;
      }
      if (!q.why || typeof q.why !== "object") {
        warnings.push(`${rel}: grammar question ${q.id || q.prompt || "?"} missing why`);
        break;
      }
    }
  }
  const skills = pack.skills || {};
  if (skills.fren && !skills.l2en) {
    warnings.push(`${rel}: has fren but missing l2en alias`);
  }
  if (!Array.isArray(pack.sounds) || !pack.sounds.length) {
    warnings.push(`${rel}: missing sounds (Prononcer → Sons)`);
  }

  const entry = catalogById.get(pack.id);
  if (!entry) {
    errors.push(`${rel}: id ${pack.id} not listed in catalog.json`);
  } else {
    if (entry.lang !== pack.lang) {
      errors.push(`${rel}: catalog lang "${entry.lang}" !== pack lang "${pack.lang}"`);
    }
    if (entry.version !== pack.version) {
      errors.push(`${rel}: catalog version ${entry.version} !== pack version ${pack.version}`);
    }
    const preferredUrl = `./${pack.lang}/${path.basename(rel)}`;
    const legacyUrl = `./${path.basename(rel)}`;
    if (entry.url && entry.url !== preferredUrl && entry.url !== legacyUrl) {
      warnings.push(`${rel}: catalog url ${entry.url} (expected ${preferredUrl})`);
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
  `OK: ${packFiles.length} packs, ${catalog.packs.length} catalog entries; languages=${(catalog.languages || []).join(",")}; layout=<lang>/<id>.json; all have lang; all seed items have l2 or fr.`
);
