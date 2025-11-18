import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authAPI, leaderboardAPI, actionAPI } from "../api/client";
import "./ProfileDropdown.css";

export default function ProfileDropdown() {
  const [profile, setProfile] = useState(null);
  const [userDetails, setUserDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showMenu, setShowMenu] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        
        // Load comprehensive profile data
        const [profileResult, rankResult, actionsResult] = await Promise.all([
          leaderboardAPI.getMyProfile(),
          leaderboardAPI.getMyRank(),
          actionAPI.getMyActions()
        ]);

        if (!profileResult.error) {
          // Combine all the data
          const enhancedProfile = {
            ...profileResult,
            rank: rankResult.error ? null : rankResult.rank,
            actionCount: actionsResult.error ? 0 : (actionsResult.actions?.length || 0)
          };
          
          setProfile(enhancedProfile);
          
          // Extract user details for better display
          setUserDetails({
            name: profileResult.name || 'Unknown User',
            email: profileResult.email || 'No email',
            role: profileResult.role?.toLowerCase() || 'member',
            initials: (profileResult.name || profileResult.email || 'U')
              .split(' ')
              .map(word => word.charAt(0))
              .slice(0, 2)
              .join('')
              .toUpperCase()
          });
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
        // Set fallback user details
        setUserDetails({
          name: 'User',
          email: 'No email',
          role: 'member',
          initials: 'U'
        });
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showMenu && !event.target.closest('.profile-menu-container')) {
        setShowMenu(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showMenu]);

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
  };

  const toggleMenu = () => {
    setShowMenu(!showMenu);
  };

  const closeMenu = () => {
    setShowMenu(false);
  };

  return (
    <div className="profile-menu-container">
      <button 
        className="profile-menu-btn" 
        onClick={toggleMenu}
        aria-expanded={showMenu}
        aria-haspopup="true"
      >
        <div className="profile-avatar">
          {loading ? '...' : (userDetails?.initials || 'U')}
        </div>
        <div className="profile-info-compact">
          <span className="profile-name">
            {loading ? 'Loading...' : (userDetails?.name || 'User')}
          </span>
          <span className="profile-role">
            {loading ? '' : (userDetails?.role ? userDetails.role.charAt(0).toUpperCase() + userDetails.role.slice(1) : 'Member')}
          </span>
        </div>
        <svg 
          className={`dropdown-arrow ${showMenu ? 'open' : ''}`}
          width="12" 
          height="12" 
          viewBox="0 0 12 12"
          fill="currentColor"
        >
          <path d="M6 9L2 5h8l-4 4z"/>
        </svg>
      </button>
      
      {showMenu && (
        <>
          <div className="profile-menu-overlay" onClick={closeMenu}></div>
          <div className="profile-menu">
            <div className="profile-menu-header">
              <div className="profile-info">
                <h4>{userDetails?.name || 'User'}</h4>
                <p>{userDetails?.email || 'No email'}</p>
                <span className="profile-role-badge">
                  {userDetails?.role ? userDetails.role.charAt(0).toUpperCase() + userDetails.role.slice(1) : 'Member'}
                </span>
              </div>
            </div>
            
            <div className="profile-menu-items">
              <div className="profile-stats">
                <div className="stat-item">
                  <label>Score:</label>
                  <span>{profile?.reputationScore || 0}</span>
                </div>
                <div className="stat-item">
                  <label>Rank:</label>
                  <span>{profile?.rank ? `#${profile.rank}` : 'N/A'}</span>
                </div>
                <div className="stat-item">
                  <label>Actions:</label>
                  <span>{profile?.actionCount || 0}</span>
                </div>
              </div>
              
              <hr className="menu-divider" />
              
              <button 
                className="menu-item logout"
                onClick={() => {
                  closeMenu();
                  handleLogout();
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.59L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
                </svg>
                Logout
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}