import React, { useContext } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { Center, Loader } from "@mantine/core";
import { AuthContext } from "../AuthContext";

export function RequireAuth({ children }) {
  const { user, loading } = useContext(AuthContext);
  const location = useLocation();
  if (loading) return <Center h={200}><Loader /></Center>;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  return children;
}

export function RequireAdmin({ children }) {
  const { user, loading } = useContext(AuthContext);
  const location = useLocation();
  if (loading) return <Center h={200}><Loader /></Center>;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  // if (user.role !== "admin") return <Navigate to="/" replace />;
  if (!(user.role === "admin" || user?.groups?.includes("Admin")))
    return <Navigate to="/" replace />;
  return children;
}
