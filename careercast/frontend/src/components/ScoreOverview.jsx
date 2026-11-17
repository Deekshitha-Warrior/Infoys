import React from "react";
import { Link } from "react-router-dom";
import { Calculator, ArrowUpRight } from "lucide-react";
import { percent, roadmapScores } from "../lib/scoreMath";

function ScoreCard({ title, value, unit = "%", formula, detail }) {
  const available = value !== null && value !== undefined && Number.isFinite(value);
  return <article className="score-math-card"><h3>{title}</h3><strong>{available ? value : "—"}{available && <small>{unit}</small>}</strong><p>{detail}</p><code>{formula}</code></article>;
}

export default function ScoreOverview({ profile, report, analysis, models, progress }) {
  const top = report?.recommendations?.[0];
  const roadmap = roadmapScores(top, progress);
  const fields = ["degree", "institution", "graduation_year", "work_experience"];
  const filled = profile ? fields.filter(field => !!profile[field]).length + (profile.technical_skills?.length ? 1 : 0) : 0;
  const checks = analysis?.checks || [];
  const passed = checks.filter(check => check.passed).length;
  const metrics = models?.ensemble;
  const score = (value) => value === null || value === undefined ? null : value;
  const label = name => name.replaceAll("_", " ");
  return <section className="standard-card dashboard-scoreboard" aria-labelledby="dashboard-scores-title">
    <div className="standard-card-heading"><h2 id="dashboard-scores-title"><Calculator size={20} /> Your match scores, explained</h2><Link to="/models">Model evaluation <ArrowUpRight size={14} /></Link></div>
    <p className="muted">{top ? `Current target: ${top.career}. Every value below uses your saved profile and current analysis.` : "Save your profile and run an analysis to see career scores. Unavailable scores are shown as a dash."}</p>
    <div className="score-math-grid">
      <ScoreCard title="Career match index" value={score(top?.ranking_score)} unit="/100" detail="Composite index used to rank careers; not the chance of getting hired." formula={top ? `0.80 × ${top.confidence}% model score + 0.20 × (${roadmap.matched}/${roadmap.required} × 100) skill match` : "0.80 × model probability (%) + 0.20 × skill alignment (%)"} />
      <ScoreCard title="Model confidence" value={score(top?.confidence)} detail="Mean of the three classifiers’ uncalibrated career probabilities." formula="100 × (P(Logistic Regression) + P(Random Forest) + P(XGBoost)) / 3" />
      <ScoreCard title="Skill match" value={score(top?.alignment)} detail="How many of this career’s core skills are listed in your profile." formula={top ? `${roadmap.matched} matched / ${roadmap.required} required × 100` : "matched core skills / required core skills × 100"} />
      <ScoreCard title="Skill gap" value={top ? percent(roadmap.missing, roadmap.required) : null} detail="Core skills still missing from your profile. A smaller gap is better." formula={top ? `${roadmap.missing} missing / ${roadmap.required} required × 100` : "missing core skills / required core skills × 100"} />
      <ScoreCard title="Learning tasks complete" value={roadmap.learning} detail={top && !roadmap.missing ? "No missing-skill tasks for this target." : "Tasks you marked complete for missing skills; existing skills are not counted as newly learned."} formula={top ? `${roadmap.practiced} marked complete / ${roadmap.missing} missing-skill tasks × 100` : "completed missing-skill tasks / missing-skill tasks × 100"} />
      <ScoreCard title="Roadmap coverage" value={roadmap.coverage} detail="Existing core skills plus self-reported completed learning tasks." formula={top ? `(${roadmap.matched} existing + ${roadmap.practiced} practiced) / ${roadmap.required} required × 100` : "(existing skills + completed tasks) / required skills × 100"} />
      <ScoreCard title="Profile completeness" value={profile ? percent(filled, 5) : null} detail="Degree, institution, graduation year, work-experience field, and technical-skill list." formula={profile ? `${filled} filled sections / 5 sections × 100` : "filled profile sections / 5 × 100"} />
      <ScoreCard title="Résumé completeness" value={analysis ? analysis.score : null} detail={analysis ? "Eight structural checks; not an ATS or grammar score." : "Upload and analyze a résumé to calculate this score."} formula={analysis ? `${passed} passed checks / ${checks.length} checks × 100` : "passed structural checks / 8 × 100"} />
      <ScoreCard title="Recognized skill coverage" value={score(report?.coverage)} detail="Profile skills with at least one token recognized by the trained text vocabulary; not a proficiency score." formula={report ? `${report.skill_count - (report.unrecognized_skills?.length || 0)} recognized / ${report.skill_count} profile skills × 100` : "recognized profile skills / supplied profile skills × 100"} />
    </div>
    {top?.model_scores && <div className="score-model-breakdown"><h3>Model scores for {top.career}</h3><div>{Object.entries(top.model_scores).map(([name, value]) => <span key={name}><small>{label(name)}</small><strong>{value}%</strong></span>)}</div></div>}
    {metrics && <div className="score-model-breakdown"><h3>Model validation results · {models.test_rows} held-out profiles</h3><p className="muted">These measure the model on the survey test set, not your personal career match.</p><div>{[["Accuracy", metrics.accuracy], ["Macro precision", metrics.precision_macro], ["Macro recall", metrics.recall_macro], ["Macro F1", metrics.f1_macro], ["Top-5 recall", metrics.top5_recall]].map(([title, value]) => <span key={title}><small>{title}</small><strong>{(value * 100).toFixed(2)}%</strong></span>)}</div><details><summary>How evaluation scores are calculated</summary><code>Accuracy = correct Top-1 predictions / test profiles × 100</code><code>Precision per class = true positives / (true positives + false positives)</code><code>Recall per class = true positives / (true positives + false negatives)</code><code>F1 per class = 2 × precision × recall / (precision + recall)</code><code>Macro metrics = average across career classes; undefined class metrics use zero</code><code>Top-5 recall = profiles whose true career is in the five highest scores / test profiles × 100</code></details></div>}
    <p className="data-note">Milestone 3 model gate: macro F1 must reach 78%. Current validation: {metrics ? `${(metrics.f1_macro * 100).toFixed(2)}% — ${metrics.f1_macro >= 0.78 ? "threshold met" : "below target"}` : "not evaluated"}. Real pilot skill-gap relevance has not been measured.</p>
    <p className="data-note">Scores are rounded for display. Core-skill checklists are curated, and learning progress is self-reported on this device. Confidence intervals, live market demand, experience-recency weighting, and assessed proficiency are not available in the current model; no scores are invented for them.</p>
  </section>;
}
