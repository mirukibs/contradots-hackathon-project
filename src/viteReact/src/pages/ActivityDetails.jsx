import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { activityAPI } from "../api/client";

export default function ActivityDetails() {
  const { activityId } = useParams();
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchActivity() {
      setLoading(true);
      setError(null);
      const result = await activityAPI.getActivityDetails(activityId);
      if (result.error) {
        setError(result.message || "Failed to load activity details");
      } else {
        setActivity(result);
      }
      setLoading(false);
    }
    fetchActivity();
  }, [activityId]);

  if (loading) return <div>Loading activity details...</div>;
  if (error) return <div style={{ color: "red" }}>Error: {error}</div>;
  if (!activity) return <div>No activity found.</div>;

  return (
    <div className="activity-details-page">
      <h2>Activity Details</h2>
      <div><b>Name:</b> {activity.name || activity.title}</div>
      <div><b>Description:</b> {activity.description}</div>
      <div><b>Points:</b> {activity.points}</div>
      <div><b>Lead:</b> {activity.leadId || activity.creator_id}</div>
      <div><b>Status:</b> {activity.isActive !== undefined ? (activity.isActive ? "Active" : "Inactive") : "Unknown"}</div>
      {/* Add more fields as needed */}
    </div>
  );
}
