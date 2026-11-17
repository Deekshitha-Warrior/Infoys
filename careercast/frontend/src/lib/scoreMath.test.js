import test from "node:test";
import assert from "node:assert/strict";
import { roadmapScores, percent } from "./scoreMath.js";

test("existing skills do not inflate completed learning tasks", () => {
  const career = { career: "Developer", matched_skills: ["python", "sql"], missing_skills: ["git", "react"] };
  const result = roadmapScores(career, { "Developer:git": true, "Developer:python": true });
  assert.equal(result.coverage, 75);
  assert.equal(result.learning, 50);
  assert.equal(result.practiced, 1);
});
test("no analysis or no missing tasks is unavailable rather than a fabricated zero", () => {
  assert.equal(roadmapScores(null).coverage, null);
  assert.equal(percent(0, 0), null);
  const result = roadmapScores({ career: "Developer", matched_skills: ["python"], missing_skills: [] });
  assert.equal(result.coverage, 100);
  assert.equal(result.learning, null);
});
test("progress for another career and duplicate skill entries do not inflate coverage", () => {
  const result = roadmapScores({ career: "Developer", matched_skills: ["sql", "sql"], missing_skills: ["sql", "git", "git"] }, { "Analyst:git": true });
  assert.equal(result.coverage, 50);
  assert.equal(result.learning, 0);
  assert.equal(result.required, 2);
});
