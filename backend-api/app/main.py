from fastapi import FastAPI
from app.middleware.cors import add_cors
# from app.db import Base, engine
from app.db import engine
from app.models.base import Base
from app.routes import auth_routes, story_routes, admin_routes, user_routes
from starlette.staticfiles import StaticFiles


app = FastAPI(title="LLM Story API")
add_cors(app)

# @app.on_event("startup")
# def on_startup():
#     Base.metadata.create_all(bind=engine)

# Routers (your routers already carry /v1 prefixes)
app.include_router(auth_routes.router)
app.include_router(story_routes.router)
app.include_router(admin_routes.router)
app.include_router(user_routes.router)

# app.mount("/", StaticFiles(directory="app/static", html=True), name="spa")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/db")
def health_db():
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return {"db": "ok"}
    except Exception as e:
        return {"db": "down", "error": str(e)}



