import React from "react";
import { Link } from "react-router-dom";
import {
  Target,
  BookOpen,
  ChartNoAxesCombined,
  ArrowRight,
  ArrowUpRight,
  FileUp,
  Sparkles,
  Layers3,
  Route,
  Check,
  Code2,
  BrainCircuit,
  BriefcaseBusiness,
} from "lucide-react";

function CardHeader({ icon: Icon, title, to }) {
  return (
    <div className="standard-card-heading">
      <h3>
        <Icon size={18} />
        {title}
      </h3>
      {to && (
        <Link to={to}>
          View all <ArrowRight size={13} />
        </Link>
      )}
    </div>
  );
}
export default function ReferenceDashboard({
  user,
  profile,
  report,
  analysis,
  completion,
  progress,
  onGenerate,
  onExport,
  busy,
}) {
  const careers = report?.recommendations || [],
    top = careers[0];
  const skills = profile?.technical_skills || [];
  const plan = top ? [...top.matched_skills, ...top.missing_skills] : [];
  const completed = top
    ? plan.filter(
        (s) => top.matched_skills.includes(s) || progress[`${top.career}:${s}`],
      ).length
    : 0;
  const learning = plan.length
    ? Math.round((completed / plan.length) * 100)
    : 0;
  const tiles = [
    [
      Target,
      "Career Recommendations",
      "Discover paths aligned with your skills and experience.",
      "/careers",
    ],
    [
      BookOpen,
      "Learning Resources",
      "Focused practice, useful resources and your next steps.",
      "/learning",
    ],
    [
      Layers3,
      "Skill Analysis",
      "Know your strengths and see the gaps to close.",
      "/skills",
    ],
    [
      ChartNoAxesCombined,
      "My Profile",
      "Keep your education, skills and experience up to date.",
      "/profile",
    ],
  ];
  return (
    <div className="reference-dashboard">
      <div className="reference-top-grid">
        <section className="reference-welcome">
          <div className="welcome-content">
            <span className="eyebrow">YOUR CAREER, WITH CLARITY</span>
            <h1>
              Welcome back, <em>{user?.name?.split(" ")[0]}!</em>
            </h1>
            <p>
              A little clarity. A lot of possibility. Here’s where you stand.
            </p>
            <div className="hero-stat-strip">
              {[
                [Layers3, "Your skills", skills.length, "/profile"],
                [Target, "Career matches", careers.length, "/careers"],
                [BookOpen, "Learning progress", `${learning}%`, "/learning"],
              ].map(([Icon, label, value, to]) => (
                <Link key={label} to={to}>
                  <span className="hero-stat-icon">
                    <Icon size={22} />
                  </span>
                  <span>
                    <small>{label}</small>
                    <strong>{value}</strong>
                  </span>
                  <ArrowRight size={13} />
                </Link>
              ))}
            </div>
          </div>
          <img
            className="reference-target"
            src="/images/career-target.png"
            alt=""
          />
        </section>
        <aside className="standard-card quick-actions">
          <h3>
            <Sparkles size={20} />
            Quick actions
          </h3>
          <button disabled={busy} onClick={report ? onExport : onGenerate}>
            <FileUp size={17} />
            {busy
              ? "Preparing…"
              : report
                ? "Download career report"
                : "Analyze my profile"}
            <ArrowRight size={14} />
          </button>
          <Link to="/resume">
            <FileUp size={17} />
            Upload résumé
            <ArrowRight size={14} />
          </Link>
          <Link to="/skills">
            <Target size={17} />
            Review skill gaps
            <ArrowRight size={14} />
          </Link>
        </aside>
      </div>
      <div className="reference-feature-grid">
        {tiles.map(([Icon, title, description, to]) => (
          <Link to={to} className="standard-card feature-tile" key={title}>
            <span className="feature-symbol">
              <Icon size={27} strokeWidth={1.5} />
            </span>
            <div>
              <h3>{title}</h3>
              <p>{description}</p>
            </div>
            <ArrowRight size={17} />
          </Link>
        ))}
      </div>
      <div className="reference-content-grid">
        <section className="standard-card recommendation-gallery">
          <CardHeader
            icon={Sparkles}
            title="Recommended career paths"
            to="/careers"
          />
          {careers.length ? (
            <div className="career-gallery">
              {careers.slice(0, 4).map((career, i) => {
                const Icon = /data|intelligence/i.test(career.career)
                  ? ChartNoAxesCombined
                  : /software|web/i.test(career.career)
                    ? Code2
                    : /educator/i.test(career.career)
                      ? BookOpen
                      : BriefcaseBusiness;
                return (
                  <Link
                    to={`/skills?career=${encodeURIComponent(career.career)}`}
                    className="career-gallery-card"
                    key={career.career}
                  >
                    <div className={`career-scene scene-${i}`}>
                      <div className="scene-grid" />
                      <Icon size={43} strokeWidth={1.1} />
                      <span className="scene-orb" />
                    </div>
                    <h4>{career.career}</h4>
                    <p>
                      {career.matched_skills.length} matching core skills.
                      Explore the strengths you bring and what to learn next.
                    </p>
                    <div className="gallery-match">
                      <span>{career.alignment}%</span>
                      <small>Skill alignment</small>
                      <ArrowUpRight size={14} />
                    </div>
                    <div className="gallery-tags">
                      {career.matched_skills.slice(0, 2).map((s) => (
                        <span key={s}>{s}</span>
                      ))}
                      {!career.matched_skills.length && (
                        <span>Explore this path</span>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="standard-empty">
              <Target size={35} />
              <h3>Your possibilities start with your profile.</h3>
              <p>Add your skills, then run your first career analysis.</p>
              <button className="primary" disabled={busy} onClick={onGenerate}>
                Analyze my profile <ArrowRight size={15} />
              </button>
            </div>
          )}
        </section>
        <aside className="standard-card reference-snapshot">
          <CardHeader icon={ChartNoAxesCombined} title="Your career snapshot" />
          <h4>Top skills</h4>
          <div className="skill-tags">
            {skills.length ? (
              skills.slice(0, 6).map((s) => <span key={s}>{s}</span>)
            ) : (
              <span>No skills added yet</span>
            )}
          </div>
          <dl>
            <div>
              <Target size={16} />
              <dt>Top-ranked career</dt>
              <dd>{top?.career || "Run an analysis"}</dd>
            </div>
            <div>
              <BrainCircuit size={16} />
              <dt>Specialization</dt>
              <dd>{profile?.specialization || "Add to profile"}</dd>
            </div>
            <div>
              <BookOpen size={16} />
              <dt>Education</dt>
              <dd>{profile?.degree || "Add to profile"}</dd>
            </div>
          </dl>
          <blockquote>
            “The future belongs to those who learn, adapt and grow.”
          </blockquote>
        </aside>
        <section className="standard-card reference-skill-panel">
          <CardHeader
            icon={ChartNoAxesCombined}
            title="Your profile at a glance"
            to="/skills"
          />
          <div className="reference-skill-summary">
            <div
              className="reference-score"
              style={{ "--score": `${top?.alignment || 0}%` }}
            >
              <div>
                <strong>{top ? `${top.alignment}%` : "—"}</strong>
                <small>Core skill alignment</small>
              </div>
            </div>
            <div className="reference-bars">
              {[
                ["Profile complete", completion],
                ["Learning roadmap", learning],
                ["Résumé completeness", analysis?.score || 0],
              ].map(([label, value]) => (
                <div key={label}>
                  <span>
                    {label}
                    <b>{value}%</b>
                  </span>
                  <div className="metric-track">
                    <i style={{ width: `${value}%` }} />
                  </div>
                </div>
              ))}
              <small>Based on saved information and checklist matches.</small>
            </div>
          </div>
        </section>
        <section className="standard-card reference-roadmap">
          <CardHeader icon={Route} title="Your learning path" to="/learning" />
          <div className="roadmap-overview">
            {[
              [Check, "Current skills"],
              [BookOpen, "Build foundations"],
              [Layers3, "Build a project"],
              [Target, "Explore your goal"],
            ].map(([Icon, label], i) => (
              <React.Fragment key={label}>
                {i > 0 && <span className="roadmap-connector">→</span>}
                <Link to="/learning">
                  <span
                    className={
                      i === 0 ? "roadmap-node complete" : "roadmap-node"
                    }
                  >
                    <Icon size={23} />
                  </span>
                  <small>{label}</small>
                </Link>
              </React.Fragment>
            ))}
          </div>
          <p>A focused plan for {top?.career || "your next direction"}.</p>
        </section>
        <Link to="/learning" className="reference-mountain-card">
          <h3>
            Your dream career
            <br />
            is closer than you think.
          </h3>
          <span>
            Explore learning path <ArrowUpRight size={15} />
          </span>
        </Link>
      </div>
    </div>
  );
}
