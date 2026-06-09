import React from "react";
import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import { AuthProvider } from "./AuthContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import GenerateStory from "./pages/GenerateStory";
import MyStories from "./pages/MyStories";
import Profile from "./pages/Profile";
import AdminPanel from "./pages/AdminPanel";
import { RequireAuth, RequireAdmin } from "./components/Reroutes";


export default function App() {
  return (
    <MantineProvider>
      <Notifications />
      <AuthProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<GenerateStory />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/generate" element={<GenerateStory />} />
              <Route path="/mystories" element={<RequireAuth><MyStories /></RequireAuth>} />
              <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
              <Route path="/admin" element={<RequireAdmin><AdminPanel /></RequireAdmin>} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </AuthProvider>
    </MantineProvider>
  );
}
