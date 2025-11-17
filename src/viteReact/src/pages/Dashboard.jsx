import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./dashboard.css";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [score, setScore] = useState(0);
  const [recentActions, setRecentActions] = useState([]);

  // Load user data (placeholder until backend endpoints for user context)
  useEffect(() => {
    const storedUser = localStorage.getItem("user_email");
    const storedScore = localStorage.getItem("user_score");
    const storedActions = JSON.parse(localStorage.getItem("recent_actions") || "[]");

    setUser(storedUser || "Unknown User");
    setScore(storedScore || 0);
    setRecentActions(storedActions);
  }, []);

  return (
    <>
      <header className="header">
        <span className="logo">
          <b>Credora</b>
        </span>
        <span className="right">
          <b>Welcome back</b>
          <p>{user}</p>
        </span>
      </header>

      <main className="dashboard">

        <section className="hero-card">

          <div className="score-box">
            <h3>Your Social Score</h3>
            <p className="score">{score}</p>
          </div>

          <div className="quick-actions">
            <Link to="/activities">
              <button>Activities</button>
            </Link>
            <Link to="/submit-action">
              <button className="outline">Submit Action</button>
            </Link>
            <Link to="/reputation">
              <button className="outline">Reputation</button>
            </Link>
          </div>
        </section>

        <section className="recent-actions">
          <h2>Recent Actions</h2>

          {recentActions.length === 0 && (
            <p className="empty">No recent actions yet.</p>
          )}

          {recentActions.map((a, i) => (
            <div className="action-item" key={i}>
              <b>{a.activity}</b>
              <p>{a.description}</p>
              <span className={a.status}>{a.status}</span>
            </div>
          ))}
        </section>
      </main>
    </>
  );
}
