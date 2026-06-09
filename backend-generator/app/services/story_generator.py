import os
from transformers import AutoModelForCausalLM, AutoTokenizer

_MODEL_NAME = "distilgpt2"
_CACHE_DIR = os.getenv("HF_HOME", "/app/models")

_tokenizer = AutoTokenizer.from_pretrained(
    _MODEL_NAME, cache_dir=_CACHE_DIR, local_files_only=True
)
_model = AutoModelForCausalLM.from_pretrained(
    _MODEL_NAME, cache_dir=_CACHE_DIR, local_files_only=True
)

def generate_story(prompt, genre, style, length, *, temperature=0.9, top_p=0.92):
    parts = ["Write a short"]
    if genre:
        parts.append(genre)
    parts.append("story")
    if style:
        parts.append(f"in a {style} style")
    instr = " ".join(parts) + "."
    seed = f"{instr}\nPrompt: {prompt}\n\nStory:\n"

    import torch
    inputs = _tokenizer.encode(seed, return_tensors="pt")
    max_new = max(200, min(1200, length))
    min_len = min(100, max_new - 10)

    with torch.no_grad():
        out = _model.generate(
            inputs,
            max_new_tokens=max_new,
            min_length=min_len,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            pad_token_id=_tokenizer.eos_token_id,
            eos_token_id=_tokenizer.eos_token_id,
        )
    text = _tokenizer.decode(out[0], skip_special_tokens=True)
    return text[len(seed):].strip() or text.strip()
