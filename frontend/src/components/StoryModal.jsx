import React, { useEffect, useState } from "react";
import { Modal, Stack, Group, Badge, Text, Textarea, Button, Loader, Center, Rating } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { getStory, getFeedbackForStory, getStoryDownloadUrl } from "../api/endpoints";

export default function StoryModal({ opened, onClose, storyId }) {
  const [loading, setLoading] = useState(false);
  const [detail, setDetail] = useState(null);     // { id, title, genre, created_at, content }
  const [feedbacks, setFeedbacks] = useState([]); // [{ id, rating, notes, created_at, story_id }]

  useEffect(() => {
    if (!opened || !storyId) return;
    setLoading(true);
    Promise.all([getStory(storyId), getFeedbackForStory(storyId)])
      .then(([storyRes, fbRes]) => {
        setDetail(storyRes.data);
        const list = Array.isArray(fbRes.data) ? fbRes.data : (fbRes.data?.items ?? []);
        console.debug("feedback api payload:", fbRes.data);
        setFeedbacks(list);
      })
      .catch(() => {
        notifications.show({ color: "red", message: "Could not load story" });
        onClose?.();
      })
      .finally(() => setLoading(false));
  }, [opened, storyId, onClose]);

  const content =
    detail?.content ?? detail?.story ?? detail?.text ?? detail?.body ?? "";

  return (
    <Modal opened={opened} onClose={onClose} title={detail?.title || "Story"} size="lg" centered>
      {loading ? (
        <Center my="lg"><Loader /></Center>
      ) : detail ? (
        <Stack>
          <Group gap="xs" wrap="wrap">
            {detail?.genre ? <Badge>{detail.genre}</Badge> : null}
            {detail?.id ? <Badge variant="light">ID: {detail.id}</Badge> : null}
            {detail?.created_at && (
              <Text size="sm" c="dimmed">
                {new Date(detail.created_at).toLocaleString()}
              </Text>
            )}
          </Group>

          <Textarea value={content} readOnly autosize minRows={12} />

          <Group justify="end">
            <Button
              variant="light"
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(content);
                  notifications.show({ color: "green", message: "Copied" });
                } catch { /* ignore */ }
              }}
            >
              Copy
            </Button>
            {detail?.id && (
              <Button
                variant="light"
                onClick={async () => {
                  try {
                    const { data } = await getStoryDownloadUrl(detail.id);
                    window.open(data.url, "_blank");
                  } catch {
                    notifications.show({ color: "red", message: "Download link failed" });
                  }
                }}
              >
                Download (.txt)
              </Button>
            )}
          </Group>

          <Stack gap="xs" mt="sm">
            <Text fw={600}>My feedback</Text>
            {feedbacks.length === 0 ? (
              <Text c="dimmed" size="sm">You haven’t left feedback for this story yet.</Text>
            ) : (
              feedbacks.map((f) => (
                <Stack
                  key={f.id}
                  gap={2}
                  style={{ borderTop: "1px solid var(--mantine-color-default-border)", paddingTop: 8 }}
                >
                  <Group gap="xs" justify="space-between" wrap="wrap">
                    <Rating value={Number(f.rating) || 0} readOnly />
                    <Text size="xs" c="dimmed">
                      {f.created_at ? new Date(f.created_at).toLocaleString() : "—"}
                    </Text>
                  </Group>
                  <Text size="sm">{f.notes || "—"}</Text>
                </Stack>
              ))
            )}
          </Stack>
        </Stack>
      ) : (
        <Text c="dimmed">No content.</Text>
      )}
    </Modal>
  );
}
