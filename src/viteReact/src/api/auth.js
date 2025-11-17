import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1/auth";

export async function registerUser(data) {
  try {
    const payload = {
      name: data.name,
      email: data.email,
      password: data.password
    };

    const res = await axios.post(`${API_BASE}/register/`, payload);
    return res.data;
  } catch (err) {
    if (err.response) return err.response.data;
    return { error: "NETWORK_ERROR", message: err.message };
  }
}

export async function loginUser(data) {
  try {
    const res = await axios.post(`${API_BASE}/login/`, data);
    return res.data;
  } catch (err) {
    if (err.response) return err.response.data;
    return { error: "NETWORK_ERROR", message: err.message };
  }
}

export function setAuthToken(token) {
  localStorage.setItem("token", token);
}

export function getAuthToken() {
  return localStorage.getItem("token");
}
