import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Eye,
  EyeOff,
  AlertCircle,
  ArrowRight,
  BrainCircuit,
  Check,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import AuthVisual from "../components/AuthVisual";

function PageBg() {
  return (
    <div className="fixed inset-0 pointer-events-none z-0" aria-hidden="true">
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(135deg, #EFEBFC 0%, #FAF9FF 50%, #F8F5FF 100%)",
        }}
      />
      <div
        className="absolute inset-0 opacity-35"
        style={{
          backgroundImage:
            "radial-gradient(circle, #D5C8F1 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />
    </div>
  );
}

function InputField({
  label,
  name,
  type,
  value,
  onChange,
  placeholder,
  error,
  suffix,
}) {
  return (
    <div>
      <label className="block text-sm font-semibold text-ink-900 mb-1.5">
        {label}
      </label>
      <div className="relative">
        <input
          type={type || "text"}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={
            name === "password"
              ? "new-password"
              : name === "confirm_password"
                ? "new-password"
                : name
          }
          className={`cc-input ${error ? "error" : ""} ${suffix ? "pr-11" : ""}`}
        />
        {suffix && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            {suffix}
          </div>
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

/* ── Password strength ─────────────────────────────────────────────────── */
function PasswordStrength({ password }) {
  const checks = [
    { label: "6+ chars", ok: password.length >= 6 },
    { label: "Number", ok: /\d/.test(password) },
    { label: "Letter", ok: /[a-zA-Z]/.test(password) },
  ];
  const score = checks.filter((c) => c.ok).length;
  const colors = ["bg-red-400", "bg-warning", "bg-success"];
  if (!password) return null;
  return (
    <div className="mt-2 animate-fade-in">
      <div className="flex gap-1 mb-1.5">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full transition-all duration-300 ${i < score ? colors[score - 1] : "bg-ink-border"}`}
          />
        ))}
      </div>
      <div className="flex items-center gap-3">
        {checks.map((c) => (
          <span
            key={c.label}
            className={`text-xs flex items-center gap-1 ${c.ok ? "text-success" : "text-ink-600"}`}
          >
            <Check size={11} style={{ opacity: c.ok ? 1 : 0.3 }} /> {c.label}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [show, setShow] = useState({ password: false, confirm: false });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);

  function validate() {
    const e = {};
    if (!form.name.trim()) e.name = "Full name is required.";
    if (!form.email.trim()) e.email = "Email is required.";
    else if (!/\S+@\S+\.\S+/.test(form.email))
      e.email = "Enter a valid email address.";
    if (!form.password) e.password = "Password is required.";
    else if (form.password.length < 6)
      e.password = "Password must be at least 6 characters.";
    if (!form.confirm_password)
      e.confirm_password = "Please confirm your password.";
    else if (form.password !== form.confirm_password)
      e.confirm_password = "Passwords do not match.";
    return e;
  }

  async function handleSubmit(ev) {
    ev.preventDefault();
    setApiError("");
    const e = validate();
    if (Object.keys(e).length) {
      setErrors(e);
      return;
    }
    setErrors({});
    setLoading(true);
    try {
      await register(
        form.name,
        form.email,
        form.password,
        form.confirm_password,
      );
      navigate("/dashboard");
    } catch (err) {
      setApiError(
        err.response?.data?.detail || "Registration failed. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  function onChange(e) {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
    setErrors((p) => ({ ...p, [e.target.name]: "" }));
  }

  const eyeBtn = (field) => (
    <button
      type="button"
      onClick={() => setShow((p) => ({ ...p, [field]: !p[field] }))}
      className="text-ink-600 hover:text-pg-500 transition-colors"
    >
      {show[field] ? <EyeOff size={18} /> : <Eye size={18} />}
    </button>
  );

  return (
    <div className="auth-page min-h-screen flex items-center justify-center px-4 py-10 relative">
      <PageBg />
      <AuthVisual />

      <div className="relative z-10 w-full max-w-md animate-scale-in">
        {/* Logo */}
        <div className="flex flex-col items-center mb-7">
          <div
            className="w-13 h-13 rounded-2xl flex items-center justify-center mb-3"
            style={{
              width: "52px",
              height: "52px",
              background: "linear-gradient(135deg, #A98ADF, #35274F)",
              boxShadow: "0 8px 24px rgb(118 83 220 / 0.28)",
            }}
          >
            <BrainCircuit size={22} className="text-white" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">
            <span className="text-ink-900">Career</span>
            <span className="text-green-gradient">Cast</span>
          </h1>
          <p className="text-ink-600 text-sm mt-1">
            Join thousands building their career paths
          </p>
        </div>

        <div
          className="bg-white rounded-2xl p-8"
          style={{
            border: "1px solid #E6E0F1",
            boxShadow: "0 4px 24px rgb(0 0 0 / 0.08)",
          }}
        >
          <div
            className="h-0.5 w-full rounded-full mb-7"
            style={{
              background:
                "linear-gradient(90deg, #A98ADF, #7653DC, #C9A86A, #7653DC, #A98ADF)",
            }}
          />

          <h2 className="text-xl font-bold text-ink-900 mb-1">
            Create account
          </h2>
          <p className="text-ink-600 text-sm mb-5">
            Start your AI-powered career journey.
          </p>

          {apiError && (
            <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-xl px-4 py-3 mb-5 animate-fade-in">
              <AlertCircle
                size={16}
                style={{ color: "#DC2626", flexShrink: 0 }}
              />
              <p className="text-red-700 text-sm">{apiError}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            <InputField
              label="Full Name"
              name="name"
              value={form.name}
              onChange={onChange}
              placeholder="Jane Doe"
              error={errors.name}
            />
            <InputField
              label="Email address"
              name="email"
              type="email"
              value={form.email}
              onChange={onChange}
              placeholder="you@example.com"
              error={errors.email}
            />
            <div>
              <InputField
                label="Password"
                name="password"
                type={show.password ? "text" : "password"}
                value={form.password}
                onChange={onChange}
                placeholder="Min. 6 characters"
                error={errors.password}
                suffix={eyeBtn("password")}
              />
              <PasswordStrength password={form.password} />
            </div>
            <InputField
              label="Confirm Password"
              name="confirm_password"
              type={show.confirm ? "text" : "password"}
              value={form.confirm_password}
              onChange={onChange}
              placeholder="Repeat your password"
              error={errors.confirm_password}
              suffix={eyeBtn("confirm")}
            />

            <button
              type="submit"
              disabled={loading}
              className="btn-green w-full flex items-center justify-center gap-2 py-3 text-sm mt-1"
            >
              {loading ? (
                <>
                  <svg
                    className="animate-spin w-4 h-4"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    />
                  </svg>
                  Creating account…
                </>
              ) : (
                <>
                  Create Account <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-ink-border" />
            <span className="text-ink-600 text-xs">or</span>
            <div className="flex-1 h-px bg-ink-border" />
          </div>

          <p className="text-center text-ink-600 text-sm">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-pg-500 hover:text-pg-700 font-semibold underline underline-offset-2 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
