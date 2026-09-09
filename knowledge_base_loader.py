"""
knowledge_base_loader.py
Loads maritime service PDFs, chunks them, and retrieves relevant chunks
using BM25-style scoring (TF × IDF with saturation and length normalisation).
"""

import os
import re
import math
from pathlib import Path
from collections import Counter


# ── Loading ───────────────────────────────────────────────────────────────────

def load_knowledge_base(folder: str = "knowledge_base") -> list[dict]:
    """
    Read all PDFs (and .txt fallbacks) from folder.
    Returns a list of chunk dicts: {name, text, source, chunk_id}
    """
    docs = []
    folder_path = Path(folder)

    if not folder_path.exists():
        return docs

    for filepath in sorted(folder_path.iterdir()):
        if filepath.suffix.lower() == ".pdf":
            text = _extract_pdf(filepath)
        elif filepath.suffix.lower() == ".txt":
            text = filepath.read_text(encoding="utf-8", errors="ignore")
        else:
            continue

        if not text.strip():
            continue

        chunks = _chunk_text(text, chunk_size=500, overlap=80)
        for i, chunk in enumerate(chunks):
            docs.append({
                "name": filepath.stem,
                "source": str(filepath),
                "chunk_id": f"{filepath.stem}_{i}",
                "text": chunk,
            })

    return docs


def _extract_pdf(filepath: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        pass
    try:
        import PyPDF2
        parts = []
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                parts.append(page.extract_text() or "")
        return "\n".join(parts)
    except ImportError:
        print(f"[WARNING] No PDF library. Install pdfplumber or PyPDF2.")
        return ""
    except Exception as e:
        print(f"[WARNING] Could not read {filepath}: {e}")
        return ""


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    words = text.split()
    chunks, step = [], chunk_size - overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i: i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


# ── BM25 search ───────────────────────────────────────────────────────────────

_K1 = 1.5   # term frequency saturation
_B  = 0.75  # length normalisation strength


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s؀-ۿ]", " ", text)
    return [t for t in text.split() if len(t) > 1]


def _build_idf(docs: list[dict]) -> dict[str, float]:
    """Compute IDF for every term across the corpus."""
    N = len(docs)
    df: dict[str, int] = {}
    for doc in docs:
        for term in set(_tokenize(doc["text"])):
            df[term] = df.get(term, 0) + 1
    return {term: math.log((N - n + 0.5) / (n + 0.5) + 1)
            for term, n in df.items()}


def _bm25_score(
    query_terms: list[str],
    doc_tokens: list[str],
    idf: dict[str, float],
    avg_dl: float,
) -> float:
    tf = Counter(doc_tokens)
    dl = len(doc_tokens)
    score = 0.0
    for term in query_terms:
        if term not in idf:
            continue
        f = tf.get(term, 0)
        score += idf[term] * (f * (_K1 + 1)) / (
            f + _K1 * (1 - _B + _B * dl / max(avg_dl, 1))
        )
    return score


# Cache of the corpus-level BM25 stats, keyed by chunk count and the first and last
# chunk id, so it rebuilds only when the knowledge base actually changes.
_INDEX_CACHE: dict = {}


def _get_index(docs: list[dict]) -> dict:
    """Build (or reuse) the BM25 index: IDF, per-doc tokens, and average length.

    The IDF table and tokenization depend only on the corpus, not the query, so
    computing them once and reusing them turns every search from O(corpus) work
    into a cheap scoring pass.
    """
    # Key on corpus content, not on id(docs). CPython reuses freed addresses, so an
    # address-based key can serve a stale index for a different corpus.
    cache_key = (len(docs), docs[0]["chunk_id"], docs[-1]["chunk_id"])
    cached = _INDEX_CACHE.get("entry")
    if cached and cached["key"] == cache_key:
        return cached

    tokenized = [_tokenize(d["text"]) for d in docs]
    avg_dl = sum(len(t) for t in tokenized) / max(len(tokenized), 1)
    entry = {
        "key":       cache_key,
        "idf":       _build_idf(docs),
        "tokenized": tokenized,
        "avg_dl":    avg_dl,
    }
    _INDEX_CACHE["entry"] = entry
    return entry


def search_knowledge_base(docs: list[dict], query: str, top_k: int = 4) -> list[dict]:
    """BM25 retrieval — returns top_k most relevant chunks."""
    if not docs:
        return []

    query_terms = _tokenize(query)
    if not query_terms:
        return docs[:top_k]

    index = _get_index(docs)
    idf, tokenized, avg_dl = index["idf"], index["tokenized"], index["avg_dl"]

    scored = []
    for doc, tokens in zip(docs, tokenized):
        score = _bm25_score(query_terms, tokens, idf, avg_dl)
        # Boost chunks whose header area (first 200 chars) contains query terms
        header = doc["text"][:200].lower()
        if any(t in header for t in query_terms):
            score *= 1.3
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [d for s, d in scored[:top_k] if s > 0]
    return results or docs[:top_k]
