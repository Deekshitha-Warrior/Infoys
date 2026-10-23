import React from "react";
import { Link } from "react-router-dom";
import { Search, ChevronDown, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
export default function TopNav({ title }) {
  const { user } = useAuth();
  return (
    <header className="cc-topbar">
      <div className="workspace-breadcrumb">
        <span>Workspace</span>
        <span aria-hidden="true">/</span>
        <strong>{title}</strong>
      </div>
      <form action="/careers" className="workspace-search">
        <Search size={17} />
        <input
          aria-label="Search careers"
          name="q"
          placeholder="Find your next direction"
        />
        <kbd>↵</kbd>
      </form>
      <div className="topbar-right">
        <span className="ai-badge">
          <Sparkles size={14} />
          Your workspace
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
