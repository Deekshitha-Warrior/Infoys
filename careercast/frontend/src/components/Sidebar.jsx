import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, User, FileText, LogOut, Leaf } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/dashboard", label: "Dashboard",     icon: LayoutDashboard },
  { to: "/profile",   label: "My Profile",    icon: User },
  { to: "/resume",    label: "Resume Upload", icon: FileText },
];

export default function Sidebar() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const initials = user?.name
    ? user.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "?";

  return (
    <aside className="fixed inset-y-0 left-0 w-64 flex flex-col z-40 bg-white border-r border-ink-border"
      style={{ boxShadow: "1px 0 0 #DCEAE3" }}>

      {/* Brand */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-ink-border">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: "linear-gradient(135deg, #00A693, #065F46)", boxShadow: "0 4px 10px rgb(0 166 147 / 0.28)" }}>
          <Leaf size={17} className="text-white" />
        </div>
        <div className="leading-none">
          <div className="text-[17px] font-extrabold tracking-tight">
            <span className="text-ink-900">Career</span>
            <span className="text-green-gradient">Cast</span>
          </div>
          <p className="text-[10px] text-ink-600 mt-0.5 tracking-wider uppercase">AI Career Platform</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `group relative flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm transition-all duration-150 ${
                isActive ? "nav-active" : "nav-inactive"
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r-full bg-pg-500" />
                )}
                <Icon
                  size={17}
                  className={isActive ? "text-pg-700 flex-shrink-0" : "text-ink-600 flex-shrink-0 group-hover:text-ink-900"}
                  strokeWidth={isActive ? 2.2 : 1.8}
                />
                <span>{label}</span>
                {isActive && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-pg-500" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Divider */}
      <div className="h-px mx-4 bg-ink-border" />

      {/* User strip + logout */}
      <div className="px-3 py-4 space-y-1">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl border border-ink-border mb-1.5"
          style={{ background: "#F0FDF8" }}>
          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-xs font-bold text-white shadow-sm"
            style={{ background: "linear-gradient(135deg, #00A693, #065F46)" }}>
            {initials}
          </div>
          <div className="min-w-0">
            <p className="text-ink-900 text-xs font-semibold truncate leading-tight">{user?.name}</p>
            <p className="text-ink-600 text-[10px] truncate">{user?.email}</p>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-ink-600 hover:text-red-700 hover:bg-red-50 border border-transparent hover:border-red-100 transition-all duration-150 group"
        >
          <LogOut size={15} className="group-hover:translate-x-0.5 transition-transform flex-shrink-0" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
