from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

_MODEL_NAME = "distilgpt2"
_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")

_tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME, cache_dir=_CACHE_DIR, local_files_only=True)
_model = AutoModelForCausalLM.from_pretrained(_MODEL_NAME, cache_dir=_CACHE_DIR, local_files_only=True)
_model.eval()

# Make sure pad_token exists
if _tokenizer.pad_token is None:
    _tokenizer.pad_token = _tokenizer.eos_token

def generate_story(prompt: str, genre: str | None, style: str | None, length: int, *, temperature: float = 0.9, top_p: float = 0.92) -> str:
    """
    Generate a short story using GPT-2 (distilgpt2).
    - prompt: user-provided starting idea
    - genre, style: optional steering signals
    - length: target length (tokens), capped 50–1200
    """

    # Build an instruction-style seed instead of repeating "Genre: X"
    parts = ["Write a short"]
    if genre:
        parts.append(genre)
    parts.append("story")
    if style:
        parts.append(f"in a {style} style")
    instr = " ".join(parts) + "."
    seed = f"{instr}\nPrompt: {prompt}\n\nStory:\n"

    inputs = _tokenizer.encode(seed, return_tensors="pt")
    max_new = max(200, min(1200, length))
    min_len = min(100, max_new - 10)

    with torch.no_grad():
        output = _model.generate(
            inputs,
            max_new_tokens=max_new,
            min_length=min_len,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            top_k=50,
            repetition_penalty=1.15,
            no_repeat_ngram_size=3,
            pad_token_id=_tokenizer.eos_token_id,
            eos_token_id=_tokenizer.eos_token_id,
        )

    text = _tokenizer.decode(output[0], skip_special_tokens=True)
    continuation = text[len(seed):].strip()
    return continuation if continuation else text.strip()
