import React, { useContext, useEffect, useState } from "react";
import { Title, Card, Stack, TextInput, PasswordInput, Button, Group, NumberInput, Text } from "@mantine/core";
import { notifications } from "@mantine/notifications";
// import { getMe, updateMe, getMyPrefs, putMyPrefs, deleteMe } from "../api/endpoints";
import { getMe, getMyPrefs, putMyPrefs, deleteMe, changeEmail, confirmEmail, changePassword } from "../api/endpoints";
import { AuthContext } from "../AuthContext";

export default function Profile() {
  const { user, setUser } = useContext(AuthContext);
  const [uname, setUname] = useState("");
  const [oldPw, setOldPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [newPw2, setNewPw2] = useState("");
  const [emailNew, setEmailNew] = useState("");
  const [emailCode, setEmailCode] = useState("");
  const [prefs, setPrefs] = useState({ default_genre: "", default_style: "", default_length: 200 });

  useEffect(() => {
    getMe().then((r) => setUname(r.data.username)).catch(() => {});
    getMyPrefs().then((r) => r?.data && setPrefs({
      default_genre: r.data.default_genre || "",
      default_style: r.data.default_style || "",
      default_length: r.data.default_length ?? 200,
    })).catch(() => {});
  }, []);

  const saveProfile = async () => {
    // try {
    //   const body = { username: uname || undefined, password: pw || undefined };
    //   const r = await updateMe(body);
    //   setUser(r.data);
    //   setPw("");
    //   notifications.show({ color: "green", message: "Profile updated" });
    // } catch {
    //   notifications.show({ color: "red", message: "Update failed" });
    // }
    notifications.show({ color: "blue", message: "Username is immutable in Cognito. Email can be changed below." });
  };

  const savePrefs = async () => {
    try {
      const body = {
        default_genre: prefs.default_genre || null,
        default_style: prefs.default_style || null,
        default_length: prefs.default_length || 200,
      };
      await putMyPrefs(body);
      notifications.show({ color: "green", message: "Preferences saved" });
    } catch {
      notifications.show({ color: "red", message: "Could not save preferences" });
    }
  };

  const dangerDelete = async () => {
    if (!confirm("Delete your account? This removes your stories permanently.")) return;
    try { await deleteMe(); localStorage.removeItem("token"); setUser(null); window.location.href = "/"; } catch {}
  };

  return (
    <Stack>
      <Title order={2}>Profile</Title>
      <Group align="start" grow>
        <Card withBorder shadow="sm" p="lg">
          <Stack>
            {/* <TextInput label="Username" value={uname} onChange={(e) => setUname(e.target.value)} />
            <PasswordInput label="New password" value={pw} onChange={(e) => setPw(e.target.value)} />
            <Button onClick={saveProfile}>Save profile</Button> */}
            <TextInput label="Username (immutable)" value={uname} readOnly />
            <TextInput label="Current email" value={user?.email || ""} readOnly />
            <TextInput label="New email" value={emailNew} onChange={(e) => setEmailNew(e.target.value)} />
            <Group>
              <Button
                variant="light"
                onClick={async () => {
                  // Email change is Cognito-only; not available in local mode
                  // const at = localStorage.getItem("cog_at");
                  // if (!at) return notifications.show({ color: "red", message: "Please re-login first." });
                  // try {
                  //   await changeEmail({ access_token: at, new_email: emailNew });
                  //   notifications.show({ color: "green", message: "Code sent to new email." });
                  // } catch {
                  //   notifications.show({ color: "red", message: "Could not start email change." });
                  // }
                  notifications.show({ color: "blue", message: "Email change is only available in Cognito mode." });
                }}
              >
                Send code
              </Button>
              <TextInput
                placeholder="Confirmation code"
                value={emailCode}
                onChange={(e) => setEmailCode(e.target.value)}
              />
              <Button
                onClick={async () => {
                  // Email confirmation is Cognito-only; not available in local mode
                  // const at = localStorage.getItem("cog_at");
                  // if (!at) return notifications.show({ color: "red", message: "Please re-login first." });
                  // try {
                  //   await confirmEmail({ access_token: at, code: emailCode });
                  //   notifications.show({ color: "green", message: "Email verified. Re-login to refresh." });
                  // } catch {
                  //   notifications.show({ color: "red", message: "Verification failed." });
                  // }
                  notifications.show({ color: "blue", message: "Email change is only available in Cognito mode." });
                }}
              >
                Confirm email
              </Button>
            </Group>
            <PasswordInput label="Current password" value={oldPw} onChange={(e)=>setOldPw(e.target.value)} />
            <PasswordInput label="New password" value={newPw} onChange={(e)=>setNewPw(e.target.value)} />
            <PasswordInput label="Confirm new password" value={newPw2} onChange={(e)=>setNewPw2(e.target.value)} />
            <Button
              variant="light"
              onClick={async () => {
                // const at = localStorage.getItem("cog_at");          // Cognito access token
                // if (!at) return notifications.show({ color: "red", message: "Please re-login first." });
                // local mode: bearer token sent via Authorization header; no cog_at needed
                if (!newPw || newPw !== newPw2) return notifications.show({ color: "red", message: "Passwords don’t match." });
                try {
                  // await changePassword({ access_token: at, old_password: oldPw, new_password: newPw });
                  await changePassword({ old_password: oldPw, new_password: newPw });
                  setOldPw(""); setNewPw(""); setNewPw2("");
                  notifications.show({ color: "green", message: "Password changed." });
                } catch {
                  notifications.show({ color: "red", message: "Password change failed." });
                }
              }}
            >
              Change password
            </Button>
          </Stack>
        </Card>

        <Card withBorder shadow="sm" p="lg">
          <Stack>
            <Text fw={600}>Default Preferences</Text>
            <TextInput label="Default genre" value={prefs.default_genre} onChange={(e) => setPrefs({ ...prefs, default_genre: e.target.value })} />
            <TextInput label="Default style" value={prefs.default_style} onChange={(e) => setPrefs({ ...prefs, default_style: e.target.value })} />
            <NumberInput label="Default length" min={50} max={1200} value={prefs.default_length} onChange={(v) => setPrefs({ ...prefs, default_length: Number(v) || 200 })} />
            <Button variant="light" onClick={savePrefs}>Save preferences</Button>
          </Stack>
        </Card>
      </Group>

      <Card withBorder shadow="sm" p="lg">
        <Button color="red" variant="light" onClick={dangerDelete}>Delete my account</Button>
      </Card>
    </Stack>
  );
}
