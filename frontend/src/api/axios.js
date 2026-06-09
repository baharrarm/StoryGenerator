export const API_BASE = import.meta.env.VITE_API_BASE || "/v1";

import axios from "axios";
const API = axios.create({ baseURL: API_BASE });

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

API.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("token");
    }
    return Promise.reject(err);
  }
);

export default API;