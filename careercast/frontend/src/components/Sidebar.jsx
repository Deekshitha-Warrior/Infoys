import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  BrainCircuit,
  LayoutDashboard,
  Compass,
  ChartNoAxesCombined,
  Route,
  FileText,
  UserRound,
  FlaskConical,
  Settings2,
  CircleHelp,
  LogOut,
  ArrowUpRight,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
const items = [
  ["/dashboard", "Dashboard", LayoutDashboard],
  ["/careers", "Career Intelligence", Compass],
  ["/skills", "Skill Analysis", ChartNoAxesCombined],
  ["/learning", "Learning Path", Route],
  ["/resume", "Resume Analyzer", FileText],
  ["/profile", "My Profile", UserRound],
  ["/models", "Model Evaluation", FlaskConical],
];
export default function Sidebar() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  return (
    <aside className="cc-sidebar">
      <NavLink to="/dashboard" className="cc-brand">
        <span className="brand-icon">
          <BrainCircuit size={27} />
        </span>
        <span>
          Career<b>Cast</b>
          <small>YOUR NEXT CHAPTER</small>
        </span>
      </NavLink>
      <p className="nav-caption">
        YOUR WORKSPACE <span>01 — 07</span>
      </p>
      <nav aria-label="Main navigation">
        {items.map(([to, label, Icon]) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `side-link ${isActive ? "selected" : ""}`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-guide">
        <span>✦</span>
        <h3>Designed for your next move.</h3>
        <p>A clearer view of your strengths. A more intentional way forward.</p>
        <NavLink to="/profile">
          Build your profile <ArrowUpRight size={15} />
        </NavLink>
      </div>
      <nav className="sidebar-bottom">
        <NavLink to="/settings" className="side-link">
          <Settings2 size={18} />
          Settings
        </NavLink>
        <NavLink to="/help" className="side-link">
          <CircleHelp size={18} />
          Help & support
        </NavLink>
        <button
          className="side-link"
          onClick={() => {
            logout();
            navigate("/login");
          }}
        >
          <LogOut size={18} />
          Sign out
        </button>
      </nav>
      <div className="sidebar-version">
        <i />
        Intelligence for your next chapter
      </div>
    </aside>
  );
}
