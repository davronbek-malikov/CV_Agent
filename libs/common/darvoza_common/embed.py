"""Text embeddings.

Default is a hashing embedder: free, offline, deterministic. It matches shared
words and character trigrams, so it is not cross-lingual. A real multilingual
embedding model can replace `embed()` later without changing callers.
"""

import hashlib
import math
import re

DIM = 256


def _tokens(text: str) -> list[str]:
    words = re.findall(r"\w+", text.lower())
    grams = [w[i : i + 3] for w in words if len(w) > 3 for i in range(len(w) - 2)]
    return words + grams


def embed(text: str) -> list[float]:
    vec = [0.0] * DIM
    for tok in _tokens(text):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % DIM] += 1.0 if (h >> 8) & 1 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=False))


def to_pgvector(vec: list[float]) -> str:
    return "[" + ",".join(f"{v:.5f}" for v in vec) + "]"
