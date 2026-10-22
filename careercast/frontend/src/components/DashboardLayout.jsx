import React from "react";
import Sidebar from "./Sidebar";
import TopNav from "./TopNav";
import "../workspace.css";
export default function DashboardLayout({ title, children }) {
  return (
    <div className="cc-workspace">
      <Sidebar />
      <div className="workspace-body">
        <TopNav title={title} />
        <main className="workspace-main">{children}</main>
        <footer className="workspace-footer">
          Built around your potential.
          <span>CareerCast · Career Intelligence Platform</span>
        </footer>
      </div>
    </div>
  );
}
