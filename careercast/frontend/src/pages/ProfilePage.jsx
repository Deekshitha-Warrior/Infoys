import React, { useEffect, useState } from "react";
import {
  CheckCircle,
  AlertCircle,
  Loader2,
  X,
  Edit3,
  Save,
} from "lucide-react";
import DashboardLayout from "../components/DashboardLayout";
import api from "../api";

/* ── Tag input ─────────────────────────────────────────────────────────── */
function TagInput({
  value = [],
  onChange,
  placeholder,
  colorScheme = "green",
}) {
  const [input, setInput] = useState("");

  const scheme = {
    green: {
      pill: "bg-pg-100 text-pg-700 border border-pg-200",
      ring: "focus-within:border-pg-500 focus-within:ring-2 focus-within:ring-pg-500/15",
    },
    gold: {
      pill: "bg-gold-300/20 text-amber-800 border border-gold-400/40",
      ring: "focus-within:border-gold-400 focus-within:ring-2 focus-within:ring-gold-400/15",
    },
  }[colorScheme] || {
    pill: "bg-pg-100 text-pg-700 border border-pg-200",
    ring: "focus-within:border-pg-500",
  };

  function addTag(e) {
    if ((e.key === "Enter" || e.key === ",") && input.trim()) {
      e.preventDefault();
      const tag = input.trim().replace(/,$/, "");
      if (tag && !value.includes(tag)) onChange([...value, tag]);
      setInput("");
    }
  }

  return (
    <div
      className={`bg-white border border-ink-border rounded-xl px-3 py-2 flex flex-wrap gap-2 transition-all min-h-[46px] ${scheme.ring}`}
    >
      {value.map((tag) => (
        <span
          key={tag}
          className={`flex items-center gap-1 ${scheme.pill} text-xs px-2.5 py-1 rounded-full font-medium`}
        >
          {tag}
          <button
            type="button"
            onClick={() => onChange(value.filter((t) => t !== tag))}
            className="hover:opacity-60 transition-opacity"
          >
            <X size={11} />
          </button>
        </span>
      ))}
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={addTag}
        placeholder={value.length === 0 ? placeholder : "Add more…"}
        className="flex-1 bg-transparent text-sm text-ink-900 placeholder-ink-400 focus:outline-none min-w-[120px] py-0.5"
      />
    </div>
  );
}

/* ── Tag display (read-only) ────────────────────────────────────────────── */
function TagDisplay({ tags, colorScheme = "green", empty = "None added" }) {
  const cls =
    colorScheme === "green"
      ? "bg-pg-100 text-pg-700 border border-pg-200"
      : "bg-gold-300/20 text-amber-800 border border-gold-400/40";
  return (
    <div className="flex flex-wrap gap-2">
      {(tags || []).length > 0 ? (
        tags.map((s) => (
          <span
            key={s}
            className={`${cls} text-xs px-3 py-1 rounded-full font-medium`}
          >
            {s}
          </span>
        ))
      ) : (
        <span className="text-ink-400 text-sm italic">{empty}</span>
      )}
    </div>
  );
}

/* ── Field label ───────────────────────────────────────────────────────── */
function Field({ label, children }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-ink-600 uppercase tracking-wider mb-2">
        {label}
      </label>
      {children}
    </div>
  );
}

const inputCls = [
  "w-full bg-white border border-ink-border rounded-xl px-4 py-2.5 text-ink-900 text-sm",
  "placeholder-ink-400 outline-none transition-all duration-150",
  "hover:border-pg-300 focus:border-pg-500 focus:ring-2 focus:ring-pg-500/15",
  "disabled:bg-surface-page disabled:text-ink-600 disabled:cursor-not-allowed",
].join(" ");
const selectCls = inputCls + " cc-select";

const QUALIFICATIONS = [
  "High School",
  "Diploma",
  "Bachelor's",
  "Master's",
  "PhD",
  "Other",
];
const EXPERIENCE_OPTIONS = [
  "Fresher (0 years)",
  "Less than 1 year",
  "1-2 years",
  "2-3 years",
  "3-5 years",
  "5-7 years",
  "7-10 years",
  "10+ years",
];

