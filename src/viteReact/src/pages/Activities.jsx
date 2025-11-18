import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { activityAPI, actionAPI, authAPI, leaderboardAPI } from "../api/client";
import "./activities.css";

/**
 * Activities page with role-based access control
 * - LEAD users: Can create, edit, and deactivate activities
 * - MEMBER users: Can only view activities and submit actions
 * - Full backend integration with Django REST API
 */

export default function Activities() {
  const [activities, setActivities] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const navigate = useNavigate();

  // User profile and role state
  const [userProfile, setUserProfile] = useState(null);
  const [userRole, setUserRole] = useState('member'); // Default to member

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

  // AbortController for cancelling previous requests
  const activitiesAbortRef = useRef(null);

  // Helper function to check if user is a lead
  const isLead = () => userRole?.toLowerCase() === 'lead';

  // Load activities and user profile on mount

  useEffect(() => {
    let isMounted = true;
    const loadAll = async () => {
      console.log('[Activities] useEffect: loading data...');
      try {
        await loadData(isMounted);
      } catch (e) {
        console.error('[Activities] useEffect error:', e);
      }
    };
    loadAll();
    return () => {
      isMounted = false;
      if (activitiesAbortRef.current) {
        activitiesAbortRef.current.abort();
      }
      console.log('[Activities] useEffect cleanup: component unmounted');
    };
  }, []);

  const loadData = async (isMounted = true) => {
    await Promise.all([
      loadActivities(isMounted),
      loadUserProfile(isMounted)
    ]);
  };

  const loadUserProfile = async (isMounted = true) => {
    try {
      const profileResult = await leaderboardAPI.getMyProfile();
      console.log('[Activities] loadUserProfile result:', profileResult);
      if (!profileResult.error && isMounted) {
        setUserProfile(profileResult);
        setUserRole(profileResult.role?.toLowerCase() || 'member');
      }
    } catch (err) {
      console.error('Failed to load user profile:', err);
      if (isMounted) setUserRole('member'); // Default to member on error
    }
  };

  const loadActivities = async (isMounted = true) => {
    // Abort any previous request
    if (activitiesAbortRef.current) {
      activitiesAbortRef.current.abort();
    }
    const abortController = new AbortController();
    activitiesAbortRef.current = abortController;
    setLoading(true);
    setError(null);
    try {
      const result = await activityAPI.getActiveActivities({ signal: abortController.signal });
      console.log('[Activities] loadActivities result:', result);
      if (result.error) {
        if (isMounted) setError(result.message || 'Failed to load activities');
      } else {
        // Transform backend data to match frontend format
        const transformedActivities = (result.activities || []).map(activity => ({
          activityId: activity.activityId, // Keep original field name
          id: activity.activityId, // For compatibility
          name: activity.name,
          description: activity.description,
          leadName: activity.leadName, // Keep original field name
          lead: activity.leadName, // For display compatibility
          points: activity.points,
          isActive: activity.isActive, // Keep original field name
          status: activity.isActive ? "active" : "inactive", // For filter compatibility
          participantCount: activity.participantCount || 0,
          totalActionsSubmitted: activity.totalActionsSubmitted || 0,
          actions: [], // Will be loaded separately if needed
        }));
        if (isMounted) setActivities(transformedActivities);
      }
    } catch (err) {
      if (isMounted && err.name !== 'CanceledError' && err.code !== 'ERR_CANCELED') {
        setError('Network error loading activities');
        console.error('Load activities error:', err);
      }
    } finally {
      // Only clear loading if this is the latest request
      if (isMounted && activitiesAbortRef.current === abortController) {
        setLoading(false);
      }
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
    .filter((a) => (statusFilter === "all" ? true : 
      (statusFilter === "active" && a.isActive) || 
      (statusFilter === "inactive" && !a.isActive)))
    .sort((a, b) => {
      if (sortBy === "newest") return b.activityId.localeCompare(a.activityId);
      if (sortBy === "oldest") return a.activityId.localeCompare(b.activityId);
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
        // Close modal immediately, then refresh activities list
        setOpenCreateModal(false);
        await loadActivities();
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
      // Check if this is a reactivation request
      if (payload.isActive === true) {
        // This is a reactivation request
        const result = await activityAPI.reactivateActivity(activityId);
        
        if (result.error) {
          setError(result.message || 'Failed to reactivate activity');
        } else {
          // Success - refresh data
          await loadActivities();
        }
      } else {
        // This is an edit activity details request
        // Transform payload to match API format
        const updateData = {
          activityId: activityId,
          name: payload.name || payload.title,
          description: payload.description,
          points: Number(payload.points)
        };

        const result = await activityAPI.updateActivity(updateData);

        if (result.error) {
          setError(result.message || 'Failed to update activity');
        } else {
          // Success - refresh data and close modal
          await loadActivities();
          setOpenEditModal(null);
        }
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
      // Ensure 0x prefix for blockchain compatibility
      if (finalHash && !finalHash.startsWith("0x") && finalHash.length === 64) {
        finalHash = "0x" + finalHash;
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
    // Return hash without 0x prefix to match backend validation
    const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
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
          {isLead() && (
            <button className="create-btn" onClick={() => setOpenCreateModal(true)}>+ Create</button>
          )}
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

        {/* Role-based information message */}
        {!isLead() && (
          <div className="role-info" style={{
            // backgroundColor: '#e3f2fd',
            border: '1px solid #1976d2',
            borderRadius: '6px',
            padding: '12px',
            marginBottom: '20px',
            color: '#1565c0'
          }}>
            <p>ℹ️ You are viewing as a member. You can submit actions and view activity details. Only leads can create, edit, and manage activities.</p>
          </div>
        )}

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
          {loading ? (
            <div className="loading-indicator" style={{ textAlign: 'center', padding: '2rem' }}>
              <span role="status" aria-live="polite">Loading activities...</span>
            </div>
          ) : error ? (
            <div className="error-indicator" style={{ color: '#b71c1c', textAlign: 'center', padding: '2rem' }}>
              <span role="alert">{error}</span>
            </div>
          ) : filtered.length === 0 ? (
            <p className="empty">No activities match your filters.</p>
          ) : (
            filtered.map((a) => (
              <div className="activity-card" key={a.activityId}>
                <div className="card-head">
                  <h3>{a.name}</h3>
                  <span className={`status ${a.isActive ? 'active' : 'inactive'}`}>
                    {a.isActive ? 'active' : 'inactive'}
                  </span>
                </div>

                <p className="description">{a.description}</p>

                <div className="meta">
                  <p>ID: {a.activityId} | Lead: {a.leadName}</p>
                  <p>Points: {a.points}</p>
                </div>

                <div className="stats">
                  <span>Participants: {a.participantCount}</span>
                  <span>Actions Submitted: {a.totalActionsSubmitted}</span>
                </div>

                <div className="actions">
                  {/* Lead-only actions: Edit and Deactivate/Reactivate */}
                  {isLead() && (
                    <button onClick={() => setOpenEditModal(a)}>Edit</button>
                  )}
                  
                  <button onClick={() => setOpenSubmitModal(a)} className="outline">Submit Action</button>

                  {isLead() && (
                    a.isActive ? (
                      <button className="danger" onClick={() => setOpenDeactivateModal(a.activityId)}>Deactivate</button>
                    ) : (
                      <button className="outline" onClick={() => handleEdit(a.activityId, { isActive: true })}>Reactivate</button>
                    )
                  )}

                  <Link to={`/activity/${a.activityId}`}>
                    <button className="link-btn">View Details</button>
                  </Link>
                </div>

                {/* Show minimal recent actions inline */}
                {a.actions && a.actions.length > 0 && (
                  <div className="mini-actions">
                    {a.actions.slice(0, 2).map((act) => (
                      <div className="mini-action" key={act.actionId}>
                        <div className="mini-left">
                          <b>{act.personName}</b>
                          <small className="muted">{new Date(act.submittedAt).toLocaleString()}</small>
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
            ))
          )}
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
            onSave={(payload) => handleEdit(openEditModal.activityId, payload)}
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
              await handleSubmitAction({ activityId: openSubmitModal.activityId, description, proofHash, file })
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
  const [form, setForm] = useState({ name: "", description: "", points: "" });
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
  const [form, setForm] = useState({ 
    name: activity.name || "", 
    description: activity.description || "", 
    points: activity.points || "" 
  });
  const [err, setErr] = useState(null);

  const submit = (e) => {
    e.preventDefault();
    setErr(null);

    if (!form.name || form.name.length > 32) {
      return setErr("Name required (1-32 chars)");
    }
    onSave({ name: form.name, description: form.description, points: Number(form.points) });
  };

  return (
    <form className="form" onSubmit={submit}>
      <label>Activity Name</label>
      <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />

      <label>Description</label>
      <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />

      <div className="row">
        <div style={{ flex: 1 }}>
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

  const validateProofHash = (hash) => {
    if (!hash) return false;
    // Remove 0x prefix if present
    const cleanHash = hash.startsWith('0x') ? hash.slice(2) : hash;
    // Check valid hex lengths: 32 (MD5), 40 (SHA-1), 64 (SHA-256), 128 (SHA-512)
    const validLengths = [32, 40, 64, 128];
    const isValidLength = validLengths.includes(cleanHash.length);
    const isValidHex = /^[a-fA-F0-9]+$/.test(cleanHash);
    return isValidLength && isValidHex;
  };

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);

    if (!description || description.length > 256) {
      return setErr("Description required (1-256 chars)");
    }
    
    if (!file && !proofHash) {
      return setErr("Provide a proof file or a proof hash");
    }
    
    if (proofHash && !validateProofHash(proofHash)) {
      return setErr("Proof hash must be valid hexadecimal (32, 40, 64, or 128 characters), optionally prefixed with 0x");
    }

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

      <label>Or enter proof hash (32, 40, 64, or 128 hex characters)</label>
      <input 
        value={proofHash} 
        onChange={(e) => setProofHash(e.target.value)} 
        placeholder="0xabc123..." 
        pattern="^(0x)?[a-fA-F0-9]{32}$|^(0x)?[a-fA-F0-9]{40}$|^(0x)?[a-fA-F0-9]{64}$|^(0x)?[a-fA-F0-9]{128}$"
      />

      {err && <div className="form-error">{err}</div>}

      <div className="modal-actions">
        <button type="button" onClick={onCancel} disabled={busy}>Cancel</button>
        <button type="submit" className="primary" disabled={busy}>{busy ? "Submitting..." : "Submit Action"}</button>
      </div>
    </form>
  );
}
