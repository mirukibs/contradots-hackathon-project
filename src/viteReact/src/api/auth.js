const API_URL = "http://localhost:8000/api"; // adjust to your backend
import { getAuthHeader } from "../api/auth";

async function fetchProtectedData() {
  const res = await fetch("http://localhost:8000/api/protected-route/", {
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
  });
  const json = await res.json();
  return json;
}


export async function registerUser(data) {
  try {
    const res = await fetch(`${API_URL}/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) {
      return { error: json };
    }
    // assume json contains token and maybe user
    return { data: json };
  } catch (err) {
    return { error: { detail: "Network error" } };
  }
}

export async function loginUser(data) {
  try {
    const res = await fetch(`${API_URL}/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) {
      return { error: json };
    }
    return { data: json };
  } catch (err) {
    return { error: { detail: "Network error" } };
  }
}

// Helper to get the auth header for future API calls
export function getAuthHeader() {
  const token = localStorage.getItem("token");
  if (!token) return {};
  return {
    Authorization: `Bearer ${token}`, // or whatever your backend expects
  };
}
