import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authAPI, actionAPI, leaderboardAPI } from "../api/client";
import ProfileDropdown from "../components/ProfileDropdown";
import "./dashboard.css";

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [recentActions, setRecentActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Load user data and recent actions from backend
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Load user profile
        const profileResult = await leaderboardAPI.getMyProfile();
        if (profileResult.error) {
          setError(profileResult.message);
        } else {
          setProfile(profileResult.data);
        }

        // Load recent actions
        const actionsResult = await actionAPI.getMyActions();
        if (!actionsResult.error && actionsResult.data) {
          // Get the 5 most recent actions
          const recent = actionsResult.data
            .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
            .slice(0, 5);
          setRecentActions(recent);
        }

      } catch (err) {
        setError('Failed to load dashboard data');
        console.error('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  return (
    <>
      <header className="header">
        <span className="logo">
          <b>Credora</b>
        </span>
        <ProfileDropdown />
      </header>

      <main className="dashboard">

        {error && (
          <div className="error-banner">
            <p>⚠️ {error}</p>
          </div>
        )}

        <section className="hero-card">

          <div className="score-box">
            <h3>Your Social Score</h3>
            <p className="score">
              {loading ? '...' : (profile?.totalScore || 0)}
            </p>
          </div>

          <div className="quick-actions">
            <Link to="/activities">
              <button>Activities</button>
            </Link>
            <Link to="/activities#submit">
              <button className="outline">Submit Action</button>
            </Link>
            <Link to="/leaderboard">
              <button className="outline">Leaderboard</button>
            </Link>
          </div>
        </section>

        <section className="recent-actions">
          <h2>Recent Actions</h2>

          {loading && <p className="empty">Loading recent actions...</p>}

          {!loading && recentActions.length === 0 && (
            <p className="empty">No recent actions yet.</p>
          )}

          {!loading && recentActions.map((a, i) => (
            <div className="action-item" key={a.actionId || i}>
              <b>{a.activityTitle || 'Activity'}</b>
              <p>{a.description}</p>
              <span className={`status ${a.status}`}>{a.status}</span>
              <small className="timestamp">
                {new Date(a.createdAt).toLocaleString()}
              </small>
            </div>
          ))}
        </section>
      </main>
    </>
  );
}
