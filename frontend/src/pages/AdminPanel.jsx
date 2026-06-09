import React, { useContext, useEffect, useMemo, useState } from "react";
import { Tabs, Title, Card, Group, Button, Table, Select, NumberInput, TextInput, Text } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { adminUsers, adminDeleteUser, adminStories, deleteStory } from "../api/endpoints";
import { AuthContext } from "../AuthContext";
import StoryModal from "../components/StoryModal";

export default function AdminPanel() {
  const { user } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [stories, setStories] = useState([]);
  const [genre, setGenre] = useState("");
  const [style, setStyle] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [order, setOrder] = useState("desc");
  const [limit, setLimit] = useState(10);
  const [page, setPage] = useState(1);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const offset = useMemo(() => (page - 1) * limit, [page, limit]);

  useEffect(() => {
    if (user?.role === "admin"|| user?.groups?.includes("Admin")) adminUsers().then((r) => setUsers(r.data || [])).catch(() => {});
  }, [user]);

  useEffect(() => {
    if (user?.role !== "admin") return;
    const params = { genre: genre || undefined, style: style || undefined, sort_by: sortBy, order, limit, offset };
    adminStories(params).then((r) => setStories(r.data || [])).catch(() => notifications.show({ color: "red", message: "Failed to load stories" }));
  }, [user, genre, style, sortBy, order, limit, offset]);

  // if (user?.role !== "admin") return <Text>You must be an admin.</Text>;
  if (!(user?.role === "admin" || user?.groups?.includes("Admin")))
    return <Text>You must be an admin.</Text>;

  const removeUser = async (id) => {
    if (!confirm("Delete this user and all their stories?")) return;
    try { await adminDeleteUser(id); notifications.show({ color: "green", message: "User deleted" }); setUsers((u) => u.filter((x) => x.id !== id)); } catch { notifications.show({ color: "red", message: "Delete failed" }); }
  };

  const removeStory = async (id) => {
    try { await deleteStory(id); notifications.show({ color: "green", message: "Story deleted" }); setStories((s) => s.filter((x) => x.id !== id)); } catch { notifications.show({ color: "red", message: "Delete failed" }); }
  };

  return (
    <>
      <Title order={2}>Admin Panel</Title>
      <Tabs defaultValue="users" mt="md">
        <Tabs.List>
          <Tabs.Tab value="users">Users</Tabs.Tab>
          <Tabs.Tab value="stories">Stories</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="users" pt="md">
          <Card withBorder shadow="sm" p="lg">
            <Table striped withTableBorder withColumnBorders>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>ID</Table.Th>
                  <Table.Th>Username</Table.Th>
                  <Table.Th>Email</Table.Th>
                  <Table.Th>Role</Table.Th>
                  <Table.Th>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {users.map((u) => (
                  <Table.Tr key={u.id}>
                    <Table.Td>{u.id}</Table.Td>
                    <Table.Td>{u.username}</Table.Td>
                    <Table.Td>{u.email || "—"}</Table.Td>
                    <Table.Td>{u.role}</Table.Td>
                    <Table.Td>
                      {u.role !== "admin" && (
                        <Button size="xs" color="red" variant="light" onClick={() => removeUser(u.id)}>
                          Delete
                        </Button>
                      )}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="stories" pt="md">
          <Card withBorder shadow="sm" p="lg">
            <Group grow>
              <TextInput label="Genre" value={genre} onChange={(e) => setGenre(e.target.value)} />
              <TextInput label="Style" value={style} onChange={(e) => setStyle(e.target.value)} />
              <Select label="Sort by" value={sortBy} onChange={setSortBy} data={[{ value: "created_at", label: "Created" }, { value: "title", label: "Title" }]} />
              <Select label="Order" value={order} onChange={setOrder} data={[{ value: "asc", label: "Asc" }, { value: "desc", label: "Desc" }]} />
              <NumberInput label="Page size" min={1} max={50} value={limit} onChange={(v) => setLimit(Number(v) || 10)} />
              <NumberInput label="Page" min={1} value={page} onChange={(v) => setPage(Number(v) || 1)} />
            </Group>
          </Card>

          <Card withBorder shadow="sm" p="lg" mt="md">
            {stories.length ? (
              <Table striped withTableBorder withColumnBorders>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>ID</Table.Th>
                    <Table.Th>Title</Table.Th>
                    <Table.Th>Genre</Table.Th>
                    <Table.Th>Created</Table.Th>
                    <Table.Th>Actions</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {stories.map((s) => (
                    <Table.Tr key={s.id}>
                      <Table.Td>{s.id}</Table.Td>
                      <Table.Td>{s.title}</Table.Td>
                      <Table.Td>{s.genre || "—"}</Table.Td>
                      <Table.Td>{new Date(s.created_at).toLocaleString()}</Table.Td>
                      <Table.Td>
                        <Table.Td>
                        <Group gap="xs">
                          <Button size="xs" variant="light" onClick={() => { setSelectedId(s.id); setViewerOpen(true); }}>
                            View
                          </Button>
                          <Button size="xs" color="red" variant="light" onClick={() => removeStory(s.id)}>
                            Delete
                          </Button>
                        </Group>
+                      </Table.Td>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            ) : (
              <Text c="dimmed">No stories found.</Text>
            )}

            <Group justify="space-between" mt="md">
              <Button variant="light" disabled={page === 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Prev</Button>
              <Text>Page {page}</Text>
              <Button variant="light" disabled={stories.length < limit} onClick={() => setPage((p) => p + 1)}>Next</Button>
            </Group>
          </Card>

          <StoryModal opened={viewerOpen} onClose={() => setViewerOpen(false)} storyId={selectedId} />
        </Tabs.Panel>
      </Tabs>
    </>
  );
}