import os
from fastapi.middleware.cors import CORSMiddleware

def _parse_origins(val: str | None) -> list[str]:
    # Accept comma/space/newline-separated OR "*" for any origin
    if not val or not val.strip():
        return ["http://localhost:5173", "http://127.0.0.1:5173"]
    if val.strip() == "*":
        return ["*"]
    parts = (val.replace("\n", ",").replace(" ", ",")).split(",")
    return [p.strip().rstrip("/") for p in parts if p.strip()]

def add_cors(app):
    origins = _parse_origins(os.getenv("CORS_ORIGINS"))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,                         # set CORS_ORIGINS in prod
        allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
        allow_headers=["*"],                           # includes Authorization
        expose_headers=["ETag"],
        allow_credentials=False,                       # using Bearer tokens
        max_age=3600,
    )
