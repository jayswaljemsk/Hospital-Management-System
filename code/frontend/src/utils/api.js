const baseURL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api").replace(/\/$/, "");

function buildUrl(endpoint) {
  const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return `${baseURL}${path}`;
}

function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { "Authentication-Token": token } : {};
}

async function parseResponse(response) {
  if (response.status === 204) return null;

  const text = await response.text();
  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

const api = {
  async request(endpoint, options = {}) {
    const url = buildUrl(endpoint);

    const headers = {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...options.headers,
    };

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_id");
        localStorage.removeItem("user_role");
      }

      const payload = await parseResponse(response);

      if (!response.ok) {
        const errorMessage =
          (payload && (payload.error || payload.message)) ||
          `HTTP ${response.status}`;
        const error = new Error(errorMessage);
        error.status = response.status;
        error.payload = payload;
        throw error;
      }

      return payload;
    } catch (error) {
      if (error instanceof TypeError && /fetch/i.test(error.message)) {
        throw new Error("Network error: backend server is unreachable or blocked (CORS/server down)");
      }
      throw error;
    }
  },

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "GET" });
  },

  post(endpoint, data = {}, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  put(endpoint, data = {}, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  patch(endpoint, data = {}, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "DELETE" });
  },

  async download(endpoint, filename = "download.csv") {
    const url = buildUrl(endpoint);
    const response = await fetch(url, {
      method: "GET",
      headers: {
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) {
      const payload = await parseResponse(response);
      const errorMessage =
        (payload && (payload.error || payload.message)) ||
        `HTTP ${response.status}`;
      const error = new Error(errorMessage);
      error.status = response.status;
      error.payload = payload;
      throw error;
    }

    const blob = await response.blob();
    const objectUrl = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.URL.revokeObjectURL(objectUrl);
  },
};

export default api;
