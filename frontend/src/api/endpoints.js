import API from "./axios";

// Auth — original local endpoints (pre-Cognito, kept for portfolio)
// export const login = (data) => API.post("/auth/login", data);
// export const register = (data) => API.post("/auth/register", data);

// Auth — works in both local and Cognito mode (AUTH_PROVIDER env var on backend)
export const signup = (data) => API.post("/auth/signup", data);
export const register = signup; // backward-compatible alias
export const confirmSignup = (params) =>
  API.post("/auth/confirm", null, { params }); // { username, code }
export const login = ({ username, password, email }) =>
  API.post("/auth/login", {
    username,
    password,
    // backend login ignore value:
    email: email || `${username}@dummy.local`,
  });
export const changeEmail = (data) => API.post("/auth/email/change", data);     // { access_token, new_email }
export const confirmEmail = (data) => API.post("/auth/email/confirm", data);   // { access_token, code }
export const changePassword = (data) => API.post("/auth/password/change", data); // { access_token, old_password, new_password }

// Users
export const getMe = () => API.get("/users/me");
export const updateMe = (data) => API.patch("/users/me", data);
export const getMyPrefs = () => API.get("/users/me/preferences");
export const putMyPrefs = (data) => API.put("/users/me/preferences", data);
export const deleteMe = () => API.delete("/users/me");

// Stories
export const generateStory = (data, params) =>
  API.post("/stories/generate", data, { params });
export const deleteStory = (id) => API.delete(`/stories/${id}`);
export const postStoryFeedback = (storyId, data) => API.post(`/stories/${storyId}/feedback`, data); // { rating, comment }
export const getMyStories = (params) => API.get("/users/my-stories", { params });
export const getStory = (id) => API.get(`/stories/${id}`);
export const getFeedbackForStory = (id) => API.get(`/stories/${id}/feedback`);
// Presigned URL Download
export const getStoryDownloadUrl = (id) => API.get(`/stories/${id}/download-url`);

// Admin
export const adminUsers = () => API.get("/admin/users");
export const adminStories = (params) => API.get("/admin/stories", { params });
export const adminDeleteUser = (id) => API.delete(`/admin/users/${id}`);

