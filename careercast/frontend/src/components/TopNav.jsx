import React from "react";
import { Link } from "react-router-dom";
import { Search, ChevronDown, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
export default function TopNav({ title }) {
  const { user } = useAuth();
  return (
    <header className="cc-topbar">
      <form action="/careers" className="workspace-search">
        <Search size={17} />
        <input
          aria-label="Search careers"
          name="q"
          placeholder="Search careers, skills, possibilities…"
        />
        <kbd>↵</kbd>
      </form>
      <div className="topbar-right">
        <span className="ai-badge">
          <Sparkles size={14} />
          AI workspace
        </span>
        <Link className="user-menu" to="/profile">
          <span className="avatar">
            {user?.name?.slice(0, 1).toUpperCase()}
          </span>
          <span>
            <strong>{user?.name}</strong>
            <small>{title}</small>
          </span>
          <ChevronDown size={14} />
        </Link>
      </div>
    </header>
  );
}
