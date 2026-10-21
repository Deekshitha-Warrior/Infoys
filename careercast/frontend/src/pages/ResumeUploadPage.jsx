import React, { useCallback, useEffect, useState } from "react";
import {
  Upload, FileText, CheckCircle, AlertCircle, Loader2,
  RefreshCw, Save, X, ChevronDown, ChevronUp,
} from "lucide-react";
import DashboardLayout from "../components/DashboardLayout";
import api from "../api";

const MAX_MB = 5;

/* ── Tag editor ────────────────────────────────────────────────────────── */
function TagEditor({ tags, onChange, placeholder, scheme = "green" }) {
  const [input, setInput] = useState("");

  const styles = {
    green:  { pill: "bg-pg-100 text-pg-800 border border-pg-300",          ring: "#00A693" },
    teal:   { pill: "bg-emerald-50 text-emerald-800 border border-emerald-200", ring: "#059669" },
    gold:   { pill: "bg-amber-50 text-amber-800 border border-amber-200",   ring: "#C9A86A" },
  };
  const s = styles[scheme] || styles.green;

  function addTag(e) {
    if ((e.key === "Enter" || e.key === ",") && input.trim()) {
      e.preventDefault();
      const tag = input.trim().replace(/,$/, "");
      if (tag && !tags.includes(tag)) onChange([...tags, tag]);
      setInput("");
    }
  }

  return (
    <div
      className="bg-white border border-ink-border rounded-xl px-3 py-2 flex flex-wrap gap-2 min-h-[46px] transition-all"
      style={{ ["--ring-color"]: s.ring }}
      onFocus={(e) => { e.currentTarget.style.borderColor = s.ring; e.currentTarget.style.boxShadow = `0 0 0 3px ${s.ring}20`; }}
      onBlur={(e)  => { e.currentTarget.style.borderColor = "#DCEAE3"; e.currentTarget.style.boxShadow = "none"; }}
    >
      {tags.map((t) => (
        <span key={t} className={`flex items-center gap-1.5 ${s.pill} text-xs px-2.5 py-1 rounded-full font-medium`}>
          {t}
          <button type="button" onClick={() => onChange(tags.filter((x) => x !== t))} className="hover:opacity-60 transition-opacity">
            <X size={11} />
          </button>
        </span>
      ))}
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={addTag}
        placeholder={tags.length === 0 ? placeholder : "Add more…"}
        className="flex-1 bg-transparent text-sm text-ink-900 placeholder-ink-400 focus:outline-none min-w-[120px] py-0.5"
      />
    </div>
  );
}

