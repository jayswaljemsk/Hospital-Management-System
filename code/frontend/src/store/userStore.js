import { createStore } from "vuex";
import api from "@/utils/api";

const dashboardByRole = {
  admin: "/admin_dashboard/home",
  doctor: "/doctor_dashboard/home",
  patient: "/patient_dashboard/home",
};

export default createStore({
  state: {
    token: localStorage.getItem("access_token") || null,
    userId: localStorage.getItem("user_id") || null,
    role: localStorage.getItem("user_role") || null,
    name: localStorage.getItem("user_name") || null,
  },

  getters: {
    isAuthenticated: (state) => !!state.token,
    dashboardRoute: (state) => dashboardByRole[state.role] || "/",
  },

  mutations: {
    SET_AUTH(state, { token, userId, role, name }) {
      state.token = token || null;
      state.userId = userId || null;
      state.role = role || null;
      state.name = name || null;

      if (state.token) localStorage.setItem("access_token", state.token);
      else localStorage.removeItem("access_token");

      if (state.userId !== null && state.userId !== undefined) {
        localStorage.setItem("user_id", String(state.userId));
      } else {
        localStorage.removeItem("user_id");
      }

      if (state.role) localStorage.setItem("user_role", state.role);
      else localStorage.removeItem("user_role");

      if (state.name) localStorage.setItem("user_name", state.name);
      else localStorage.removeItem("user_name");
    },

    CLEAR_AUTH(state) {
      state.token = null;
      state.userId = null;
      state.role = null;
      state.name = null;
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_id");
      localStorage.removeItem("user_role");
      localStorage.removeItem("user_name");
    },
  },

  actions: {
    async login({ commit }, credentials) {
      const response = await api.post("/login", credentials);

      const token =
        response?.access_token ||
        response?.token ||
        response?.data?.access_token ||
        response?.data?.token;

      const userId = response?.user_id || response?.data?.user_id || null;
      const role = response?.role || response?.data?.role || null;
      const name = response?.name || response?.data?.name || null;

      const message =
        response?.message || response?.data?.message || "Login successful.";
      const error = response?.error || response?.data?.error || null;

      if (error) {
        throw new Error(error);
      }

      if (!token) {
        throw new Error("Login response did not include a token");
      }

      commit("SET_AUTH", { token, userId, role, name });
      return response;
    },

    async register(_, payload) {
      return api.post("/register", payload);
    },

    logout({ commit }) {
      commit("CLEAR_AUTH");
    },
  },
});
