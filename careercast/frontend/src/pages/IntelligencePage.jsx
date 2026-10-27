import React, { useEffect, useState } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import {
  ArrowUpRight,
  ArrowRight,
  Sparkles,
  Target,
  Code2,
  Check,
  Download,
  RefreshCw,
  BookOpen,
  ShieldCheck,
  Layers3,
  GraduationCap,
  FileText,
  CircleAlert,
  Edit3,
  Save,
  X,
} from "lucide-react";
import DashboardLayout from "../components/DashboardLayout";
import { useAuth } from "../context/AuthContext";
import api from "../api";
import ReferenceDashboard from "../components/ReferenceDashboard";
const titles = {
  "/dashboard": "Overview",
  "/careers": "Career Intelligence",
  "/skills": "Skill Analysis",
  "/learning": "Learning Path",
  "/models": "Model Evaluation",
  "/settings": "Settings",
  "/help": "Help & support",
};
const descriptions = {
  "/dashboard":
    "A little clarity. A lot of possibility. Here’s where you stand.",
  "/careers": "Explore the paths that connect your skills to your ambitions.",
  "/skills": "Know your strengths. Discover what to build next.",
  "/learning": "Small steps today. Meaningful progress tomorrow.",
  "/models": "Understand the evidence behind your career recommendations.",
  "/settings": "Manage your account and the progress saved on this device.",
  "/help": "Everything you need to find your way around CareerCast.",
};
const gateLabels = {
  baseline_top1_65: "Baseline accuracy · target 65%",
  ensemble_f1_80: "Ensemble macro F1 · target 80%",
  top5_recall_90: "Top-5 career recall · target 90%",
  parser_200_resumes: "Résumé parsing · 200-document benchmark",
  semeval_linkedin: "External benchmark validation",
  embedding_mean_cosine_85: "Skill synonym similarity · target 85%",
};
const resources = {
  python: "https://docs.python.org/3/tutorial/",
  sql: "https://sqlbolt.com/",
  react: "https://react.dev/learn",
  javascript: "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
  "machine learning":
    "https://developers.google.com/machine-learning/crash-course",
  git: "https://git-scm.com/book/en/v2",
  excel: "https://support.microsoft.com/excel",
  tableau: "https://www.tableau.com/learn/training",
  "power bi": "https://learn.microsoft.com/power-bi/",
  pandas: "https://pandas.pydata.org/docs/getting_started/",
};
export function Ring({ value = 0, label = "Skill alignment" }) {
  return (
    <div
      className="ring"
      role="img"
      aria-label={`${label}: ${value}%`}
      style={{ "--value": `${value}%` }}
    >
      <div>
        <strong>
          {value}
          <sup>%</sup>
        </strong>
        <small>{label}</small>
      </div>
    </div>
  );
}
function Bar({ value }) {
  return (
    <div className="metric-track">
      <i style={{ width: `${value}%` }} />
    </div>
  );
}
function Empty() {
  return (
    <div className="empty-state">
      <Target size={36} />
      <h3>Let’s find your next direction</h3>
      <p>
        Add your skills, then analyze your profile to unlock personalized career
        recommendations.
      </p>
      <Link className="primary" to="/profile">
        Complete my profile <ArrowRight size={16} />
      </Link>
    </div>
  );
}
function CardTitle({ title, to, label = "View all" }) {
  return (
    <div className="card-heading">
      <h3>{title}</h3>
      {to && (
        <Link to={to}>
          {label}
          <ArrowUpRight size={14} />
        </Link>
      )}
    </div>
  );
}
export default function IntelligencePage() {
  const { pathname } = useLocation(),
    [params] = useSearchParams(),
    { user, updateName } = useAuth();
  const [profile, setProfile] = useState(null),
    [report, setReport] = useState(null),
    [models, setModels] = useState(null),
    [analysis, setAnalysis] = useState(null),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [selected, setSelected] = useState(params.get("career") || ""),
    [progress, setProgress] = useState({}),
    [nameDraft, setNameDraft] = useState(user?.name || ""),
    [editingName, setEditingName] = useState(false),
    [savingName, setSavingName] = useState(false);
  const title = titles[pathname] || "Overview";
  useEffect(() => {
    if (params.get("career")) setSelected(params.get("career"));
  }, [params]);
  useEffect(() => {
    let live = true;
    setLoading(true);
    setError("");
    Promise.all([
      api.get("/api/profile/me"),
      api.get("/api/intelligence/history"),
      api.get("/api/intelligence/models"),
      api.get("/api/intelligence/resume-analysis").catch((e) => {
        if (e.response?.status === 404) return { data: null };
        throw e;
      }),
    ])
      .then(([p, h, m, a]) => {
        if (live) {
          setProfile(p.data);
          setReport(h.data[0]?.is_current ? h.data[0].report : null);
          setModels(m.data);
          setAnalysis(a.data);
        }
      })
      .catch(
        (e) =>
          live &&
          setError(
            e.response?.data?.detail ||
              "Could not load your workspace. Check that the backend is running.",
          ),
      )
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
  }, [pathname]);
  useEffect(() => {
    try {
      setProgress(
        JSON.parse(
          localStorage.getItem(`cc_learning_${user?.user_id}`) || "{}",
        ),
      );
    } catch {
      setProgress({});
    }
  }, [user?.user_id]);
  const careers = report?.recommendations || [],
    skillCareers = report?.skill_careers || careers,
    careerOptions = ["/skills", "/learning"].includes(pathname)
      ? skillCareers
      : careers,
    target =
      careerOptions.find((c) => c.career === selected) || careerOptions[0],
    skills = profile?.technical_skills || [];
  const completion = profile
    ? Math.round(
        (["degree", "institution", "graduation_year", "work_experience"].filter(
          (k) => profile[k],
        ).length /
          5) *
          100 +
          (skills.length ? 20 : 0),
      )
    : 0;
  async function generate() {
    setBusy(true);
    setError("");
    try {
      setReport((await api.post("/api/intelligence/predict")).data);
    } catch (e) {
      setError(
        e.response?.data?.detail || "Prediction failed. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function saveName(e) {
    e.preventDefault();
    const name = nameDraft.trim();
    if (!name) {
      setError("Name cannot be empty.");
      return;
    }
    setSavingName(true);
    setError("");
    try {
      await updateName(name);
      setNameDraft(name);
      setEditingName(false);
    } catch (e) {
      setError(e.response?.data?.detail || "Could not update your name.");
    } finally {
      setSavingName(false);
    }
  }
  async function exportReport() {
    setBusy(true);
    setError("");
    try {
      const reportType =
        pathname === "/skills"
          ? "skills"
          : pathname === "/careers"
            ? "careers"
            : "overview";
      const response = await api.get("/api/intelligence/report.pdf", {
        params: { career: target?.career, report_type: reportType },
        responseType: "blob",
      });
      const url = URL.createObjectURL(response.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `careercast-${reportType}-report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (e) {
      let detail = "Could not export the PDF. Please try again.";
      try {
        detail = JSON.parse(await e.response.data.text()).detail || detail;
      } catch {}
      setError(detail);
    } finally {
      setBusy(false);
    }
  }
  function toggle(skill) {
    const next = {
      ...progress,
      [`${target.career}:${skill}`]: !progress[`${target.career}:${skill}`],
    };
    setProgress(next);
    localStorage.setItem(`cc_learning_${user?.user_id}`, JSON.stringify(next));
  }
  const careerSelect = (
    <label className="career-select">
      Your target career
      <select
        value={target?.career || ""}
        onChange={(e) => setSelected(e.target.value)}
      >
        {careerOptions.map((c) => (
          <option key={c.career}>{c.career}</option>
        ))}
      </select>
    </label>
  );
  return (
    <DashboardLayout title={title}>
      <div
        className={`page-heading ${pathname === "/dashboard" ? "dashboard-page-heading" : ""}`}
      >
        <div>
          <p className="eyebrow">YOUR CAREER, WITH CLARITY</p>
          <h1>
            {pathname === "/dashboard"
              ? `Welcome back, ${user?.name?.split(" ")[0]}.`
              : title}
          </h1>
          <p className="muted">
            {descriptions[pathname] || "Your personal career workspace."}
          </p>
        </div>
        {["/dashboard", "/careers", "/skills"].includes(pathname) && (
          <div className="heading-actions">
            <button
              className="secondary"
              disabled={!report || busy}
              onClick={exportReport}
            >
              <Download size={16} />
              Export report
            </button>
            <button
              className="primary"
              disabled={busy || loading}
              onClick={generate}
            >
              <RefreshCw size={16} className={busy ? "spinning" : ""} />
              {busy
                ? "Analyzing…"
                : report
                  ? "Refresh analysis"
                  : "Analyze my profile"}
            </button>
          </div>
        )}
      </div>
      {error && (
        <div className="error-banner" role="alert">
          <CircleAlert size={18} />
          {error}
        </div>
      )}
      {loading ? (
        <div className="loading-state" role="status">
          <RefreshCw className="spinning" />
          Getting your workspace ready…
        </div>
      ) : (
        <>
          {pathname === "/dashboard" && (
            <ReferenceDashboard
              user={user}
              profile={profile}
              report={report}
              analysis={analysis}
              completion={completion}
              progress={progress}
              onGenerate={generate}
              onExport={exportReport}
              busy={busy}
            />
          )}
          {pathname === "/careers" && (
            <>
              <section className="career-hero">
                <div>
                  <span className="hero-pill">
                    <Sparkles size={14} />
                    FIND YOUR FIT
                  </span>
                  <h2>There’s more than one way forward.</h2>
                  <p>
                    Your top career matches, grounded in your profile and
                    skills.
                  </p>
                </div>
                <Target size={100} strokeWidth={1} />
              </section>
              {!report ? (
                <Empty />
              ) : (
                <>
                  <div className="dashboard-columns">
                    <section className="panel">
                      <CardTitle title="Career compatibility" />
                      <p className="muted text-small">
                        Core skill alignment · choose a path to explore
                      </p>
                      {careers
                        .filter(
                          (c) =>
                            !params.get("q") ||
                            c.career
                              .toLowerCase()
                              .includes(params.get("q").toLowerCase()),
                        )
                        .map((c) => (
                          <button
                            className={`compatibility-row ${target?.career === c.career ? "active" : ""}`}
                            key={c.career}
                            onClick={() => setSelected(c.career)}
                          >
                            <strong>{c.career}</strong>
                            <Bar value={c.alignment} />
                            <b>{c.alignment}%</b>
                          </button>
                        ))}
                    </section>
                    <section className="panel target-panel">
                      <span className="green-pill">EXPLORE THIS DIRECTION</span>
                      <h2>{target?.career}</h2>
                      <Ring value={target?.alignment} />
                      <div className="target-metrics">
                        <div>
                          <strong>{target?.confidence}%</strong>
                          <small>Model confidence</small>
                        </div>
                        <div>
                          <strong>
                            {target?.matched_skills.length}/
                            {(target?.matched_skills.length || 0) +
                              (target?.missing_skills.length || 0)}
                          </strong>
                          <small>Core skills matched</small>
                        </div>
                      </div>
                      <Link
                        className="primary"
                        to={`/skills?career=${encodeURIComponent(target?.career || "")}`}
                      >
                        View skill gaps <ArrowRight size={16} />
                      </Link>
                    </section>
                  </div>
                  <section className="panel model-comparison">
                    <CardTitle title="A second perspective, from every model" />
                    <p className="muted">
                      Each classifier weighs your profile differently. These are
                      uncalibrated class probabilities.
                    </p>
                    <div className="model-score-grid">
                      {Object.entries(target?.model_scores || {}).map(
                        ([name, value]) => (
                          <div key={name}>
                            <small>{name.replaceAll("_", " ")}</small>
                            <strong>{value}%</strong>
                            <Bar value={value} />
                          </div>
                        ),
                      )}
                    </div>
                  </section>
                  <p className="data-note">
                    {report.method} {report.data_scope}{" "}
                    <Link to="/models">See evaluation & limitations ↗</Link>
                  </p>
                </>
              )}
            </>
          )}
          {pathname === "/skills" &&
            (careerOptions.length ? (
              <>
                {careerSelect}
                <div className="dashboard-columns">
                  <section className="panel">
                    <CardTitle title="Strengths to build on" />
                    <p className="muted">
                      Your matching skills for {target?.career}.
                    </p>
                    <div className="check-list">
                      {target?.matched_skills.length ? (
                        target.matched_skills.map((s) => (
                          <div key={s}>
                            <span className="check-circle">
                              <Check size={14} />
                            </span>
                            <strong>{s}</strong>
                            <span className="green-pill">Matched</span>
                          </div>
                        ))
                      ) : (
                        <p>Add the skills you already have in your profile.</p>
                      )}
                    </div>
                  </section>
                  <section className="panel">
                    <CardTitle title="Your next growth opportunities" />
                    <div className="check-list">
                      {target?.missing_skills.map((s, i) => (
                        <div key={s}>
                          <span className="step-number">{i + 1}</span>
                          <strong>{s}</strong>
                          <span className="lavender-pill">To develop</span>
                        </div>
                      ))}
                    </div>
                    <Link
                      className="primary"
                      to={`/learning?career=${encodeURIComponent(target.career)}`}
                    >
                      Build my learning path <ArrowRight size={16} />
                    </Link>
                  </section>
                </div>
                <div className="panel">
                  <CardTitle title="All the skills you bring" />
                  <div className="skill-tags">
                    {skills.map((s) => (
                      <span key={s}>{s}</span>
                    ))}
                  </div>
                  <p className="data-note">
                    Curated core-skill checklist for each role. Vocabulary
                    coverage: {report.coverage}%. Unrecognized skills:{" "}
                    {report.unrecognized_skills?.join(", ") || "None"}.
                  </p>
                </div>
              </>
            ) : (
              <Empty />
            ))}
          {pathname === "/learning" &&
            (target ? (
              <>
                {careerSelect}
                <div className="learning-grid">
                  <section className="roadmap">
                    {[...target.matched_skills, ...target.missing_skills].map(
                      (skill, i) => {
                        const known = target.matched_skills.includes(skill),
                          done = known || progress[`${target.career}:${skill}`];
                        return (
                          <article
                            className={`roadmap-step ${done ? "done" : ""}`}
                            key={skill}
                          >
                            <span className="timeline-dot">
                              {done ? <Check size={16} /> : i + 1}
                            </span>
                            <div className="roadmap-content">
                              <div>
                                <small>
                                  STEP {String(i + 1).padStart(2, "0")}
                                </small>
                                <h3>{skill}</h3>
                                <p>
                                  {known
                                    ? "Already in your profile"
                                    : "Learn the foundations, practice, and build a small project."}
                                </p>
                              </div>
                              <span
                                className={
                                  done ? "green-pill" : "lavender-pill"
                                }
                              >
                                {done ? "Completed" : "To explore"}
                              </span>
                            </div>
                            {!known && (
                              <div className="roadmap-actions">
                                <a
                                  href={
                                    resources[skill] ||
                                    `https://www.coursera.org/search?query=${encodeURIComponent(skill)}`
                                  }
                                  target="_blank"
                                  rel="noreferrer"
                                >
                                  Explore resources <ArrowUpRight size={15} />
                                </a>
                                <label>
                                  <input
                                    type="checkbox"
                                    checked={
                                      !!progress[`${target.career}:${skill}`]
                                    }
                                    onChange={() => toggle(skill)}
                                  />
                                  Mark complete
                                </label>
                              </div>
                            )}
                          </article>
                        );
                      },
                    )}
                  </section>
                  <aside className="panel learning-summary">
                    <span className="eyebrow">YOUR DIRECTION</span>
                    <div className="learning-illustration">
                      <GraduationCap size={70} strokeWidth={1.3} />
                    </div>
                    <h2>{target.career}</h2>
                    <p className="muted">
                      Your current strengths and the skills to build next.
                    </p>
                    <Ring
                      value={Math.round(
                        ([
                          ...target.matched_skills,
                          ...target.missing_skills,
                        ].filter(
                          (s) =>
                            target.matched_skills.includes(s) ||
                            progress[`${target.career}:${s}`],
                        ).length /
                          Math.max(
                            1,
                            target.matched_skills.length +
                              target.missing_skills.length,
                          )) *
                          100,
                      )}
                      label="Roadmap progress"
                    />
                    <p className="data-note">
                      Progress is saved on this device. Add verified new skills
                      to your profile yourself.
                    </p>
                  </aside>
                </div>
              </>
            ) : (
              <Empty />
            ))}
          {pathname === "/models" && <ModelEvaluation models={models} />}
          {pathname === "/settings" && (
            <section className="panel settings-panel">
              <h2>Your account</h2>
              <p className="muted">
                Manage the details that shape your recommendations.
              </p>
              <div className="settings-row">
                <span>Name</span>
                {editingName ? (
                  <form className="settings-name-form" onSubmit={saveName}>
                    <input
                      aria-label="Name"
                      autoFocus
                      maxLength={255}
                      onChange={(e) => setNameDraft(e.target.value)}
                      value={nameDraft}
                    />
                    <button
                      className="primary"
                      disabled={savingName}
                      type="submit"
                    >
                      <Save size={16} />
                      {savingName ? "Saving…" : "Save"}
                    </button>
                    <button
                      className="secondary"
                      disabled={savingName}
                      onClick={() => {
                        setNameDraft(user?.name || "");
                        setEditingName(false);
                        setError("");
                      }}
                      type="button"
                    >
                      <X size={16} />
                      Cancel
                    </button>
                  </form>
                ) : (
                  <div className="settings-name-value">
                    <strong>{user?.name}</strong>
                    <button
                      className="secondary"
                      onClick={() => {
                        setNameDraft(user?.name || "");
                        setEditingName(true);
                      }}
                      type="button"
                    >
                      <Edit3 size={16} />
                      Edit name
                    </button>
                  </div>
                )}
              </div>
              <div className="settings-row">
                <span>Email</span>
                <strong>{user?.email}</strong>
              </div>
              <Link className="primary" to="/profile">
                Edit career profile <ArrowRight size={16} />
              </Link>
              <hr />
              <h3>Learning progress</h3>
              <p className="muted">
                Saved locally in this browser for your account.
              </p>
              <button
                className="secondary"
                onClick={() => {
                  setProgress({});
                  localStorage.removeItem(`cc_learning_${user?.user_id}`);
                }}
              >
                Reset learning progress
              </button>
            </section>
          )}
          {pathname === "/help" && (
            <section className="panel help-panel">
              <h2>A clearer path, in four steps.</h2>
              {[
                [
                  "01",
                  "Make it yours",
                  "Add your education, skills, certifications and experience in My Profile.",
                ],
                [
                  "02",
                  "Let your résumé help",
                  "Upload a text-based PDF or DOCX (up to 5 MB), review the extracted details, and save them to your profile.",
                ],
                [
                  "03",
                  "Explore your possibilities",
                  "Choose Analyze my profile. Compare career recommendations and the contribution of each ML model.",
                ],
                [
                  "04",
                  "Build your next skill",
                  "Open Skill Analysis, then follow your learning roadmap and track your progress.",
                ],
              ].map(([n, h, p]) => (
                <div className="help-step" key={n}>
                  <span>{n}</span>
                  <div>
                    <h3>{h}</h3>
                    <p className="muted">{p}</p>
                  </div>
                </div>
              ))}
              <p className="data-note">
                Check Model Evaluation for measured results and limitations.
                Scanned PDFs require OCR before uploading.
              </p>
            </section>
          )}
        </>
      )}
    </DashboardLayout>
  );
}
function ModelEvaluation({ models }) {
  return (
    <>
      <section className="panel">
        <CardTitle title="Measured results. Clear limitations." />
        <p className="muted">{models?.dataset || "No training run yet"}</p>
        <div className="evaluation-summary">
          <span>
            <strong>{models?.train_rows || 0}</strong>Training profiles
          </span>
          <span>
            <strong>{models?.test_rows || 0}</strong>Held-out profiles
          </span>
          <span>
            <strong>{models?.classes?.length || 0}</strong>Career categories
          </span>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Classifier</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>Macro F1</th>
                <th>Top-5 recall</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries({
                ...models?.models,
                ...(models?.ranking
                  ? { ranked_recommendations: models.ranking }
                  : {}),
                ...(models?.ensemble ? { ensemble: models.ensemble } : {}),
              }).map(([name, m]) => (
                <tr key={name}>
                  <td>{name.replaceAll("_", " ")}</td>
                  {[
                    "accuracy",
                    "precision_macro",
                    "recall_macro",
                    "f1_macro",
                    "top5_recall",
                  ].map((k) => (
                    <td key={k}>{(m[k] * 100).toFixed(1)}%</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="data-note">{models?.split}</p>
      </section>
      <section className="panel">
        <CardTitle title="Milestone acceptance checks" />
        <div className="check-list">
          {Object.entries(models?.gates || {}).map(([key, value]) => (
            <div key={key}>
              <ShieldCheck size={19} />
              <strong>{gateLabels[key] || key.replaceAll("_", " ")}</strong>
              <span className={value === true ? "green-pill" : "lavender-pill"}>
                {value === true
                  ? "Passed"
                  : value === false
                    ? "Below target"
                    : "Not independently verified"}
              </span>
            </div>
          ))}
        </div>
        <ul className="limitations">
          {models?.limitations?.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ul>
      </section>
    </>
  );
}
