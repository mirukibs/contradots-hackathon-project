import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./activities.css";

export default function Activities() {
  const [activities, setActivities] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("newest");

  // Placeholder until backend is connected
  useEffect(() => {
    const demo = [
      {
        id: 1,
        name: "Beach Cleanup",
        description: "Clean local beach and collect trash",
        lead: 1,
        points: 50,
        status: "active",
        submitted: 5,
        validated: 3,
      },
      {
        id: 2,
        name: "Tree Planting",
        description: "Plant trees in the community park",
        lead: 1,
        points: 100,
        status: "active",
        submitted: 12,
        validated: 8,
      },
      {
        id: 3,
        name: "Code Review Sprint",
        description: "Review community PRs for quality assurance",
        lead: 3,
        points: 75,
        status: "inactive",
        submitted: 22,
        validated: 16,
      },
    ];

    setActivities(demo);
  }, []);

  const filtered = activities
    .filter((a) =>
      a.name.toLowerCase().includes(search.toLowerCase())
    )
    .filter((a) =>
      statusFilter === "all" ? true : a.status === statusFilter
    )
    .sort((a, b) => {
      if (sortBy === "newest") return b.id - a.id;
      if (sortBy === "oldest") return a.id - b.id;
      if (sortBy === "highpoints") return b.points - a.points;
      if (sortBy === "lowpoints") return a.points - b.points;
      return 0;
    });

  return (
    <>
      <header className="header">
        <span className="logo">
          <b>Credora</b>
        </span>
        <Link to="/create-activity">
          <button className="create-btn">+ Create</button>
        </Link>
      </header>

      <main className="activities-page">
        <span className="glow"></span>

        <h1>Activities</h1>

        {/* Filters */}
        <div className="filters">
          <input
            type="text"
            placeholder="Search activity..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
            <option value="highpoints">Points (High → Low)</option>
            <option value="lowpoints">Points (Low → High)</option>
          </select>
        </div>

        {/* List */}
        <section className="activities-list">
          {filtered.map((a) => (
            <div className="activity-card" key={a.id}>
              <div className="card-head">
                <h3>{a.name}</h3>
                <span className={`status ${a.status}`}>
                  {a.status}
                </span>
              </div>

              <p className="description">{a.description}</p>

              <div className="meta">
                <p>ID: {a.id} | Lead: Person #{a.lead}</p>
                <p>Points: {a.points}</p>
              </div>

              <div className="stats">
                <span>Submitted: {a.submitted}</span>
                <span>Validated: {a.validated}</span>
              </div>

              <div className="actions">
                <Link to={`/activity/${a.id}`}>
                  <button>View Details</button>
                </Link>

                {a.status === "active" && (
                  <button className="outline danger">
                    Deactivate
                  </button>
                )}
              </div>
            </div>
          ))}
        </section>
      </main>
    </>
  );
}