/* ── Section card ──────────────────────────────────────────────────────── */
function SectionCard({ step, label, stepBg, lineColor, children, delay = 0 }) {
  return (
    <section
      className="bg-white rounded-2xl border border-ink-border overflow-hidden animate-slide-up"
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: "both",
        boxShadow: "0 1px 3px rgb(0 0 0 / 0.06)",
      }}
    >
      <div className="h-0.5" style={{ background: lineColor }} />
      <div className="px-6 py-5">
        <h3 className="text-base font-semibold text-ink-900 flex items-center gap-3 mb-5">
          <span
            className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white shadow-sm flex-shrink-0"
            style={{ background: stepBg }}
          >
            {step}
          </span>
          {label}
        </h3>
        {children}
      </div>
    </section>
  );
}

export default function ProfilePage() {
  const [form, setForm] = useState({
    qualification: "",
    degree: "",
    specialization: "",
    institution: "",
    graduation_year: "",
    technical_skills: [],
    soft_skills: [],
    work_experience: "",
    previous_role: "",
    certifications: "",
  });
  const [editing, setEditing] = useState(false);
  const [hasProfile, setHasProfile] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/api/profile/me")
      .then((res) => {
        const p = res.data;
        setForm({
          qualification: p.qualification || "",
          degree: p.degree || "",
          specialization: p.specialization || "",
          institution: p.institution || "",
          graduation_year: p.graduation_year || "",
          technical_skills: p.technical_skills || [],
          soft_skills: p.soft_skills || [],
          work_experience: p.work_experience || "",
          previous_role: p.previous_role || "",
          certifications: p.certifications || "",
        });
        setHasProfile(!!p.profile_id);
        setEditing(!p.profile_id);
      })
      .catch(() => setEditing(true))
      .finally(() => setLoading(false));
  }, []);

  function handleChange(e) {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setSuccess("");
    setError("");
    try {
      await api.post("/api/profile/me", form);
      setHasProfile(true);
      setEditing(false);
      setSuccess("Profile saved successfully!");
      setTimeout(() => setSuccess(""), 4000);
    } catch (err) {
      setError(
        Array.isArray(err.response?.data?.detail)
          ? err.response.data.detail.map((e) => e.msg).join("; ")
          : err.response?.data?.detail || "Failed to save profile.",
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <DashboardLayout title="My Profile">
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <Loader2
            size={28}
            style={{ color: "#7653DC" }}
            className="animate-spin"
          />
          <p className="text-ink-600 text-sm">Loading your profile…</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="My Profile">
      <div className="standard-profile">
        {/* Header */}
        <div className="page-heading" style={{ animationFillMode: "both" }}>
          <div>
            <p className="eyebrow">THE FOUNDATION OF YOUR NEXT CHAPTER</p>
            <h1>My Profile</h1>
            <p className="muted">
              Keep your details current for accurate career insights.
            </p>
          </div>
          {hasProfile && !editing && (
            <button
              onClick={() => setEditing(true)}
              className="flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-xl transition-all group"
              style={{
                background: "#EFEBFC",
                border: "1px solid #D5C8F1",
                color: "#584092",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "#E9E2FA";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "#EFEBFC";
              }}
            >
              <Edit3
                size={14}
                className="group-hover:rotate-12 transition-transform"
              />
              Edit Profile
            </button>
          )}
        </div>

        {/* Alerts */}
        {success && (
          <div className="flex items-center gap-3 bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3 mb-5 animate-fade-in">
            <CheckCircle
              size={18}
              style={{ color: "#059669", flexShrink: 0 }}
            />
            <p className="text-emerald-800 text-sm font-medium">{success}</p>
          </div>
        )}
        {error && (
          <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl px-4 py-3 mb-5 animate-fade-in">
            <AlertCircle
              size={18}
              style={{ color: "#DC2626", flexShrink: 0 }}
            />
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-5">
          {/* 1. Education */}
          <SectionCard
            step="1"
            label="Education"
            stepBg="linear-gradient(135deg, #7653DC, #584092)"
            lineColor="linear-gradient(90deg, transparent, #7653DC, transparent)"
            delay={0}
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field label="Highest Qualification">
                <select
                  name="qualification"
                  value={form.qualification}
                  onChange={handleChange}
                  disabled={!editing}
                  className={selectCls}
                >
                  <option value="">Select qualification</option>
                  {QUALIFICATIONS.map((q) => (
                    <option key={q}>{q}</option>
                  ))}
                </select>
              </Field>
              <Field label="Degree / Program">
                <input
                  name="degree"
                  value={form.degree}
                  onChange={handleChange}
                  disabled={!editing}
                  placeholder="e.g. B.Tech Computer Science"
                  className={inputCls}
                />
              </Field>
              <Field label="Specialization">
                <input
                  name="specialization"
                  value={form.specialization}
                  onChange={handleChange}
                  disabled={!editing}
                  placeholder="e.g. Artificial Intelligence"
                  className={inputCls}
                />
              </Field>
              <Field label="College / Institution">
                <input
                  name="institution"
                  value={form.institution}
                  onChange={handleChange}
                  disabled={!editing}
                  placeholder="e.g. IIT Bombay"
                  className={inputCls}
                />
              </Field>
              <Field label="Graduation Year">
                <input
                  type="number"
                  name="graduation_year"
                  value={form.graduation_year}
                  onChange={handleChange}
                  disabled={!editing}
                  placeholder="e.g. 2026"
                  min="1990"
                  max={new Date().getFullYear() + 15}
                  className={inputCls}
                />
              </Field>
            </div>
          </SectionCard>

          {/* 2. Skills */}
          <SectionCard
            step="2"
            label="Skills"
            stepBg="linear-gradient(135deg, #A98ADF, #7653DC)"
            lineColor="linear-gradient(90deg, transparent, #A98ADF, transparent)"
            delay={80}
          >
            <div className="space-y-5">
              <Field label="Technical Skills">
                {editing ? (
                  <>
                    <p className="text-ink-600 text-xs mb-2">
                      Type a skill and press Enter or comma to add it as a tag
                    </p>
                    <TagInput
                      value={form.technical_skills}
                      onChange={(v) =>
                        setForm((p) => ({ ...p, technical_skills: v }))
                      }
                      placeholder="e.g. Python, React, SQL…"
                      colorScheme="green"
                    />
                  </>
                ) : (
                  <TagDisplay
                    tags={form.technical_skills}
                    colorScheme="green"
                    empty="No technical skills added yet"
                  />
                )}
              </Field>
              <Field label="Soft Skills">
                {editing ? (
                  <>
                    <p className="text-ink-600 text-xs mb-2">
                      Type a skill and press Enter or comma to add it as a tag
                    </p>
                    <TagInput
                      value={form.soft_skills}
                      onChange={(v) =>
                        setForm((p) => ({ ...p, soft_skills: v }))
                      }
                      placeholder="e.g. Communication, Leadership…"
                      colorScheme="gold"
                    />
                  </>
                ) : (
                  <TagDisplay
                    tags={form.soft_skills}
                    colorScheme="gold"
                    empty="No soft skills added yet"
                  />
                )}
              </Field>
            </div>
          </SectionCard>

          {/* 3. Professional */}
          <SectionCard
            step="3"
            label="Professional Information"
            stepBg="linear-gradient(135deg, #584092, #35274F)"
            lineColor="linear-gradient(90deg, transparent, #584092, transparent)"
            delay={160}
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field label="Work Experience">
                <select
                  name="work_experience"
                  value={form.work_experience}
                  onChange={handleChange}
                  disabled={!editing}
                  className={selectCls}
                >
                  <option value="">Select experience level</option>
                  {EXPERIENCE_OPTIONS.map((o) => (
                    <option key={o}>{o}</option>
                  ))}
                </select>
              </Field>
              <Field label="Previous Job Role">
                <input
                  name="previous_role"
                  value={form.previous_role}
                  onChange={handleChange}
                  disabled={!editing}
                  placeholder="e.g. Software Engineer Intern"
                  className={inputCls}
                />
              </Field>
              <Field label="Certifications">
                <input
                  name="certifications"
                  value={form.certifications}
                  onChange={handleChange}
                  disabled={!editing}
                  placeholder="e.g. AWS Certified, Google Data Analytics"
                  className={`${inputCls} sm:col-span-2`}
                />
              </Field>
            </div>
          </SectionCard>

          {/* Save / Cancel */}
          {editing && (
            <div
              className="flex items-center gap-3 animate-slide-up"
              style={{ animationDelay: "200ms", animationFillMode: "both" }}
            >
              <button
                type="submit"
                disabled={saving}
                className="btn-green flex items-center gap-2 px-7 py-2.5 text-sm"
              >
                {saving ? (
                  <Loader2 size={15} className="animate-spin" />
                ) : (
                  <Save size={15} />
                )}
                {saving ? "Saving…" : "Save Profile"}
              </button>
              {hasProfile && (
                <button
                  type="button"
                  onClick={() => setEditing(false)}
                  className="btn-ghost px-6 py-2.5 text-sm"
                >
                  Cancel
                </button>
              )}
            </div>
          )}
        </form>
      </div>
    </DashboardLayout>
  );
}
