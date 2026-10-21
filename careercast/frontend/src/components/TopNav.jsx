import React from "react";
import { Bell } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function TopNav({ title }) {
  const { user } = useAuth();

  const initials = user?.name
    ? user.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "?";

  return (
    <header className="h-16 bg-white border-b border-ink-border flex items-center justify-between px-8 sticky top-0 z-30"
      style={{ boxShadow: "0 1px 3px rgb(0 0 0 / 0.06)" }}>

      {/* Left: title with Persian Green accent bar */}
      <div className="flex items-center gap-3">
        <div className="w-1 h-5 rounded-full" style={{ background: "linear-gradient(180deg, #00A693, #065F46)" }} />
        <h1 className="text-base font-semibold text-ink-900 tracking-tight">{title}</h1>
      </div>

      {/* Right: bell + user pill */}
      <div className="flex items-center gap-2.5">
        <button
          className="relative w-9 h-9 rounded-xl bg-surface-page hover:bg-surface-mint border border-ink-border flex items-center justify-center text-ink-600 hover:text-pg-500 transition-all"
          aria-label="Notifications"
        >
          <Bell size={16} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full" style={{ background: "#C9A86A" }} />
        </button>

        <div className="flex items-center gap-2.5 pl-3 pr-2 py-1.5 rounded-xl bg-surface-page hover:bg-surface-mint border border-ink-border transition-all cursor-default">
          <span className="text-sm text-ink-600 hidden sm:block">
            Hi, <span className="text-ink-900 font-semibold">{user?.name?.split(" ")[0]}</span>
          </span>
          <div className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white shadow-sm flex-shrink-0"
            style={{ background: "linear-gradient(135deg, #00A693, #065F46)" }}>
            {initials}
          </div>
        </div>
      </div>
    </header>
  );
}
