// Ratios describe checklist coverage, not independently assessed proficiency.
export function percent(numerator, denominator) {
  return denominator > 0 ? Math.round(100 * numerator / denominator) : null;
}

export function roadmapScores(career, progress = {}) {
  if (!career) return { coverage: null, learning: null, practiced: 0, required: 0, matched: 0, missing: 0 };
  const known = new Set(career.matched_skills || []);
  const missing = [...new Set(career.missing_skills || [])].filter(skill => !known.has(skill));
  const practiced = missing.filter(skill => progress[`${career.career}:${skill}`] === true).length;
  const required = known.size + missing.length;
  return { coverage: percent(known.size + practiced, required), learning: percent(practiced, missing.length), practiced, required, matched: known.size, missing: missing.length };
}