/* ── Collapsible section ───────────────────────────────────────────────── */
function Section({ title, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-white rounded-xl border border-ink-border overflow-hidden" style={{ boxShadow: "0 1px 3px rgb(0 0 0 / 0.05)" }}>
      <button
        type="button"
        onClick={() => setOpen((p) => !p)}
        className="w-full flex items-center justify-between px-5 py-3.5 text-left transition-colors"
        style={{ background: "#F7FAF8", borderBottom: open ? "1px solid #DCEAE3" : "none" }}
        onMouseEnter={(e) => { e.currentTarget.style.background = "#DFF7EF"; }}
        onMouseLeave={(e) => { e.currentTarget.style.background = "#F7FAF8"; }}
      >
        <span className="text-sm font-semibold text-ink-900">{title}</span>
        <div className="text-ink-600">
          {open ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </div>
      </button>
      {open && (
        <div className="px-5 py-4 bg-white animate-fade-in">
          {children}
        </div>
      )}
    </div>
  );
}

/* ── File badge ────────────────────────────────────────────────────────── */
function FileBadge({ filename }) {
  const ext = filename?.split(".").pop()?.toUpperCase() || "";
  const cls = ext === "PDF"
    ? "bg-red-50 text-red-600 border-red-200"
    : "bg-emerald-50 text-emerald-700 border-emerald-200";
  return <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${cls}`}>{ext}</span>;
}

/* ── Safe date ─────────────────────────────────────────────────────────── */
function formatDate(raw) {
  if (!raw) return "Unknown date";
  const d = new Date(raw);
  return isNaN(d.getTime()) ? "Unknown date" : d.toLocaleDateString(undefined, { dateStyle: "medium" });
}

export default function ResumeUploadPage() {
  const [dragging,     setDragging]     = useState(false);
  const [file,         setFile]         = useState(null);
  const [uploading,    setUploading]    = useState(false);
  const [uploadError,  setUploadError]  = useState("");
  const [parsed,       setParsed]       = useState(null);
  const [existing,     setExisting]     = useState(null);

  const [techSkills,   setTechSkills]   = useState([]);
  const [softSkills,   setSoftSkills]   = useState([]);
  const [jobRoles,     setJobRoles]     = useState([]);
  const [experience,   setExperience]   = useState([]);
  const [education,    setEducation]    = useState([]);

  const [applying,     setApplying]     = useState(false);
  const [applySuccess, setApplySuccess] = useState("");
  const [applyError,   setApplyError]   = useState("");

  useEffect(() => {
    api.get("/api/resume/latest").then((r) => setExisting(r.data)).catch(() => {});
  }, []);

  function populateEditable(info) {
    setTechSkills(info?.technical_skills || []);
    setSoftSkills(info?.soft_skills      || []);
    setJobRoles(info?.job_roles          || []);
    setExperience(info?.experience       || []);
    setEducation(info?.education         || []);
  }

  function validateFile(f) {
    if (!f) return "No file selected.";
    const ext = f.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx"].includes(ext))
      return `Unsupported format ".${ext}". Please upload PDF or DOCX.`;
    if (f.size > MAX_MB * 1024 * 1024)
      return `File is ${(f.size / 1024 / 1024).toFixed(1)} MB — maximum is ${MAX_MB} MB.`;
    return null;
  }

  function handleFiles(files) {
    const f = files[0];
    const err = validateFile(f);
    if (err) { setUploadError(err); return; }
    setUploadError(""); setFile(f); setParsed(null);
  }

  const onDrop = useCallback((e) => {
    e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files);
  }, []);

  async function handleUpload() {
    if (!file) return;
    setUploading(true); setUploadError(""); setParsed(null);
    setApplySuccess(""); setApplyError("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await api.post("/api/resume/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setParsed(res.data);
      populateEditable(res.data.parsed_information);
      setExisting(res.data);
    } catch (err) {
      setUploadError(err.response?.data?.detail || "Upload failed. Please try again.");
    } finally { setUploading(false); }
  }

  async function handleApply() {
    if (!parsed) return;
    setApplying(true); setApplyError(""); setApplySuccess("");
    try {
      await api.post(`/api/resume/${parsed.resume_id}/apply`, {
        technical_skills: techSkills, soft_skills: softSkills,
        job_roles: jobRoles, experience, education,
      });
      setApplySuccess("Extracted data saved to your profile!");
      setTimeout(() => setApplySuccess(""), 4000);
    } catch (err) {
      setApplyError(err.response?.data?.detail || "Failed to save data.");
    } finally { setApplying(false); }
  }

  return (
    <DashboardLayout title="Resume Upload">
      <div className="max-w-3xl mx-auto space-y-5">

        {/* ── Page header ────────────────────────────────────────── */}
        <div>
          <h2 className="text-2xl font-bold text-ink-900">Resume Upload &amp; Parsing</h2>
          <p className="text-ink-600 text-sm mt-1">
            Upload your resume and let CareerCast extract key information automatically.
          </p>
        </div>

        {/* ── Previously uploaded notice ─────────────────────────── */}
        {existing && !parsed && (
          <div className="bg-white rounded-xl border border-ink-border flex items-center gap-4 px-5 py-4 animate-fade-in"
            style={{ boxShadow: "0 1px 3px rgb(0 0 0 / 0.06)", borderColor: "#A7EAD3" }}>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ background: "#DFF7EF", border: "1px solid #A7EAD3" }}>
              <FileText size={17} style={{ color: "#00A693" }} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <p className="text-ink-900 text-sm font-semibold truncate">{existing.filename}</p>
                <FileBadge filename={existing.filename} />
              </div>
              <p className="text-ink-600 text-xs">Uploaded {formatDate(existing.upload_date)}</p>
            </div>
            <button
              onClick={() => { setParsed(existing); populateEditable(existing.parsed_information); }}
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg transition-all flex-shrink-0"
              style={{ background: "#DFF7EF", border: "1px solid #A7EAD3", color: "#065F46" }}
              onMouseEnter={(e) => { e.currentTarget.style.background = "#C7F0E4"; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = "#DFF7EF"; }}
            >
              <RefreshCw size={12} /> View Parsed
            </button>
          </div>
        )}

        {/* ── Drop zone ──────────────────────────────────────────── */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => document.getElementById("resume-file-input").click()}
          className="rounded-2xl p-10 text-center cursor-pointer transition-all duration-200"
          style={{
            border: `2px dashed ${file ? "#059669" : dragging ? "#00A693" : "#5ED3AC"}`,
            background: file ? "#ECFDF5" : dragging ? "#DFF7EF" : "#F0FDF8",
            transform: dragging ? "scale(1.005)" : "scale(1)",
          }}
        >
          <input id="resume-file-input" type="file" accept=".pdf,.docx" className="hidden"
            onChange={(e) => handleFiles(e.target.files)} />

          {/* Icon container */}
          <div className="w-14 h-14 mx-auto mb-4 rounded-xl flex items-center justify-center border transition-all"
            style={{
              background: file ? "#D1FAE5" : dragging ? "#DFF7EF" : "#FFFFFF",
              borderColor: file ? "#A7F3D0" : dragging ? "#5ED3AC" : "#DCEAE3",
            }}>
            {file
              ? <CheckCircle size={26} style={{ color: "#059669" }} />
              : <Upload size={26} style={{ color: dragging ? "#00A693" : "#52645D" }} />
            }
          </div>

          {file ? (
            <div>
              <div className="flex items-center justify-center gap-2 mb-1">
                <p className="text-ink-900 font-semibold">{file.name}</p>
                <FileBadge filename={file.name} />
              </div>
              <p className="text-ink-600 text-sm">{(file.size / 1024).toFixed(1)} KB — ready to upload</p>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); setFile(null); setParsed(null); setUploadError(""); }}
                className="mt-3 text-xs text-ink-600 hover:text-red-600 transition-colors flex items-center gap-1 mx-auto"
              >
                <X size={11} /> Remove file
              </button>
            </div>
          ) : (
            <div>
              <p className="text-ink-900 font-semibold text-base mb-1">
                {dragging ? "Drop it here!" : "Drag & drop your resume"}
              </p>
              <p className="text-ink-600 text-sm mb-3">or click to browse your files</p>
              <div className="flex items-center justify-center gap-3">
                <span className="bg-red-50 border border-red-200 text-red-600 text-xs px-2.5 py-1 rounded-full font-medium">PDF</span>
                <span className="text-xs px-2.5 py-1 rounded-full font-medium" style={{ background: "#DFF7EF", border: "1px solid #A7EAD3", color: "#065F46" }}>DOCX</span>
                <span className="text-ink-600 text-xs">Max {MAX_MB} MB</span>
              </div>
            </div>
          )}
        </div>

        {/* Upload error */}
        {uploadError && (
          <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-xl px-4 py-3 animate-fade-in">
            <AlertCircle size={16} style={{ color: "#DC2626", flexShrink: 0 }} />
            <p className="text-red-700 text-sm">{uploadError}</p>
          </div>
        )}

        {/* Upload button */}
        {file && !parsed && (
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="btn-green flex items-center gap-2 px-6 py-3 text-sm animate-slide-up"
            style={{ animationFillMode: "both" }}
          >
            {uploading
              ? <><Loader2 size={15} className="animate-spin" /> Uploading &amp; Parsing…</>
              : <><Upload size={15} /> Upload &amp; Parse Resume</>
            }
          </button>
        )}

        {/* ── Parsed results ─────────────────────────────────────── */}
        {parsed && (
          <div className="space-y-4 animate-fade-in">

            {/* Results header */}
            <div className="bg-white rounded-xl border flex items-center gap-3 px-5 py-4"
              style={{ borderColor: "#A7F3D0", boxShadow: "0 1px 3px rgb(0 0 0 / 0.05)" }}>
              <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{ background: "#D1FAE5", border: "1px solid #A7F3D0" }}>
                <CheckCircle size={18} style={{ color: "#059669" }} />
              </div>
              <div>
                <p className="text-ink-900 text-sm font-semibold">Parsing complete</p>
                <p className="text-ink-600 text-xs mt-0.5">Review and edit extracted data below, then save to your profile</p>
              </div>
            </div>

            <Section title="Technical Skills" defaultOpen>
              <p className="text-ink-600 text-xs mb-3">Press Enter or comma to add · click × to remove</p>
              <TagEditor tags={techSkills} onChange={setTechSkills} placeholder="e.g. Python, React, SQL…" scheme="green" />
            </Section>

            <Section title="Education Details" defaultOpen>
              <div className="space-y-2.5">
                {education.length > 0 ? (
                  education.map((line, i) => (
                    <div key={i} className="flex items-start gap-3 group">
                      <div className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" style={{ background: "#00A693" }} />
                      <p className="text-ink-900 text-sm flex-1 leading-relaxed">{line}</p>
                      <button
                        onClick={() => setEducation(education.filter((_, j) => j !== i))}
                        className="opacity-0 group-hover:opacity-100 text-ink-600 hover:text-red-600 transition-all flex-shrink-0 mt-0.5"
                      >
                        <X size={13} />
                      </button>
                    </div>
                  ))
                ) : (
                  <p className="text-ink-600 text-sm italic">No education details extracted.</p>
                )}
              </div>
            </Section>

            <Section title="Job Roles Detected" defaultOpen>
              <TagEditor tags={jobRoles} onChange={setJobRoles} placeholder="e.g. Software Engineer…" scheme="teal" />
            </Section>

            <Section title="Experience Information" defaultOpen>
              <div className="space-y-2.5">
                {experience.length > 0 ? (
                  experience.map((line, i) => (
                    <div key={i} className="flex items-start gap-3 group">
                      <div className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" style={{ background: "#34BA98" }} />
                      <p className="text-ink-900 text-sm flex-1 leading-relaxed">{line}</p>
                      <button
                        onClick={() => setExperience(experience.filter((_, j) => j !== i))}
                        className="opacity-0 group-hover:opacity-100 text-ink-600 hover:text-red-600 transition-all flex-shrink-0 mt-0.5"
                      >
                        <X size={13} />
                      </button>
                    </div>
                  ))
                ) : (
                  <p className="text-ink-600 text-sm italic">No experience information extracted.</p>
                )}
              </div>
            </Section>

            <Section title="Soft Skills" defaultOpen={false}>
              <p className="text-ink-600 text-xs mb-3">Add soft skills manually or from your resume</p>
              <TagEditor tags={softSkills} onChange={setSoftSkills} placeholder="e.g. Communication, Leadership…" scheme="gold" />
            </Section>

            {/* Feedback */}
            {applySuccess && (
              <div className="flex items-center gap-2.5 bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3 animate-fade-in">
                <CheckCircle size={16} style={{ color: "#059669", flexShrink: 0 }} />
                <p className="text-emerald-800 text-sm font-medium">{applySuccess}</p>
              </div>
            )}
            {applyError && (
              <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-xl px-4 py-3 animate-fade-in">
                <AlertCircle size={16} style={{ color: "#DC2626", flexShrink: 0 }} />
                <p className="text-red-700 text-sm">{applyError}</p>
              </div>
            )}

            {/* Action buttons */}
            <div className="flex items-center gap-3 flex-wrap">
              <button onClick={handleApply} disabled={applying} className="btn-green flex items-center gap-2 px-6 py-3 text-sm">
                {applying
                  ? <><Loader2 size={15} className="animate-spin" /> Saving…</>
                  : <><Save size={15} /> Save to Profile</>
                }
              </button>
              <button
                onClick={() => { setFile(null); setParsed(null); setUploadError(""); setApplySuccess(""); setApplyError(""); }}
                className="btn-ghost px-5 py-3 text-sm"
              >
                Upload Different File
              </button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
