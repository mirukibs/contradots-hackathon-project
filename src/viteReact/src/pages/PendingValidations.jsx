import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { actionAPI, authAPI } from "../api/client";
import "./pending-validations.css";

/**
 * Pending Validations page for Leads to review and validate submitted actions
 * - Only accessible to users with Lead role
 * - Displays all actions with status "submitted" 
 * - Allows validation (approve/reject) with reasoning
 * - Real-time updates on validation actions
 */

export default function PendingValidations() {
  const [pendingActions, setPendingActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [validatingAction, setValidatingAction] = useState(null);
  const [validationReason, setValidationReason] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  // Load pending validations on mount
  useEffect(() => {
    loadPendingValidations();
  }, []);

  const loadPendingValidations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await actionAPI.getPendingValidations();
      if (result.error) {
        if (result.error === 'AUTHORIZATION_ERROR') {
          setError('Access denied. Only leads can view pending validations.');
        } else {
          setError(result.message || 'Failed to load pending validations');
        }
      } else {
        setPendingActions(result.actions || []);
      }
    } catch (err) {
      setError('Network error loading pending validations');
      console.error('Load pending validations error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleValidateAction = async (actionId, isValid) => {
    setBusy(true);
    setError(null);
    
    try {
      const result = await actionAPI.validateProof({
        actionId: actionId,
        isValid: isValid,
        reason: validationReason || (isValid ? "Proof validated successfully" : "Proof validation failed")
      });
      
      if (result.error) {
        setError(result.message || 'Failed to validate action');
      } else {
        // Success - refresh the list and close modal
        await loadPendingValidations();
        setValidatingAction(null);
        setValidationReason("");
      }
    } catch (err) {
      setError('Network error validating action');
      console.error('Validate action error:', err);
    } finally {
      setBusy(false);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
  };

  return (
    <>
      <header className="header">
        <span className="logo"><b>Credora</b></span>
        <div className="header-actions">
          <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none', marginRight: '1rem' }}>
            ← Dashboard
          </Link>
          <Link to="/activities" style={{ color: 'white', textDecoration: 'none', marginRight: '1rem' }}>
            Activities
          </Link>
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

      <main className="pending-validations-page">
        <h2>Pending Validations</h2>
        <p className="subtitle">Review and validate submitted actions</p>

        {error && (
          <div className="error-banner">
            <p>⚠️ {error}</p>
          </div>
        )}

        {loading && <p className="loading">Loading pending validations...</p>}

        {!loading && pendingActions.length === 0 && (
          <div className="empty-state">
            <h3>No Pending Validations</h3>
            <p>All submitted actions have been validated.</p>
            <Link to="/activities">
              <button className="primary">View Activities</button>
            </Link>
          </div>
        )}

        <section className="validations-list">
          {pendingActions.map((action) => (
            <div className="validation-card" key={action.actionId}>
              <div className="card-header">
                <div className="action-info">
                  <h3>{action.activityName}</h3>
                  <p className="submitter">Submitted by: <strong>{action.personName}</strong></p>
                  <p className="submitted-date">
                    {new Date(action.submittedAt).toLocaleDateString()} at {new Date(action.submittedAt).toLocaleTimeString()}
                  </p>
                </div>
                <span className="status submitted">submitted</span>
              </div>

              <div className="description">
                <h4>Action Description</h4>
                <p>{action.description}</p>
              </div>

              <div className="validation-actions">
                <button 
                  className="approve-btn"
                  onClick={() => setValidatingAction({ ...action, type: 'approve' })}
                  disabled={busy}
                >
                  ✓ Approve
                </button>
                <button 
                  className="reject-btn"
                  onClick={() => setValidatingAction({ ...action, type: 'reject' })}
                  disabled={busy}
                >
                  ✗ Reject
                </button>
              </div>
            </div>
          ))}
        </section>
      </main>

      {/* Validation Modal */}
      {validatingAction && (
        <div className="modal-backdrop" onClick={() => setValidatingAction(null)}>
          <div className="glass-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {validatingAction.type === 'approve' ? 'Approve' : 'Reject'} Action
              </h3>
              <button className="close" onClick={() => setValidatingAction(null)}>✕</button>
            </div>
            <div className="modal-content">
              <div className="validation-summary">
                <p><strong>Activity:</strong> {validatingAction.activityName}</p>
                <p><strong>Submitted by:</strong> {validatingAction.personName}</p>
                <p><strong>Description:</strong> {validatingAction.description}</p>
              </div>

              <form 
                className="validation-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleValidateAction(
                    validatingAction.actionId, 
                    validatingAction.type === 'approve'
                  );
                }}
              >
                <label>
                  {validatingAction.type === 'approve' ? 'Approval' : 'Rejection'} Reason (optional)
                </label>
                <textarea
                  value={validationReason}
                  onChange={(e) => setValidationReason(e.target.value)}
                  placeholder={validatingAction.type === 'approve' 
                    ? "Why is this action valid?" 
                    : "Why is this action invalid?"
                  }
                  rows="3"
                />

                <div className="modal-actions">
                  <button type="button" onClick={() => setValidatingAction(null)} disabled={busy}>
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    className={validatingAction.type === 'approve' ? 'primary approve' : 'primary reject'}
                    disabled={busy}
                  >
                    {busy ? 'Processing...' : 
                      (validatingAction.type === 'approve' ? 'Approve Action' : 'Reject Action')
                    }
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </>
  );
}