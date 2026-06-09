import os

STORY_DIR = os.getenv("STORY_DIR", os.path.abspath("./data/stories"))
# os.makedirs(STORY_DIR, exist_ok=True)

def save_story(filename: str, content: str):
    path = os.path.join(STORY_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def load_story(filename: str) -> str:
    path = os.path.join(STORY_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def delete_story(filename: str):
    path = os.path.join(STORY_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
