import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  User, FileText, CheckCircle, AlertCircle,
  ChevronRight, Briefcase, GraduationCap, Code,
  TrendingUp, Star, Zap,
} from "lucide-react";
import DashboardLayout from "../components/DashboardLayout";
import { useAuth } from "../context/AuthContext";
import api from "../api";

/* ── Skeleton ──────────────────────────────────────────────────────────── */
function Skeleton({ className = "" }) {
  return <div className={`shimmer-bg rounded-lg ${className}`} />;
}

/* ── Persian Green progress ring ──────────────────────────────────────── */
function Ring({ pct }) {
  const r    = 44;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  const color = pct === 100 ? "#059669" : "#00A693";
  return (
    <svg width="110" height="110" viewBox="0 0 110 110" className="drop-shadow">
      <circle cx="55" cy="55" r={r} fill="none" stroke="#DCEAE3" strokeWidth="8" />
      <circle
        cx="55" cy="55" r={r}
        fill="none" stroke={color} strokeWidth="8"
        strokeDasharray={`${dash} ${circ}`}
        strokeDashoffset={circ * 0.25}
        strokeLinecap="round"
        style={{ transition: "stroke-dasharray 1s cubic-bezier(0.16,1,0.3,1)" }}
      />
      <text x="55" y="53" textAnchor="middle" dominantBaseline="middle" fill="#172B25" fontSize="18" fontWeight="700">{pct}%</text>
      <text x="55" y="68" textAnchor="middle" dominantBaseline="middle" fill="#52645D" fontSize="8">
        {pct === 100 ? "Complete" : "Completed"}
      </text>
    </svg>
  );
}

