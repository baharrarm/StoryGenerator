# import os, uuid
# from .paths import STORY_DIR, ensure_dirs

# def write_story_text(text: str) -> str:
#     ensure_dirs()
#     story_id = str(uuid.uuid4())
#     path = os.path.join(STORY_DIR, f"{story_id}.txt")
#     with open(path, "w", encoding="utf-8") as f:
#         print("Writing story to:", path)
#         f.write(text)
#     return path, story_id

# def read_story_text(path: str) -> str:
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             return f.read()
#     except FileNotFoundError:
#         return "" 

# def delete_story_file(path: str) -> None:
#     try:
#         if path and os.path.isfile(path):
#             os.remove(path)
#     except Exception:
#         # swallow file errors. DB delete still proceeds
#         pass

import uuid
from app.storage import save_story, load_story, delete_story

def write_story_text(user_id: int, text: str):
    story_id = str(uuid.uuid4())
    key = f"stories/{user_id}/{story_id}.txt"          
    save_story(key, text)                # goes to S3 or local based on env
    return key, story_id

def read_story_text(key: str) -> str:
    return load_story(key)

def delete_story_file(key: str) -> None:
    try:
        delete_story(key)
    except Exception:
        pass
