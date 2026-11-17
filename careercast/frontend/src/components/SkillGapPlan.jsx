import React, { useEffect, useState } from "react";
import { ArrowUpRight, Download, Check } from "lucide-react";
import api from "../api";

export default function SkillGapPlan({ career, profileKey }) {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [ratings, setRatings] = useState({});
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    let active = true;
    setReport(null); setError(""); setRatings({}); setSaved(false);
    api.get("/api/intelligence/gap-report", { params: { career } })
      .then(({ data }) => { if (active) setReport(data); })
      .catch(() => { if (active) setError("Could not load your practice plan. Please refresh the page."); });
    return () => { active = false; };
  }, [career, profileKey]);
  async function download() {
    try {
      const { data } = await api.get("/api/intelligence/gap-report", { params: { career, format: "csv" }, responseType: "blob" });
      const url = URL.createObjectURL(data);
      const link = document.createElement("a"); link.href = url; link.download = "careercast-skill-gap.csv"; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch { setError("Could not export your practice plan. Try again."); }
  }
  async function saveFeedback() {
    setSaving(true); setSaved(false); setError("");
    try {
      await api.post("/api/intelligence/gap-feedback", { career, profile_hash: report.profile_hash, ratings });
      setSaved(true);
    } catch { setError("Could not save feedback. Refresh the plan if your profile changed."); }
    finally { setSaving(false); }
  }
  return <section className="panel competency-plan">
    <div className="learning-library-heading"><div><span className="eyebrow">TURN GAPS INTO ACTION</span><h2>Your competency improvement plan</h2><p className="muted">Practice, build evidence, and get feedback for {career}.</p></div>
      <button className="secondary" type="button" onClick={download} disabled={!report}><Download size={16} /> Export CSV</button></div>
    {error && <p role="alert">{error}</p>}
    {!report && !error && <p role="status">Preparing your plan…</p>}
    {report && <>
      <div className="learning-library-cards">{report.actions.map((action) => <article className="learning-library-card" key={action.skill}>
        <span className="lavender-pill">Step {action.sequence}</span><h3>{action.skill}</h3><p>{action.practice}</p><p className="muted"><strong>Show your progress: </strong>{action.evidence}</p>
        <a href={action.resource_url} target="_blank" rel="noopener noreferrer">Find learning resources <ArrowUpRight size={16} /></a>
        <label className="gap-rating">Is this relevant to your goal?<select aria-label={`Relevance of ${action.skill}`} value={action.skill in ratings ? String(ratings[action.skill]) : ""} onChange={(e) => {
          const next = { ...ratings }; if (e.target.value === "") delete next[action.skill]; else next[action.skill] = e.target.value === "true"; setRatings(next); setSaved(false);
        }}><option value="">Choose (optional)</option><option value="true">Relevant</option><option value="false">Not relevant</option></select></label>
      </article>)}</div>
      {!report.actions.length && <p><Check size={16} /> All checklist skills are listed in your profile. Build portfolio evidence to demonstrate your proficiency.</p>}
      {!!report.actions.length && <div className="roadmap-actions"><button className="primary" type="button" disabled={!Object.keys(ratings).length || saving} onClick={saveFeedback}>{saving ? "Saving…" : "Share relevance feedback"}</button><span role="status">{saved ? "Thank you. Your feedback is saved." : "Optional: help improve future practice plans."}</span></div>}
      <p className="data-note">{report.method} Feedback is used to evaluate relevance; no pilot relevance score is claimed yet.</p>
    </>}
  </section>;
}
