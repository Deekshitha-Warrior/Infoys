import React from "react";
import { BrainCircuit, CheckCircle2 } from "lucide-react";
export default function AuthVisual() {
  return (
    <aside className="auth-visual">
      <div className="auth-wordmark">
        <BrainCircuit size={32} />
        <span>
          Career<b>Cast</b>
        </span>
      </div>
      <div className="auth-story">
        <p className="eyebrow">YOUR NEXT CHAPTER</p>
        <h2>
          Your skills.
          <br />
          Your possibilities.
          <br />
          <em>Your future.</em>
        </h2>
        <p>
          A thoughtful space to understand your strengths, explore career paths
          and build what comes next.
        </p>
        <div className="auth-promises">
          <span>
            <CheckCircle2 size={15} />
            Profile-based career insights
          </span>
          <span>
            <CheckCircle2 size={15} />A focused path to your next skill
          </span>
        </div>
      </div>
      <img src="/images/career-mountain.png" alt="" />
    </aside>
  );
}
