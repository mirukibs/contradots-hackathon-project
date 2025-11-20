// import { useState, useEffect } from "react";
// import { Link, useNavigate } from "react-router-dom";
// import { leaderboardAPI, authAPI } from "../api/client";
// import "./leaderboard.css";

// /**
//  * Leaderboard page showing user rankings and scores
//  * - Global leaderboard with pagination
//  * - User profile display with rank
//  * - Real-time data from backend API
//  */

// export default function Leaderboard() {
//   const [leaderboard, setLeaderboard] = useState([]);
//   const [userProfile, setUserProfile] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);
//   const [page, setPage] = useState(1);
//   const [hasMore, setHasMore] = useState(false);
//   const navigate = useNavigate();

//   useEffect(() => {
//     loadLeaderboardData();
//   }, [page]);

//   const loadLeaderboardData = async () => {
//     try {
//       setLoading(true);
//       setError(null);

//       // Load leaderboard
//       const leaderboardResult = await leaderboardAPI.getLeaderboard({ 
//         page: page,
//         limit: 20 
//       });

//       if (leaderboardResult.error) {
//         setError(leaderboardResult.message);
//       } else {
//         const data = leaderboardResult.data;
//         if (page === 1) {
//           setLeaderboard(data.rankings || []);
//         } else {
//           setLeaderboard(prev => [...prev, ...(data.rankings || [])]);
//         }
//         setHasMore(data.hasMore || false);
//       }

//       // Load user profile if first page
//       if (page === 1) {
//         const profileResult = await leaderboardAPI.getMyProfile();
//         if (!profileResult.error) {
//           setUserProfile(profileResult.data);
//         }
//       }

//     } catch (err) {
//       setError('Network error loading leaderboard');
//       console.error('Leaderboard error:', err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleLoadMore = () => {
//     if (!loading && hasMore) {
//       setPage(prev => prev + 1);
//     }
//   };

//   const handleLogout = async () => {
//     await authAPI.logout();
//     navigate('/login');
//   };

//   return (
//     <>
//       <header className="header">
//         <Link to="/dashboard" className="back-btn">← Dashboard</Link>
//         <span className="logo">
//           <b>Leaderboard</b>
//         </span>
//         <button 
//           onClick={handleLogout}
//           style={{
//             padding: '0.5rem 1rem',
//             background: 'rgba(255,255,255,0.1)',
//             border: '1px solid rgba(255,255,255,0.3)',
//             color: 'white',
//             borderRadius: '6px',
//             cursor: 'pointer'
//           }}
//         >
//           Logout
//         </button>
//       </header>

//       <main className="leaderboard-page">

//         {error && (
//           <div className="error-banner">
//             <p>⚠️ {error}</p>
//           </div>
//         )}

//         {/* User Profile Card */}
//         {userProfile && (
//           <section className="user-profile-card">
//             <div className="profile-info">
//               <h3>Your Ranking</h3>
//               <div className="user-stats">
//                 <div className="stat">
//                   <span className="label">Rank</span>
//                   <span className="value">#{userProfile.rank || 'N/A'}</span>
//                 </div>
//                 <div className="stat">
//                   <span className="label">Score</span>
//                   <span className="value">{userProfile.totalScore || 0}</span>
//                 </div>
//                 <div className="stat">
//                   <span className="label">Actions</span>
//                   <span className="value">{userProfile.totalActions || 0}</span>
//                 </div>
//               </div>
//             </div>
//           </section>
//         )}

//         {/* Leaderboard Table */}
//         <section className="leaderboard-table">
//           <h2>Global Rankings</h2>
          
//           {loading && page === 1 && (
//             <p className="loading">Loading leaderboard...</p>
//           )}

//           <div className="rankings">
//             {leaderboard.map((user, index) => (
//               <div className="ranking-item" key={user.personId || index}>
//                 <div className="rank">
//                   #{((page - 1) * 20) + index + 1}
//                 </div>
//                 <div className="user-info">
//                   <h4>{user.username || user.email || 'Anonymous'}</h4>
//                   <p>{user.totalActions || 0} actions completed</p>
//                 </div>
//                 <div className="score">
//                   {user.totalScore || 0} pts
//                 </div>
//               </div>
//             ))}
//           </div>

//           {hasMore && (
//             <button 
//               className="load-more-btn" 
//               onClick={handleLoadMore}
//               disabled={loading}
//             >
//               {loading ? 'Loading...' : 'Load More'}
//             </button>
//           )}

//           {!loading && leaderboard.length === 0 && (
//             <p className="empty">No rankings available yet.</p>
//           )}
//         </section>
//       </main>
//     </>
//   );
// }