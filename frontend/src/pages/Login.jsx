import React from "react";
import { useContext, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card, TextInput, PasswordInput, Button, Stack, Title } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { login, getMe } from "../api/endpoints";
import { AuthContext } from "../AuthContext";

export default function Login() {
  const { setUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!form.username || !form.password) {
      notifications.show({ color: "red", message: "Please fill username and password" });
      return;
    }
    setLoading(true);
    try {
      const res = await login(form);
      localStorage.setItem("token", res.data.access_token);
      if (res.data.cog_access_token) 
        localStorage.setItem("cog_at", res.data.cog_access_token);
      const me = await getMe();
      setUser(me.data);
      notifications.show({ color: "green", message: `Welcome, ${me.data.username}!` });
      navigate("/generate");
    } catch (e) {
      notifications.show({ color: "red", message: "Login failed. Check your credentials." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack align="center" mt="xl">
      <Title order={2}>Login</Title>
      <Card withBorder shadow="sm" p="lg" w={420}>
        <Stack>
          <TextInput
            label="Username"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />
          <PasswordInput
            label="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <Button loading={loading} onClick={handleSubmit}>Login</Button>
          <Button variant="subtle" component={Link} to="/register">New here? Register</Button>
        </Stack>
      </Card>
    </Stack>
  );
}