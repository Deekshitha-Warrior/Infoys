import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, AlertCircle, ArrowRight, Leaf } from "lucide-react";
import { useAuth } from "../context/AuthContext";

/* ── Ivory background with mint dot-grid ──────────────────────────────── */
function PageBg() {
  return (
    <div className="fixed inset-0 pointer-events-none z-0" aria-hidden="true">
      <div className="absolute inset-0" style={{ background: "linear-gradient(135deg, #FFFEF7 0%, #F0FDF8 50%, #DFF7EF 100%)" }} />
      <div
        className="absolute inset-0 opacity-40"
        style={{
          backgroundImage: "radial-gradient(circle, #A7EAD3 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />
    </div>
  );
}

/* ── Input field ───────────────────────────────────────────────────────── */
function InputField({ label, name, type = "text", value, onChange, placeholder, error, suffix }) {
  return (
    <div>
      <label className="block text-sm font-semibold text-ink-900 mb-1.5">{label}</label>
      <div className="relative">
        <input
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={name === "password" ? "current-password" : name}
          className={`cc-input ${error ? "error" : ""} ${suffix ? "pr-11" : ""}`}
        />
        {suffix && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">{suffix}</div>
        )}
      </div>
      {error && (
        <p className="flex items-center gap-1.5 text-danger text-xs mt-1.5 animate-fade-in">
          <AlertCircle size={12} className="flex-shrink-0" /> {error}
        </p>
      )}
    </div>
  );
}

export default function LoginPage() {
  const { login } = useAuth();
  const navigate  = useNavigate();

  const [form, setForm]         = useState({ email: "", password: "" });
  const [showPwd, setShowPwd]   = useState(false);
  const [errors, setErrors]     = useState({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading]   = useState(false);

  function validate() {
    const e = {};
    if (!form.email.trim()) e.email = "Email is required.";
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = "Enter a valid email address.";
    if (!form.password) e.password = "Password is required.";
    return e;
  }

  async function handleSubmit(ev) {
    ev.preventDefault();
    setApiError("");
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setErrors({});
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate("/dashboard");
    } catch (err) {
      setApiError(err.response?.data?.detail || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  }

  function onChange(e) {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
    setErrors((p) => ({ ...p, [e.target.name]: "" }));
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative">
      <PageBg />

      <div className="relative z-10 w-full max-w-md animate-scale-in">

        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4"
            style={{ background: "linear-gradient(135deg, #00A693, #065F46)", boxShadow: "0 8px 24px rgb(0 166 147 / 0.30)" }}>
            <Leaf size={26} className="text-white" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">
            <span className="text-ink-900">Career</span>
            <span className="text-green-gradient">Cast</span>
          </h1>
          <p className="text-ink-600 text-sm mt-1">AI-Powered Career Intelligence</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl p-8" style={{ border: "1px solid #DCEAE3", boxShadow: "0 4px 24px rgb(0 0 0 / 0.08)" }}>
          {/* Top accent line */}
          <div className="h-0.5 w-full rounded-full mb-7"
            style={{ background: "linear-gradient(90deg, #00A693, #34BA98, #C9A86A, #34BA98, #00A693)" }} />

          <h2 className="text-xl font-bold text-ink-900 mb-1">Welcome back</h2>
          <p className="text-ink-600 text-sm mb-6">Sign in to continue to your dashboard.</p>

          {apiError && (
            <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-xl px-4 py-3 mb-5 animate-fade-in">
              <AlertCircle size={16} style={{ color: "#DC2626", flexShrink: 0 }} />
              <p className="text-red-700 text-sm">{apiError}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            <InputField label="Email address" name="email" type="email" value={form.email} onChange={onChange} placeholder="you@example.com" error={errors.email} />

            <InputField
              label="Password"
              name="password"
              type={showPwd ? "text" : "password"}
              value={form.password}
              onChange={onChange}
              placeholder="••••••••"
              error={errors.password}
              suffix={
                <button
                  type="button"
                  onClick={() => setShowPwd((p) => !p)}
                  className="text-ink-600 hover:text-pg-500 transition-colors"
                  aria-label={showPwd ? "Hide password" : "Show password"}
                >
                  {showPwd ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              }
            />

            <button
              type="submit"
              disabled={loading}
              className="btn-green w-full flex items-center justify-center gap-2 py-3 text-sm mt-1"
            >
              {loading ? (
                <>
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Signing in…
                </>
              ) : (
                <>Sign In <ArrowRight size={16} /></>
              )}
            </button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-ink-border" />
            <span className="text-ink-600 text-xs">or</span>
            <div className="flex-1 h-px bg-ink-border" />
          </div>

          <p className="text-center text-ink-600 text-sm">
            Don't have an account?{" "}
            <Link to="/register" className="text-pg-500 hover:text-pg-700 font-semibold underline underline-offset-2 transition-colors">
              Create account
            </Link>
          </p>
        </div>

        <p className="text-center text-ink-600 text-xs mt-5">
          Secure · AI-Powered · Free to use
        </p>
      </div>
    </div>
  );
}
