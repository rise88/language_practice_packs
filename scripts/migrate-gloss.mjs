#!/usr/bin/env node
/**
 * Lift pratiquePack v1 → v2 gloss shape.
 * - pratiquePack := 2
 * - flat `en` → gloss.en (keep legacy `en`)
 * - listen.wordEn → wordGloss.en (keep legacy wordEn)
 * - grammar.rule string → { fr: rule }
 * - drop skills.meaning.choices when gloss exists (app derives MCQ from gloss[lang])
 *
 * Usage: node scripts/migrate-gloss.mjs
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function ensureGlossEn(obj) {
  if (!obj || typeof obj !== "object") return false;
  const en = typeof obj.en === "string" ? obj.en : null;
  if (!en) return false;
  if (!obj.gloss || typeof obj.gloss !== "object") obj.gloss = {};
  if (typeof obj.gloss.en !== "string" || !obj.gloss.en) {
    obj.gloss.en = en;
    return true;
  }
  return false;
}

function migratePack(pack) {
  let changed = false;

  if (pack.pratiquePack !== 2) {
    pack.pratiquePack = 2;
    changed = true;
  }

  for (const card of pack.seed || []) {
    if (ensureGlossEn(card)) changed = true;
  }

  for (const phrase of pack.phrases || []) {
    if (ensureGlossEn(phrase)) changed = true;
  }

  for (const item of pack.listen || []) {
    if (ensureGlossEn(item)) changed = true;
    const wordEn = typeof item.wordEn === "string" ? item.wordEn : null;
    if (wordEn) {
      if (!item.wordGloss || typeof item.wordGloss !== "object") item.wordGloss = {};
      if (typeof item.wordGloss.en !== "string" || !item.wordGloss.en) {
        item.wordGloss.en = wordEn;
        changed = true;
      }
    }
  }

  for (const lesson of pack.grammar || []) {
    if (typeof lesson.rule === "string") {
      lesson.rule = { fr: lesson.rule };
      changed = true;
    } else if (lesson.rule && typeof lesson.rule === "object" && !lesson.rule.fr && typeof lesson.en === "string") {
      // unlikely; leave as-is
    }
    if (!lesson.why || typeof lesson.why !== "object") {
      lesson.why = {};
      changed = true;
    }
  }

  const skills = pack.skills || {};
  for (const drillId of Object.keys(skills)) {
    const items = skills[drillId];
    if (!Array.isArray(items)) continue;
    for (const item of items) {
      if (ensureGlossEn(item)) changed = true;
      if (drillId === "meaning" && item.gloss && typeof item.gloss === "object" && Array.isArray(item.choices)) {
        delete item.choices;
        changed = true;
      }
    }
  }

  return changed;
}

function main() {
  const files = fs
    .readdirSync(root)
    .filter((f) => f.endsWith(".json") && f !== "catalog.json")
    .sort();

  let n = 0;
  for (const file of files) {
    const full = path.join(root, file);
    const pack = JSON.parse(fs.readFileSync(full, "utf8"));
    if (!pack.pratiquePack && pack.pratiquePack !== 0) continue;
    if (migratePack(pack)) {
      fs.writeFileSync(full, JSON.stringify(pack, null, 2) + "\n");
      n += 1;
      console.log("migrated", file);
    } else {
      console.log("unchanged", file);
    }
  }
  console.log(`done: ${n}/${files.length} files updated`);
}

main();
