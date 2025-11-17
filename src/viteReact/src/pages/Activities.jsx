import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { activityAPI, actionAPI, authAPI, apiUtils } from "../api/client";
import "./activities.css";

/**
 * Activities page with inline modals (Create / Edit / Submit / Deactivate)
 * - Single-file for hackathon speed
 * - Glassmorphism modal style
 * - Full backend integration with Django REST API
 */

export default function Activities() {
  const [activities, setActivities] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const navigate = useNavigate();

  // Modal state
  const [openCreateModal, setOpenCreateModal] = useState(false);
  const [openEditModal, setOpenEditModal] = useState(null); // activity object
  const [openSubmitModal, setOpenSubmitModal] = useState(null); // activity object
  const [openDeactivateModal, setOpenDeactivateModal] = useState(null); // activity id

  // UX state
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const fileInputRef = useRef();

  // Load activities from backend on mount
  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await activityAPI.getActiveActivities();
      if (result.error) {
        setError(result.message || 'Failed to load activities');
      } else {
        // Transform backend data to match expected format
        const transformedActivities = (result.activities || []).map(activity => ({
          id: activity.activityId,
          name: activity.name,
          description: activity.description,
          lead: activity.leadName,
          points: activity.points,
          status: activity.isActive ? "active" : "inactive",
          submitted: 0, // Will be loaded separately or calculated
          validated: 0, // Will be loaded separately or calculated
          actions: [], // Will be loaded separately if needed
        }));
        setActivities(transformedActivities);
      }
    } catch (err) {
      setError('Network error loading activities');
      console.error('Load activities error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Helpers
  const nextId = () => {
    const max = activities.reduce((m, a) => Math.max(m, a.id), 0);
    return max + 1;
  };

  // Filtering + sorting
  const filtered = activities
    .filter((a) => a.name.toLowerCase().includes(search.toLowerCase()))
    .filter((a) => (statusFilter === "all" ? true : a.status === statusFilter))
    .sort((a, b) => {
      if (sortBy === "newest") return b.id - a.id;
      if (sortBy === "oldest") return a.id - b.id;
      if (sortBy === "highpoints") return b.points - a.points;
      if (sortBy === "lowpoints") return a.points - b.points;
      return 0;
    });

  // Create activity (backend)
  const handleCreate = async (payload) => {
    setBusy(true);
    setError(null);
    
    try {
      const result = await activityAPI.createActivity({
        name: payload.name,
        description: payload.description,
        points: Number(payload.points)
      });
      
      if (result.error) {
        setError(result.message || 'Failed to create activity');
      } else {
        // Refresh activities list
        await loadActivities();
        setOpenCreateModal(false);
      }
    } catch (err) {
      setError('Network error creating activity');
      console.error('Create activity error:', err);
    } finally {
      setBusy(false);
    }
  };

  // Edit activity (backend)
  const handleEdit = async (activityId, payload) => {
    setBusy(true);
    setError(null);
    
    try {
      // Transform payload to match API format
      const updateData = {
        activityId: activityId,
        title: payload.name || payload.title,
        description: payload.description,
        points: Number(payload.points),
        tags: payload.tags || [],
        expiry: payload.expiry || null
      };

      const result = await activityAPI.updateActivity(updateData);

      if (result.error) {
        setError(result.message || 'Failed to update activity');
      } else {
        // Success - refresh data and close modal
        await loadActivities();
        setOpenEditModal(null);
      }
    } catch (err) {
      setError('Network error updating activity');
      console.error("Update activity error:", err);
    } finally {
      setBusy(false);
    }
  };

  // Deactivate activity (backend)
  const handleDeactivate = async (activityId) => {
    setBusy(true);
    setError(null);
    
    try {
      const result = await activityAPI.deactivateActivity(activityId);
      
      if (result.error) {
        setError(result.message || 'Failed to deactivate activity');
      } else {
        // Refresh activities list
        await loadActivities();
        setOpenDeactivateModal(null);
      }
    } catch (err) {
      setError('Network error deactivating activity');
      console.error('Deactivate activity error:', err);
    } finally {
      setBusy(false);
    }
  };

  // Submit action (backend), with optional file hashing
  const handleSubmitAction = async ({ activityId, description, proofHash, file }) => {
    setBusy(true);
    setError(null);
    
    try {
      // Compute file hash if file provided and no manual hash
      let finalHash = proofHash || null;
      if (file && !finalHash) {
        finalHash = await computeFileHash(file);
      }

      if (!finalHash) {
        setError("Please provide either a file or proof hash");
        setBusy(false);
        return;
      }

      const result = await actionAPI.submitAction({
        activityId: activityId,
        description: description,
        proofHash: finalHash
      });

      if (result.error) {
        setError(result.message || 'Failed to submit action');
      } else {
        // Success - refresh data and close modal
        await loadActivities();
        setOpenSubmitModal(null);
      }
    } catch (err) {
      setError('Network error submitting action');
      console.error("Submit action error:", err);
    } finally {
      setBusy(false);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
  };

  // Utility: compute SHA-256 hex of a File/Blob
  const computeFileHash = async (file) => {
    const arrayBuffer = await file.arrayBuffer();
    const digest = await crypto.subtle.digest("SHA-256", arrayBuffer);
    const hashArray = Array.from(new Uint8Array(digest));
    const hashHex = "0x" + hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
    return hashHex;
  };

  // --- Render ---
  return (
    <>
      <header className="header">
        <span className="logo"><b>Credora</b></span>
        <div className="header-actions">
          <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none', marginRight: '1rem' }}>
            ← Dashboard
          </Link>
          <button className="create-btn" onClick={() => setOpenCreateModal(true)}>+ Create</button>
          <button 
            onClick={handleLogout}
            style={{
              marginLeft: '1rem',
              padding: '0.5rem 1rem',
              background: 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.3)',
              color: 'white',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </header>

      <main className="activities-page">

        <h2>Activities</h2>

        {/* Filters */}
        <div className="filters">
          <input
            aria-label="Search activities"
            type="text"
            placeholder="Search activity..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>

          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
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
                <span className={`status ${a.status}`}>{a.status}</span>
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
                <button onClick={() => setOpenEditModal(a)}>Edit</button>
                <button onClick={() => setOpenSubmitModal(a)} className="outline">Submit Action</button>

                {a.status === "active" ? (
                  <button className="danger" onClick={() => setOpenDeactivateModal(a.id)}>Deactivate</button>
                ) : (
                  <button className="outline" onClick={() => handleEdit(a.id, { status: "active" })}>Reactivate</button>
                )}

                <Link to={`/activity/${a.id}`}>
                  <button className="link-btn">View Details</button>
                </Link>
              </div>

              {/* Show minimal recent actions inline */}
              {a.actions && a.actions.length > 0 && (
                <div className="mini-actions">
                  {a.actions.slice(0, 2).map((act) => (
                    <div className="mini-action" key={act.actionId}>
                      <div className="mini-left">
                        <b>#{act.personId}</b>
                        <small className="muted">{new Date(act.createdAt).toLocaleString()}</small>
                      </div>
                      <div className="mini-right">
                        <span className={`tag ${act.status}`}>{act.status}</span>
                        <p className="mini-desc">{act.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {filtered.length === 0 && <p className="empty">No activities match your filters.</p>}
        </section>
      </main>

      {/* ----------------------------
           MODALS (single-file implementation)
          ---------------------------- */}

      {/* Create Activity Modal */}
      {openCreateModal && (
        <Modal onClose={() => setOpenCreateModal(false)} title="Create Activity">
          <CreateActivityForm
            onCreate={(payload) => handleCreate(payload)}
            onCancel={() => setOpenCreateModal(false)}
          />
        </Modal>
      )}

      {/* Edit Activity Modal */}
      {openEditModal && (
        <Modal onClose={() => setOpenEditModal(null)} title="Edit Activity">
          <EditActivityForm
            activity={openEditModal}
            onSave={(payload) => handleEdit(openEditModal.id, payload)}
            onCancel={() => setOpenEditModal(null)}
          />
        </Modal>
      )}

      {/* Submit Action Modal */}
      {openSubmitModal && (
        <Modal onClose={() => setOpenSubmitModal(null)} title={`Submit Action — ${openSubmitModal.name}`}>
          <SubmitActionForm
            activity={openSubmitModal}
            onSubmit={async ({ description, proofHash, file }) =>
              await handleSubmitAction({ activityId: openSubmitModal.id, description, proofHash, file })
            }
            onCancel={() => setOpenSubmitModal(null)}
            busy={busy}
            fileRef={fileInputRef}
          />
        </Modal>
      )}

      {/* Deactivate Confirmation Modal */}
      {openDeactivateModal && (
        <Modal onClose={() => setOpenDeactivateModal(null)} title="Deactivate Activity">
          <div className="modal-body">
            <p>Are you sure you want to deactivate this activity? Submissions will be stopped.</p>
            <div className="modal-actions">
              <button onClick={() => setOpenDeactivateModal(null)}>Cancel</button>
              <button className="danger" onClick={() => handleDeactivate(openDeactivateModal)}>Deactivate</button>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}

/* ---------------------------
   Small reusable Modal wrapper
   --------------------------- */
function Modal({ title, children, onClose }) {
  useEffect(() => {
    // lock scroll while modal is open
    document.body.style.overflow = "hidden";
    return () => (document.body.style.overflow = "");
  }, []);

  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <div className="glass-modal" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-content">{children}</div>
      </div>
    </div>
  );
}

/* ---------------------------
   CreateActivityForm
   --------------------------- */
function CreateActivityForm({ onCreate, onCancel }) {
  const [form, setForm] = useState({ name: "", description: "", lead: "", points: "" });
  const [err, setErr] = useState(null);

  const submit = (e) => {
    e.preventDefault();
    setErr(null);

    if (!form.name || form.name.length > 32) {
      return setErr("Name required (1-32 chars)");
    }
    if (!form.description || form.description.length > 256) {
      return setErr("Description required (1-256 chars)");
    }
    if (!form.lead || Number(form.lead) <= 0) {
      return setErr("Lead Person ID required (positive integer)");
    }
    if (!form.points || Number(form.points) < 1 || Number(form.points) > 1000) {
      return setErr("Points required (1-1000)");
    }

    onCreate(form);
  };

  return (
    <form className="form" onSubmit={submit}>
      <label>Activity Name</label>
      <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Beach Cleanup" />

      <label>Description</label>
      <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Short description" />

      <div className="row">
        <div style={{ flex: 1 }}>
          <label>Lead Person ID</label>
          <input type="number" value={form.lead} onChange={(e) => setForm({ ...form, lead: e.target.value })} />
        </div>
        <div style={{ flex: 1, marginLeft: 12 }}>
          <label>Points</label>
          <input type="number" value={form.points} onChange={(e) => setForm({ ...form, points: e.target.value })} />
        </div>
      </div>

      {err && <div className="form-error">{err}</div>}

      <div className="modal-actions">
        <button type="button" onClick={onCancel}>Cancel</button>
        <button type="submit" className="primary">Create Activity</button>
      </div>
    </form>
  );
}

/* ---------------------------
   EditActivityForm
   --------------------------- */
function EditActivityForm({ activity, onSave, onCancel }) {
  const [form, setForm] = useState({ name: activity.name || "", description: activity.description || "", lead: activity.lead || "", points: activity.points || "" });
  const [err, setErr] = useState(null);

  const submit = (e) => {
    e.preventDefault();
    setErr(null);

    if (!form.name || form.name.length > 32) {
      return setErr("Name required (1-32 chars)");
    }
    // Only allow name and date (tech lead asked for name + date editing). We'll keep points editable too for admin convenience.
    onSave({ name: form.name, description: form.description, lead: Number(form.lead), points: Number(form.points) });
  };

  return (
    <form className="form" onSubmit={submit}>
      <label>Activity Name</label>
      <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />

      <label>Description</label>
      <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />

      <div className="row">
        <div style={{ flex: 1 }}>
          <label>Lead Person ID</label>
          <input type="number" value={form.lead} onChange={(e) => setForm({ ...form, lead: e.target.value })} />
        </div>
        <div style={{ flex: 1, marginLeft: 12 }}>
          <label>Points</label>
          <input type="number" value={form.points} onChange={(e) => setForm({ ...form, points: e.target.value })} />
        </div>
      </div>

      {err && <div className="form-error">{err}</div>}

      <div className="modal-actions">
        <button type="button" onClick={onCancel}>Cancel</button>
        <button type="submit" className="primary">Save Changes</button>
      </div>
    </form>
  );
}

/* ---------------------------
   SubmitActionForm
   --------------------------- */
function SubmitActionForm({ activity, onSubmit, onCancel, busy, fileRef }) {
  const [description, setDescription] = useState("");
  const [proofHash, setProofHash] = useState("");
  const [file, setFile] = useState(null);
  const [err, setErr] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);

    if (!description || description.length > 256) return setErr("Description required (1-256 chars)");
    if (!file && !proofHash) return setErr("Provide a proof file or a proof hash");

    await onSubmit({ description, proofHash: proofHash || null, file: file || null });
  };

  const onFileChange = (e) => {
    setFile(e.target.files?.[0] || null);
  };

  return (
    <form className="form" onSubmit={submit}>
      <p className="muted"><b>Activity:</b> {activity.name} — {activity.points} pts</p>

      <label>Description</label>
      <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What you did..." />

      <label>Upload Proof (optional)</label>
      <input type="file" ref={fileRef} onChange={onFileChange} accept=".jpg,.jpeg,.png,.pdf" />

      <label>Or enter proof hash</label>
      <input value={proofHash} onChange={(e) => setProofHash(e.target.value)} placeholder="0xabc123..." />

      {err && <div className="form-error">{err}</div>}

      <div className="modal-actions">
        <button type="button" onClick={onCancel} disabled={busy}>Cancel</button>
        <button type="submit" className="primary" disabled={busy}>{busy ? "Submitting..." : "Submit Action"}</button>
      </div>
    </form>
  );
}
