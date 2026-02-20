# src/classification/role_matcher.py
from __future__ import annotations

import os
from typing import List

import numpy as np
from openai import OpenAI

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

_client = OpenAI()

def get_embedding(text: str) -> np.ndarray:
    """
    Получить embedding для строки текста.
    Возвращает np.ndarray(dtype=float32).
    """
    text = (text or "").strip()
    if not text:
        return np.zeros(1536, dtype="float32")

    resp = _client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    emb: List[float] = resp.data[0].embedding
    return np.array(emb, dtype="float32")


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Косинусное сходство двух векторов.
    Если один из векторов нулевой — возвращаем 0.0.
    """
    a = np.array(a, dtype="float32")
    b = np.array(b, dtype="float32")

    if a.ndim != 1 or b.ndim != 1:
        a = a.ravel()
        b = b.ravel()

    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0

    return float(np.dot(a, b) / (na * nb))
