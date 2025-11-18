import axios from "axios";

// API Base Configuration
const API_BASE_URL = "http://localhost:8000/api/v1";

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor to add authentication header
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Token ${token}`;  // Changed from Bearer to Token
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ==================== Authentication API ====================

export const authAPI = {
  async register(data) {
    try {
      const payload = {
        name: data.name,
        email: data.email,
        password: data.password,
        role: data.role
      };
      const response = await apiClient.post("/auth/register/", payload);
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async login(data) {
    try {
      const response = await apiClient.post("/auth/login/", data);
      const loginData = response.data;
      
      // Store authentication data in localStorage
      if (loginData.token) {
        localStorage.setItem("token", loginData.token);
      }
      if (loginData.user_id) {
        localStorage.setItem("user_id", loginData.user_id);
      }
      if (loginData.email) {
        localStorage.setItem("user_email", loginData.email);
      }
      
      console.log("Login successful, token stored:", loginData.token ? "Yes" : "No");
      return loginData;
    } catch (error) {
      console.error("Login error:", error);
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async logout() {
    try {
      // Make sure we have a token before attempting logout
      const token = localStorage.getItem("token");
      if (!token) {
        // No token to logout with - just clear storage
        localStorage.removeItem("token");
        return { success: true };
      }

      // Call backend logout endpoint (token will be sent via interceptor)
      await apiClient.post("/auth/logout/");
      
      // Only remove token after successful backend call
      localStorage.removeItem("token");
      return { success: true };
    } catch (error) {
      // Remove token anyway on error - logout should always succeed locally
      localStorage.removeItem("token"); 
      console.warn("Backend logout failed, but local token cleared:", error.message);
      return { success: true }; // Don't fail logout on server error
    }
  }
};

// ==================== Activity Management API ====================

export const activityAPI = {
  async createActivity(data) {
    try {
      const response = await apiClient.post("/activity_action/activities/create/", data);
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async getActiveActivities() {
    try {
      const response = await apiClient.get("/activity_action/activities/");
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async getActivityDetails(activityId) {
    try {
      const response = await apiClient.get(`/activity_action/activities/${activityId}/`);
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async updateActivity(data) {
    try {
      // Note: Backend doesn't have an update endpoint yet, this would need to be implemented
      // For now, return an error indicating this feature is not available
      return { error: "NOT_IMPLEMENTED", message: "Activity update is not yet implemented in the backend" };
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async reactivateActivity(activityId) {
    try {
      const response = await apiClient.post("/activity_action/activities/reactivate/", { activityId });
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async deactivateActivity(activityId) {
    try {
      const response = await apiClient.post("/activity_action/activities/deactivate/", { activityId });
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  }
};

// ==================== Action Management API ====================

export const actionAPI = {
  async submitAction(data) {
    try {
      const response = await apiClient.post("/activity_action/actions/submit/", data);
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async getPendingValidations() {
    try {
      const response = await apiClient.get("/activity_action/actions/pending/");
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async getMyActions() {
    try {
      const response = await apiClient.get("/activity_action/actions/my-actions/");
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async validateProof(data) {
    try {
      const response = await apiClient.post("/activity_action/actions/validate/", data);
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  }
};

// ==================== Leaderboard & Profile API ====================

export const leaderboardAPI = {
  async getLeaderboard(limit = 50, offset = 0) {
    try {
      const response = await apiClient.get(`/leaderboard/?limit=${limit}&offset=${offset}`);
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async getMyProfile() {
    try {
      const response = await apiClient.get("/leaderboard/my-profile/");
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  },

  async getMyRank() {
    try {
      const response = await apiClient.get("/leaderboard/my-rank/");
      return response.data;
    } catch (error) {
      if (error.response) return error.response.data;
      return { error: "NETWORK_ERROR", message: error.message };
    }
  }
};

// ==================== Utility Functions ====================

export const apiUtils = {
  setAuthToken(token) {
    localStorage.setItem("token", token);
  },

  getAuthToken() {
    return localStorage.getItem("token");
  },

  removeAuthToken() {
    localStorage.removeItem("token");
  },

  isAuthenticated() {
    return !!localStorage.getItem("token");
  }
};

// Default export for backwards compatibility
export default {
  auth: authAPI,
  activity: activityAPI,
  action: actionAPI,
  leaderboard: leaderboardAPI,
  utils: apiUtils
};