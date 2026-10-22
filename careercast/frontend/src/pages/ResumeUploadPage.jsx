import React, { useEffect, useRef, useState } from "react";
import {
  CloudUpload,
  FileText,
  Check,
  ArrowRight,
  RefreshCw,
  Sparkles,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import { Ring } from "./IntelligencePage";
import api from "../api";
export default function ResumeUploadPage() {
  const input = useRef(null),
    [file, setFile] = useState(null),
    [resume, setResume] = useState(null),
    [analysis, setAnalysis] = useState(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [saving, setSaving] = useState(false),
    [drag, setDrag] = useState(false),
    [fields, setFields] = useState({});
  function populate(r) {
    setResume(r);
    setFields(
      Object.fromEntries(
        ["technical_skills", "education", "job_roles", "experience"].map(
          (k) => [k, (r.parsed_information?.[k] || []).join("\n")],
        ),
      ),
    );
  }
  useEffect(() => {
    let active = true;
    api
      .get("/api/resume/latest")
      .then((r) => active && populate(r.data))
      .catch((e) => {
        if (active && e.response?.status !== 404)
          setError("Could not load your latest résumé.");
      });
    api
      .get("/api/intelligence/resume-analysis")
      .then((r) => active && setAnalysis(r.data))
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);
  function choose(f) {
    setError("");
    setMessage("");
    if (!f) return;
    if (!/\.(pdf|docx)$/i.test(f.name)) {
      setError("Please choose a PDF or DOCX file.");
      return;
    }
    if (f.size > 5 * 1024 * 1024) {
      setError("The file must be 5 MB or smaller.");
      return;
    }
    setFile(f);
  }
  async function analyze() {
    if (!file) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const body = new FormData();
      body.append("file", file);
      const r = await api.post("/api/resume/upload", body, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      populate(r.data);
      setAnalysis((await api.get("/api/intelligence/resume-analysis")).data);
      setMessage(
        "Résumé analyzed. Review the extracted details before saving.",
      );
    } catch (e) {
      setError(
        e.response?.data?.detail ||
          "Could not analyze this file. Please try a text-based PDF or DOCX.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function save() {
    setSaving(true);
    setError("");
    try {
      await api.post(
        `/api/resume/${resume.resume_id}/apply`,
        Object.fromEntries(
          Object.entries(fields).map(([k, v]) => [
            k,
            v
              .split("\n")
              .map((s) => s.trim())
              .filter(Boolean),
          ]),
        ),
      );
      setMessage(
        "Confirmed details saved to your profile. Refresh career analysis to see your updated recommendations.",
      );
    } catch (e) {
      setError(
        e.response?.data?.detail || "Could not save the extracted details.",
      );
    } finally {
      setSaving(false);
    }
  }
  return (
    <DashboardLayout title="Resume Analyzer">
      <div className="page-heading">
        <div>
          <p className="eyebrow">MAKE YOUR EXPERIENCE COUNT</p>
          <h1>Resume Analyzer</h1>
          <p className="muted">
            Your experience has a story. Let’s help it come through.
          </p>
        </div>
        <span className="ai-badge">
          <ShieldCheck size={15} />
          Only visible to your account
        </span>
      </div>
      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}
      {message && (
        <div className="success-banner" role="status">
          <Check size={17} />
          {message}
        </div>
      )}
      <div className="resume-top-grid">
        <section className="panel upload-panel">
          <div className="card-heading">
            <h3>Upload your résumé</h3>
            <span className="lavender-pill">PDF / DOCX</span>
          </div>
          <div
            className={`resume-drop ${drag ? "dragging" : ""}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDrag(true);
            }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDrag(false);
              choose(e.dataTransfer.files[0]);
            }}
          >
            <div className="upload-illustration">
              <CloudUpload size={50} strokeWidth={1.2} />
            </div>
            <h2>{file ? file.name : "Drop your résumé here"}</h2>
            <p>
              or{" "}
              <button
                className="text-button"
                onClick={() => input.current.click()}
              >
                browse files
              </button>{" "}
              to upload
            </p>
            <small>PDF or DOCX · Up to 5 MB · Text-based documents</small>
            <input
              ref={input}
              aria-label="Choose resume"
              type="file"
              accept=".pdf,.docx"
              onChange={(e) => choose(e.target.files[0])}
              hidden
            />
          </div>
          <button
            className="primary analyze-button"
            onClick={analyze}
            disabled={!file || busy}
          >
            {busy ? (
              <RefreshCw size={16} className="spinning" />
            ) : (
              <Sparkles size={16} />
            )}{" "}
            {busy ? "Reading your résumé…" : "Analyze résumé"}
          </button>
          <p className="upload-note">
            We extract your skills, education, and experience. You review what
            gets added to your profile.
          </p>
        </section>
        <section className="panel resume-score">
          <h3>Résumé completeness</h3>
          {analysis ? (
            <>
              <Ring value={analysis.score} label="Completeness" />
              <span className="green-pill">
                {analysis.score >= 75 ? "Strong foundation" : "Room to grow"}
              </span>
              <p className="muted">{analysis.word_count} words analyzed</p>
              <p className="data-note">{analysis.method}</p>
            </>
          ) : (
            <div className="empty-state">
              <FileText size={45} />
              <h3>Your story, at a glance</h3>
              <p>
                Upload a résumé to see your completeness score and suggestions.
              </p>
            </div>
          )}
        </section>
        <section className="panel checks-panel">
          <h3>What we look for</h3>
          {(
            analysis?.checks ||
            [
              "contact",
              "education",
              "skills",
              "experience",
              "projects",
              "impact",
              "portfolio",
              "summary",
            ].map((name) => ({ name, passed: null }))
          ).map((c) => (
            <div className="resume-check" key={c.name}>
              <span>{c.name}</span>
              <span className={c.passed ? "check-circle" : "pending-check"}>
                {c.passed ? (
                  <Check size={12} />
                ) : c.passed === false ? (
                  "—"
                ) : (
                  "·"
                )}
              </span>
            </div>
          ))}
        </section>
      </div>
      <div className="dashboard-columns">
        <section className="panel">
          <div className="card-heading">
            <h3>Suggestions for a stronger résumé</h3>
            <Sparkles size={17} color="#a187d0" />
          </div>
          {analysis ? (
            <div className="suggestion-list">
              {(analysis.suggestions.length
                ? analysis.suggestions
                : [
                    "All eight completeness checks passed. Tailor your projects and experience to your target role.",
                  ]
              ).map((s) => (
                <div key={s}>
                  <span className="suggestion-dot" />
                  <p>{s}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="muted">
              Personalized feedback appears after your upload. Scores are based
              on transparent structural checks, not an ATS or grammar service.
            </p>
          )}
        </section>
        <section className="resume-preview-card">
          <div className="paper-preview" aria-hidden="true">
            <strong>YOUR NEXT CHAPTER</strong>
            <span className="paper-line short" />
            <span className="paper-rule" />
            {Array.from({ length: 9 }, (_, i) => (
              <span
                className={`paper-line ${i % 3 === 0 ? "short" : ""}`}
                key={i}
              />
            ))}
          </div>
          <div>
            <span className="eyebrow">A PROFILE THAT REFLECTS YOU</span>
            <h3>More than a document.</h3>
            <p>Your résumé is the starting point for your next opportunity.</p>
            <Link to="/profile">
              View my profile <ArrowRight size={14} />
            </Link>
          </div>
        </section>
      </div>
      {resume && (
        <section className="panel parsed-review">
          <div className="card-heading">
            <div>
              <h3>Review extracted information</h3>
              <p className="muted">
                {resume.filename} ·{" "}
                {resume.parsed_information?.parser_mode?.replaceAll("_", " ") ||
                  "Resume extraction"}
              </p>
            </div>
            <FileText size={22} color="#a08ac9" />
          </div>
          {resume.parsed_information?.parse_error && (
            <div className="error-banner">
              Parsing was incomplete. Enter your details below or edit your
              profile manually.
            </div>
          )}
          <div className="parsed-fields">
            {[
              ["technical_skills", "Technical skills"],
              ["education", "Education"],
              ["job_roles", "Roles"],
              ["experience", "Experience"],
            ].map(([key, label]) => (
              <label key={key}>
                {label}
                <small>One item per line · correct anything we missed</small>
                <textarea
                  rows={5}
                  value={fields[key] || ""}
                  onChange={(e) =>
                    setFields({ ...fields, [key]: e.target.value })
                  }
                />
              </label>
            ))}
          </div>
          <div className="review-actions">
            <p className="muted">
              Skills replace your profile’s technical skills. Existing
              education, role, and experience are kept.
            </p>
            <button className="primary" disabled={saving} onClick={save}>
              {saving ? "Saving…" : "Save confirmed details"}
              <Check size={15} />
            </button>
          </div>
        </section>
      )}
    </DashboardLayout>
  );
}
