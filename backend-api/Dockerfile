FROM python:3.12-slim

WORKDIR /app

ENV STORY_DIR="./data/stories" \
    EXTERNAL_CHARACTER_API_URL="https://randomuser.me/api/?nat=au,us,gb" \
    STORY_STORAGE="s3" \
    AWS_REGION="ap-southeast-2"


# system deps (psycopg2 needs these)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY backend-api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend-api ./backend-api
WORKDIR /app/backend-api

ENV PYTHONPATH=/app/backend-api

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
