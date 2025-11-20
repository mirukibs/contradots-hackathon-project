import { authAPI, apiUtils } from "./client.js";

// Re-export for backwards compatibility
export async function registerUser(data) {
  return await authAPI.register(data);
}

export async function loginUser(data) {
  return await authAPI.login(data);
}

export function setAuthToken(token) {
  return apiUtils.setAuthToken(token);
}

export function getAuthToken() {
  return apiUtils.getAuthToken();
}

export async function logoutUser() {
  return await authAPI.logout();
}
