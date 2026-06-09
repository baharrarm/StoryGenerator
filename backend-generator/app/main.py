from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.story_generator import generate_story
from app.storage.story_store import write_story_text
from app.sqs_worker import start_worker_thread
from app.db import engine
from app.models.base import Base


app = FastAPI(title="Story Generator Service")

@app.on_event("startup")
def _start_workers():
    start_worker_thread()


class GenerateIn(BaseModel):
    prompt: str
    genre: str | None = None
    style: str | None = None
    length: int = 200
    user_id: int | None = None
    use_random_character: bool = False
    temperature: float | None = None
    top_p: float | None = None

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/health/db")
def health_db():
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return {"db": "ok"}
    except Exception as e:
        return {"db": "down", "error": str(e)}
        

@app.post("/v1/generate")
def generate(body: GenerateIn):
    # 1) run model
    text = generate_story(
        body.prompt,
        body.genre,
        body.style,
        body.length,
        temperature=body.temperature or 0.9,
        top_p=body.top_p or 0.92,
    )

    # 2) optionally save to storage (S3/local)
    story_id = None
    key = None
    if body.user_id is not None:
        key, story_id = write_story_text(body.user_id, text)

    return {
        "story": text,
        "saved": body.user_id is not None,
        "storage_key": key,
        "story_id": story_id,
    }
