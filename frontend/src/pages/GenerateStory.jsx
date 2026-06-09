import React, { useContext, useState } from "react";
import { Card, TextInput, Select, NumberInput, Button, Stack, Title, Textarea, Group, Badge, Switch } from "@mantine/core";
import { Rating } from "@mantine/core"
import { notifications } from "@mantine/notifications";
import { generateStory, postStoryFeedback } from "../api/endpoints";
import { AuthContext } from "../AuthContext";

export default function GenerateStory() {
  const { user } = useContext(AuthContext);
  const [form, setForm] = useState({ prompt: "", genre: "", style: "", length: 200 });
  const [useRandom, setUseRandom] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // { story, saved, story_id }
  const [rating, setRating] = useState(0);
  const [notes, setNotes] = useState("");
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  const handleGenerate = async () => {
    if (!form.prompt || form.prompt.trim().length < 3) {
      notifications.show({ color: "red", message: "Prompt must be at least 3 characters" });
      return;
    }
    setLoading(true);
    try {
      const payload = {
        prompt: form.prompt,
        genre: form.genre || null,
        style: form.style || null,
        length: form.length,
      };
      const res = await generateStory(payload, { use_random_character: useRandom || undefined });
      setResult(res.data);
      if (res.data.saved) notifications.show({ color: "green", message: "Story generated & saved" });
      else notifications.show({ color: "blue", message: "Story generated (not saved)" });
    } catch (e) {
      notifications.show({ color: "red", message: "Generation failed" });
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!result?.story) return;
    try { await navigator.clipboard.writeText(result.story); notifications.show({ color: "green", message: "Copied" }); } catch {}
  };

  return (
    <Stack>
      <Title order={2}>Generate a Story</Title>
      <Card withBorder shadow="sm" p="lg">
        <Stack>
          <TextInput
            label="Prompt"
            placeholder="e.g., A detective in a foggy city..."
            value={form.prompt}
            onChange={(e) => setForm({ ...form, prompt: e.target.value })}
          />
          <Group grow>
            <Select
              label="Genre (optional)"
              data={["romance", "adventure", "mystery", "fantasy", "sci-fi"].map((v) => ({ value: v, label: v }))}
              value={form.genre || null}
              onChange={(v) => setForm({ ...form, genre: v || "" })}
              clearable
            />
            <Select
              label="Style (optional)"
              data={["formal", "casual", "humorous", "dramatic"].map((v) => ({ value: v, label: v }))}
              value={form.style || null}
              onChange={(v) => setForm({ ...form, style: v || "" })}
              clearable
            />
            <NumberInput
              label="Length"
              min={50}
              max={1200}
              value={form.length}
              onChange={(v) => setForm({ ...form, length: Number(v) || 200 })}
            />
          </Group>

          <Switch
            label="Use random character"
            checked={useRandom}
            onChange={(e) => setUseRandom(e.currentTarget.checked)} 
          />

          <Group justify="space-between">
            <Button loading={loading} onClick={handleGenerate}>Generate</Button>
            <Group gap="sm">
              <Badge color={user ? "green" : "gray"}>{user ? "Logged in: will save" : "Guest: not saved"}</Badge>
              {result?.story && <Button variant="light" onClick={copy}>Copy story</Button>}
            </Group>
          </Group>
        </Stack>
      </Card>

      {result?.story && (
        <Card withBorder shadow="sm" p="lg">
          <Stack>
            <Group gap="sm">
              {result.saved ? <Badge color="green">Saved</Badge> : <Badge>Not saved</Badge>}
              {result.story_id && <Badge variant="light">ID: {result.story_id}</Badge>}
            </Group>
            <Textarea label="Output" value={result.story} autosize minRows={12} readOnly />
          </Stack>
        </Card>
      )}

      {user && result?.saved && result?.story_id && (
        <Card withBorder shadow="sm" p="lg" mt="md">
          <Stack>
            <Group justify="space-between" align="center">
              <Title order={4} style={{ margin: 0 }}>My feedback</Title>
              <Rating value={rating} onChange={setRating} />
            </Group>

            <Textarea
              placeholder="Your notes (optional)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              minRows={3}
            />

            <Group justify="flex-end">
              <Button
                loading={submittingFeedback}
                disabled={!rating}
                onClick={async () => {
                  try {
                    setSubmittingFeedback(true);
                    await postStoryFeedback(result.story_id, { rating, notes }); 
                    setRating(0);
                    setNotes("");
                    notifications.show({ color: "green", message: "Feedback submitted" });
                  } catch {
                    notifications.show({ color: "red", message: "Could not submit feedback" });
                  } finally {
                    setSubmittingFeedback(false);
                  }
                }}
              >
                Submit feedback
              </Button>
            </Group>
          </Stack>
        </Card>
      )}

    </Stack>
  );
}
