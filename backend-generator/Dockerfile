FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app


# 1) make pip use CPU torch
ENV PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu

# 2) install system deps
RUN apt-get update && apt-get install -y build-essential git && rm -rf /var/lib/apt/lists/*

# 3) install python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 4) download the model DURING THE BUILD (this is the key part)
RUN mkdir -p /app/models && \
    python - <<'PY'
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
model = "distilgpt2"
cache = "/app/models"
os.makedirs(cache, exist_ok=True)
AutoTokenizer.from_pretrained(model, cache_dir=cache)
AutoModelForCausalLM.from_pretrained(model, cache_dir=cache)
print("✅ downloaded to", cache)
PY

# 5) copy your actual app
COPY . /app

# 6) make transformers look here
ENV HF_HOME=/app/models
ENV TRANSFORMERS_CACHE=/app/models
# 7) bake in env vars
ENV AWS_REGION="ap-southeast-2" \
    STORY_STORAGE="s3"



CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
