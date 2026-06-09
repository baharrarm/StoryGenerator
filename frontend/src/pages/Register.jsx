import React from "react";
import { useContext, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card, TextInput, PasswordInput, Button, Stack, Title, Text } from "@mantine/core";
import { notifications } from "@mantine/notifications";
// import { register as registerApi, login as loginApi, getMe } from "../api/endpoints";
import { register as registerApi, confirmSignup, login as loginApi, getMe } from "../api/endpoints";
import { AuthContext } from "../AuthContext";

export default function Register() {
  const { setUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);


  const passChecks = (s) => ({
   len: s.length >= 8,
   up: /[A-Z]/.test(s),
   low: /[a-z]/.test(s),
   num: /\d/.test(s),
   sym: /[^A-Za-z0-9]/.test(s),
 });
 const pc = passChecks(form.password);
 const passOK = Object.values(pc).every(Boolean);


  const handleSubmit = async () => {
    if (!form.username || !form.email || !form.password) {
      notifications.show({ color: "red", message: "Please fill username, email and password" });
      return;
    }
    if (!passOK) {
      notifications.show({ color: "red", message: "Password must meet policy (see below)." });
      return;
    }
    setLoading(true);
    try {
      // await registerApi(form);
      // const res = await loginApi(form); // auto-login after register

      await registerApi(form); // Cognito sign-up
      const code = window.prompt("Enter the confirmation code sent to your email:");
      if (!code) throw new Error("No confirmation code");
      await confirmSignup({ username: form.username, code });
      const res = await loginApi(form); // login
      localStorage.setItem("token", res.data.access_token);
      if (res.data.cog_access_token) 
        localStorage.setItem("cog_at", res.data.cog_access_token);
      const me = await getMe();
      setUser(me.data);
      notifications.show({ color: "green", message: "Registration confirmed!" });
      navigate("/");
    } catch (e) {
      // notifications.show({ color: "red", message: "Registration failed (username may be taken)." });
      notifications.show({ color: "red", message: "Sign-up/confirm failed. Check username/email/code." });

    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack align="center" mt="xl">
      <Title order={2}>Register</Title>
      <Card withBorder shadow="sm" p="lg" w={420}>
        <Stack>
          <TextInput
            label="Username"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />
          <TextInput
            label="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <PasswordInput
            label="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <Stack gap={2}>
            <Text size="xs" c={pc.len ? "teal" : "red"}>• At least 8 characters</Text>
            <Text size="xs" c={pc.up  ? "teal" : "red"}>• At least 1 uppercase letter</Text>
            <Text size="xs" c={pc.low ? "teal" : "red"}>• At least 1 lowercase letter</Text>
            <Text size="xs" c={pc.num ? "teal" : "red"}>• At least 1 number</Text>
            <Text size="xs" c={pc.sym ? "teal" : "red"}>• At least 1 symbol</Text>
          </Stack>
          <Button loading={loading} disabled={!passOK} onClick={handleSubmit}>Create account</Button>
          <Button variant="subtle" component={Link} to="/login">Already have an account? Login</Button>
        </Stack>
      </Card>
    </Stack>
  );
}