/* ── Stat card ─────────────────────────────────────────────────────────── */
function StatCard({ icon: Icon, label, value, sub, iconBg, iconColor, delay = 0 }) {
  return (
    <div
      className="group bg-white rounded-2xl p-5 border border-ink-border hover:-translate-y-px animate-slide-up"
      style={{ animationDelay: `${delay}ms`, animationFillMode: "both", boxShadow: "0 1px 3px rgb(0 0 0 / 0.06)", transition: "box-shadow 0.2s ease, transform 0.2s ease" }}
      onMouseEnter={(e) => { e.currentTarget.style.boxShadow = "0 4px 16px rgb(0 0 0 / 0.10)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.boxShadow = "0 1px 3px rgb(0 0 0 / 0.06)"; }}
    >
      <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform"
        style={{ background: iconBg }}>
        <Icon style={{ width: "20px", height: "20px", color: iconColor }} />
      </div>
      <p className="text-ink-600 text-xs font-semibold uppercase tracking-wider mb-1">{label}</p>
      <p className="text-ink-900 text-xl font-bold leading-tight">{value}</p>
      {sub && <p className="text-ink-600 text-xs mt-1 truncate">{sub}</p>}
    </div>
  );
}

/* ── Info item ─────────────────────────────────────────────────────────── */
function InfoItem({ icon: Icon, label, value, iconColor }) {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex-shrink-0" style={{ color: iconColor }}>
        <Icon style={{ width: "15px", height: "15px" }} />
      </div>
      <div className="min-w-0">
        <p className="text-ink-600 text-xs uppercase tracking-wide mb-0.5">{label}</p>
        <p className="text-ink-900 text-sm font-medium truncate">{value}</p>
      </div>
    </div>
  );
}

/* ── Action card ───────────────────────────────────────────────────────── */
function ActionCard({ onClick, icon: Icon, title, subtitle, bg, border, iconBg, iconColor, delay = 0 }) {
  return (
    <button
      onClick={onClick}
      className="group w-full flex items-center justify-between rounded-2xl p-5 text-left animate-slide-up"
      style={{
        background: bg,
        border: `1px solid ${border}`,
        animationDelay: `${delay}ms`,
        animationFillMode: "both",
        transition: "box-shadow 0.2s ease, transform 0.2s ease",
      }}
      onMouseEnter={(e) => { e.currentTarget.style.boxShadow = "0 4px 16px rgb(0 0 0 / 0.10)"; e.currentTarget.style.transform = "translateY(-1px)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.boxShadow = "none"; e.currentTarget.style.transform = "none"; }}
    >
      <div className="flex items-center gap-4">
        <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform"
          style={{ background: iconBg, border: `1px solid ${border}` }}>
          <Icon style={{ width: "20px", height: "20px", color: iconColor }} />
        </div>
        <div>
          <p className="text-ink-900 font-semibold text-sm">{title}</p>
          <p className="text-ink-600 text-xs mt-0.5">{subtitle}</p>
        </div>
      </div>
      <ChevronRight style={{ width: "18px", height: "18px", color: iconColor }}
        className="opacity-0 group-hover:opacity-100 transition-all duration-200 flex-shrink-0" />
    </button>
  );
}

/* ── Main ──────────────────────────────────────────────────────────────── */
export default function DashboardPage() {
  const { user }   = useAuth();
  const navigate   = useNavigate();
  const [profile, setProfile] = useState(null);
  const [resume,  setResume]  = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      api.get("/api/profile/me"),
      api.get("/api/resume/latest"),
    ]).then(([profRes, resRes]) => {
      if (profRes.status === "fulfilled") setProfile(profRes.value.data);
      if (resRes.status  === "fulfilled") setResume(resRes.value.data);
      setLoading(false);
    });
  }, []);

  function calcCompletion(p) {
    if (!p) return 0;
    const fields = [p.qualification, p.degree, p.specialization, p.institution,
      p.graduation_year, p.work_experience, p.previous_role, p.certifications];
    const skillFields = [(p.technical_skills || []).length > 0, (p.soft_skills || []).length > 0];
    const total  = fields.length + skillFields.length;
    const filled = fields.filter(Boolean).length + skillFields.filter(Boolean).length;
    return Math.round((filled / total) * 100);
  }

  const completion = calcCompletion(profile);
  const firstName  = user?.name?.split(" ")[0] || "there";

  return (
    <DashboardLayout title="Dashboard">

      {/* ── Hero banner ──────────────────────────────────────────────── */}
      <div
        className="relative overflow-hidden rounded-2xl mb-7 border border-ink-border animate-slide-up"
        style={{
          animationFillMode: "both",
          background: "linear-gradient(135deg, #DFF7EF 0%, #F0FDF8 60%, #FFFEF7 100%)",
          boxShadow: "0 1px 3px rgb(0 0 0 / 0.06)",
        }}
      >
        {/* Dot grid */}
        <div className="absolute inset-0 opacity-30"
          style={{ backgroundImage: "radial-gradient(circle, #A7EAD3 1px, transparent 1px)", backgroundSize: "20px 20px" }} />
        {/* Gold blob */}
        <div className="absolute -top-6 -right-6 w-40 h-40 rounded-full blur-2xl"
          style={{ background: "radial-gradient(circle, #C9A86A20, transparent)" }} />

        <div className="relative px-7 py-7 flex items-start justify-between gap-6">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-3">
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full"
                style={{ background: "rgb(0 166 147 / 0.12)", border: "1px solid rgb(0 166 147 / 0.25)", color: "#065F46" }}>
                <Zap style={{ width: "11px", height: "11px" }} /> AI-Powered Platform
              </span>
            </div>
            <h2 className="text-2xl lg:text-3xl font-extrabold text-ink-900 leading-tight mb-2">
              Welcome back,{" "}
              <span className="text-green-gradient">{firstName}</span> 👋
            </h2>
            <p className="text-ink-600 text-sm max-w-lg leading-relaxed">
              Build your profile and prepare for AI-powered career path prediction.
              You're <strong style={{ color: "#00A693" }}>{completion}%</strong> of the way there.
            </p>
          </div>
          <div className="flex-shrink-0 hidden md:block">
            <Ring pct={completion} />
          </div>
        </div>
      </div>

      {/* ── Stat cards ───────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {loading ? (
          <>
            <div className="bg-white rounded-2xl p-5 h-28 shimmer-bg border border-ink-border" />
            <div className="bg-white rounded-2xl p-5 h-28 shimmer-bg border border-ink-border" />
            <div className="bg-white rounded-2xl p-5 h-28 shimmer-bg border border-ink-border" />
          </>
        ) : (
          <>
            <StatCard icon={TrendingUp} label="Profile Progress"
              value={`${completion}%`}
              sub={completion < 100 ? "Fill remaining fields" : "Profile complete!"}
              iconBg="#DFF7EF" iconColor="#00A693" delay={0} />
            <StatCard icon={FileText} label="Resume Status"
              value={resume ? "Uploaded" : "Not uploaded"}
              sub={resume ? resume.filename : "Upload PDF or DOCX"}
              iconBg={resume ? "#ECFDF5" : "#F7FAF8"} iconColor={resume ? "#059669" : "#94A69E"} delay={80} />
            <StatCard icon={Star} label="Account"
              value={user?.name || "—"} sub={user?.email}
              iconBg="#FDF8EE" iconColor="#C9A86A" delay={160} />
          </>
        )}
      </div>

      {/* ── Profile summary ──────────────────────────────────────────── */}
      <div className="bg-white rounded-2xl p-6 mb-6 border border-ink-border animate-slide-up"
        style={{ animationDelay: "200ms", animationFillMode: "both", boxShadow: "0 1px 3px rgb(0 0 0 / 0.06)" }}>
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-base font-semibold text-ink-900 flex items-center gap-2">
            <div className="w-5 h-5 rounded-md flex items-center justify-center" style={{ background: "#DFF7EF", border: "1px solid #A7EAD3" }}>
              <User style={{ width: "12px", height: "12px", color: "#00A693" }} />
            </div>
            Profile Summary
          </h3>
          {profile?.degree && (
            <button onClick={() => navigate("/profile")}
              className="text-xs font-semibold flex items-center gap-1 transition-colors"
              style={{ color: "#00A693" }}
              onMouseEnter={(e) => { e.currentTarget.style.color = "#065F46"; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = "#00A693"; }}>
              Edit <ChevronRight style={{ width: "12px", height: "12px" }} />
            </button>
          )}
        </div>

        {loading ? (
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-10" />)}
          </div>
        ) : profile?.degree || profile?.qualification ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {profile.degree         && <InfoItem icon={GraduationCap} label="Degree"         value={profile.degree}          iconColor="#00A693" />}
            {profile.specialization && <InfoItem icon={GraduationCap} label="Specialization" value={profile.specialization}   iconColor="#00A693" />}
            {profile.institution    && <InfoItem icon={GraduationCap} label="Institution"    value={profile.institution}      iconColor="#00A693" />}
            {profile.previous_role  && <InfoItem icon={Briefcase}     label="Previous Role"  value={profile.previous_role}    iconColor="#065F46" />}
            {profile.work_experience && <InfoItem icon={Briefcase}    label="Experience"     value={profile.work_experience}  iconColor="#065F46" />}
            {(profile.technical_skills || []).length > 0 && (
              <div>
                <div className="flex items-center gap-1.5 text-ink-600 text-xs uppercase tracking-wide mb-2">
                  <Code style={{ width: "12px", height: "12px" }} /> Technical Skills
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {(profile.technical_skills || []).slice(0, 5).map((s) => (
                    <span key={s} className="tag-green">{s}</span>
                  ))}
                  {(profile.technical_skills || []).length > 5 && (
                    <span className="text-ink-600 text-xs self-center">+{(profile.technical_skills || []).length - 5} more</span>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center mb-3"
              style={{ background: "#F0FDF8", border: "1px solid #DCEAE3" }}>
              <User style={{ width: "20px", height: "20px", color: "#52645D" }} />
            </div>
            <p className="text-ink-600 text-sm font-medium">No profile information saved yet</p>
            <p className="text-ink-600 text-xs mt-1">Click "Complete Profile" below to get started</p>
          </div>
        )}
      </div>

      {/* ── Action cards ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <ActionCard
          onClick={() => navigate("/profile")}
          icon={User} title="Complete Profile" subtitle="Add your education, skills & experience"
          bg="#F0FDF8" border="#A7EAD3" iconBg="#FFFFFF" iconColor="#00A693" delay={240}
        />
        <ActionCard
          onClick={() => navigate("/resume")}
          icon={FileText} title="Upload Resume" subtitle="PDF or DOCX — extracted automatically"
          bg="#F0FDF8" border="#DCEAE3" iconBg="#FFFFFF" iconColor="#00A693" delay={300}
        />
      </div>

    </DashboardLayout>
  );
}
