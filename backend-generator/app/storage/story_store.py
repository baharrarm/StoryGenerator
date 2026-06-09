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
