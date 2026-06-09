import React, { useContext, useEffect, useMemo, useState } from "react";
import { Title, Card, Group, Button, Table, Select, NumberInput, TextInput, Loader, Text } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { getMyStories, deleteStory } from "../api/endpoints";
import { AuthContext } from "../AuthContext";
import StoryModal from "../components/StoryModal";

export default function MyStories() {
  const { user } = useContext(AuthContext);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [genre, setGenre] = useState("");
  const [style, setStyle] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [order, setOrder] = useState("desc");
  const [limit, setLimit] = useState(10);
  const [page, setPage] = useState(1);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [selectedId, setSelectedId] = useState(null);

  const offset = useMemo(() => (page - 1) * limit, [page, limit]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = {
        genre: genre || undefined,
        style: style || undefined,
        sort_by: sortBy,
        order,
        limit,
        offset,
      };
      const res = await getMyStories(params);
      setItems(res.data || []);
    } catch (e) {
      notifications.show({ color: "red", message: "Failed to load stories" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) fetchData();
  }, [user, genre, style, sortBy, order, limit, offset]);

  const handleDelete = async (id) => {
    try {
      await deleteStory(id);
      notifications.show({ color: "green", message: "Deleted" });
      fetchData();
    } catch (e) {
      notifications.show({ color: "red", message: "Delete failed" });
    }
  };

  return (
    <>
      <Title order={2}>My Stories</Title>

      <Card withBorder shadow="sm" p="lg" mt="md">
        <Group grow>
          <TextInput label="Genre" placeholder="e.g., romance" value={genre} onChange={(e) => setGenre(e.target.value)} />
          <TextInput label="Style" placeholder="e.g., casual" value={style} onChange={(e) => setStyle(e.target.value)} />
          <Select label="Sort by" value={sortBy} onChange={setSortBy} data={[{ value: "created_at", label: "Created" }, { value: "title", label: "Title" }]} />
          <Select label="Order" value={order} onChange={setOrder} data={[{ value: "asc", label: "Asc" }, { value: "desc", label: "Desc" }]} />
          <NumberInput label="Page size" min={1} max={50} value={limit} onChange={(v) => setLimit(Number(v) || 10)} />
          <NumberInput label="Page" min={1} value={page} onChange={(v) => setPage(Number(v) || 1)} />
        </Group>
      </Card>

      <Card withBorder shadow="sm" p="lg" mt="md">
        {loading ? (
          <Group justify="center"><Loader /></Group>
        ) : (
          items.length ? (
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
                {items.map((s) => (
                  <Table.Tr key={s.id}>
                    <Table.Td>{s.id}</Table.Td>
                    <Table.Td>{s.title}</Table.Td>
                    <Table.Td>{s.genre || "—"}</Table.Td>
                    <Table.Td>{new Date(s.created_at).toLocaleString()}</Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <Button
                          variant="light"
                          size="xs"
                          onClick={() => { setSelectedId(s.id); setViewerOpen(true); }}
                        >
                          View
                        </Button>
                        <Button color="red" variant="light" size="xs" onClick={() => handleDelete(s.id)}>Delete</Button>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          ) : (
            <Text c="dimmed">No stories found.</Text>
          )
        )}

        <Group justify="space-between" mt="md">
          <Button variant="light" disabled={page === 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Prev</Button>
          <Text>Page {page}</Text>
          <Button variant="light" disabled={items.length < limit} onClick={() => setPage((p) => p + 1)}>Next</Button>
        </Group>
      </Card>
      <StoryModal
        opened={viewerOpen}
        onClose={() => setViewerOpen(false)}
        storyId={selectedId}
      />
    </>
  );
}
