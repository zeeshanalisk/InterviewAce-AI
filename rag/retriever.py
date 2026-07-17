"""
InterviewAce AI — RAG Retrieval Module
=======================================
Simple TF-IDF-based retrieval from local knowledge base text files.
No external vector database required — runs entirely locally.
"""

import os
import glob
import logging
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Path to the knowledge base directory
KB_DIR = Path(__file__).parent.parent / "knowledge_base"

# Maximum number of context chunks to retrieve
DEFAULT_TOP_K = 3

# Maximum characters per retrieved chunk
MAX_CHUNK_CHARS = 1200


# ─────────────────────────────────────────────────────────────────────────────
#  Knowledge Base Loader
# ─────────────────────────────────────────────────────────────────────────────

def load_knowledge_base() -> dict[str, str]:
    """
    Load all .txt files from the knowledge base directory.

    Returns:
        Dict mapping filename (without extension) → full text content.
    """
    kb = {}
    txt_files = sorted(glob.glob(str(KB_DIR / "*.txt")))

    if not txt_files:
        logger.warning("No knowledge base files found in %s", KB_DIR)
        return kb

    for filepath in txt_files:
        key = Path(filepath).stem
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                kb[key] = f.read()
            logger.debug("Loaded knowledge file: %s (%d chars)", key, len(kb[key]))
        except OSError as e:
            logger.error("Could not read %s: %s", filepath, e)

    logger.info("Knowledge base loaded: %d files", len(kb))
    return kb


def chunk_text(text: str, chunk_size: int = MAX_CHUNK_CHARS) -> list[str]:
    """
    Split text into overlapping chunks of approximately chunk_size characters.
    Splits on paragraph boundaries where possible.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) > chunk_size and current:
            chunks.append("\n\n".join(current))
            # Keep last paragraph for overlap
            current = [current[-1], para] if current else [para]
            current_len = sum(len(p) for p in current)
        else:
            current.append(para)
            current_len += len(para)

    if current:
        chunks.append("\n\n".join(current))

    return chunks


# ─────────────────────────────────────────────────────────────────────────────
#  TF-IDF Retriever
# ─────────────────────────────────────────────────────────────────────────────

class KnowledgeRetriever:
    """
    TF-IDF based retriever over the local knowledge base.
    Builds an index on first use and caches it in memory.
    """

    def __init__(self):
        self._chunks: list[str] = []
        self._chunk_sources: list[str] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None
        self._built = False

    def build_index(self):
        """Load knowledge base files and build TF-IDF index."""
        kb = load_knowledge_base()

        if not kb:
            logger.warning("Empty knowledge base — retriever will return empty context.")
            self._built = True
            return

        for source, text in kb.items():
            for chunk in chunk_text(text):
                self._chunks.append(chunk)
                self._chunk_sources.append(source)

        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
        )
        self._matrix = self._vectorizer.fit_transform(self._chunks)
        self._built = True
        logger.info(
            "RAG index built: %d chunks from %d files",
            len(self._chunks), len(kb)
        )

    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        filter_source: Optional[str] = None,
    ) -> str:
        """
        Retrieve the most relevant context chunks for a query.

        Args:
            query:         The search query (job role, skills, question type, etc.)
            top_k:         Number of top chunks to return.
            filter_source: If set, restrict retrieval to a specific KB file by stem name.

        Returns:
            Concatenated relevant context as a single string.
        """
        if not self._built:
            self.build_index()

        if not self._chunks or self._vectorizer is None:
            return "No knowledge base context available."

        try:
            query_vec = self._vectorizer.transform([query])
            scores = cosine_similarity(query_vec, self._matrix).flatten()

            # Apply source filter
            if filter_source:
                mask = np.array([
                    1.0 if filter_source.lower() in src.lower() else 0.0
                    for src in self._chunk_sources
                ])
                scores = scores * mask

            top_indices = scores.argsort()[::-1][:top_k]

            # Only include chunks with meaningful relevance
            relevant = [
                self._chunks[i]
                for i in top_indices
                if scores[i] > 0.01
            ]

            if not relevant:
                # Fallback: return the first chunk from the most relevant file
                best_idx = scores.argsort()[::-1][0]
                relevant = [self._chunks[best_idx]]

            return "\n\n---\n\n".join(relevant)

        except Exception as e:
            logger.error("Retrieval error: %s", e, exc_info=True)
            return "Context retrieval unavailable."

    def get_source_names(self) -> list[str]:
        """Return list of unique source file names in the knowledge base."""
        return sorted(set(self._chunk_sources))


# ─────────────────────────────────────────────────────────────────────────────
#  Singleton instance (shared across the app)
# ─────────────────────────────────────────────────────────────────────────────

_retriever_instance: Optional[KnowledgeRetriever] = None


def get_retriever() -> KnowledgeRetriever:
    """Return the singleton KnowledgeRetriever, building the index if needed."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeRetriever()
        _retriever_instance.build_index()
    return _retriever_instance


# ─────────────────────────────────────────────────────────────────────────────
#  High-level helper: role-aware retrieval
# ─────────────────────────────────────────────────────────────────────────────

_ROLE_TO_SOURCE: dict[str, str] = {
    "data scientist":        "data_science",
    "machine learning":      "data_science",
    "ml engineer":           "data_science",
    "ai engineer":           "data_science",
    "data analyst":          "data_science",
    "software engineer":     "software_engineering",
    "software developer":    "software_engineering",
    "backend developer":     "software_engineering",
    "frontend developer":    "software_engineering",
    "full stack":             "software_engineering",
    "devops":                "software_engineering",
    "product manager":       "product_management",
    "program manager":       "product_management",
    "business analyst":      "product_management",
}


def retrieve_for_role(
    job_role: str,
    query: str,
    extra_sources: Optional[list[str]] = None,
    top_k: int = DEFAULT_TOP_K,
) -> str:
    """
    Retrieve context relevant to a specific job role and query.
    Always includes behavioral/HR context and optionally role-specific context.

    Args:
        job_role:       The target job role string.
        query:          The full search query (role + skills + feature type).
        extra_sources:  Additional source file stems to include.
        top_k:          Number of chunks to retrieve per source.

    Returns:
        Combined context string.
    """
    retriever = get_retriever()

    # Determine role-specific source
    role_lower = job_role.lower()
    role_source = next(
        (src for key, src in _ROLE_TO_SOURCE.items() if key in role_lower),
        None
    )

    context_parts = []

    # Role-specific context
    if role_source:
        role_ctx = retriever.retrieve(query, top_k=top_k, filter_source=role_source)
        if role_ctx:
            context_parts.append(f"[{role_source.replace('_', ' ').title()} Knowledge]\n{role_ctx}")

    # Behavioral context (always include for interview prep)
    beh_ctx = retriever.retrieve(query, top_k=2, filter_source="behavioral_hr")
    if beh_ctx:
        context_parts.append(f"[Behavioral & HR Knowledge]\n{beh_ctx}")

    # Extra sources
    for source in (extra_sources or []):
        extra_ctx = retriever.retrieve(query, top_k=2, filter_source=source)
        if extra_ctx:
            context_parts.append(f"[{source.replace('_', ' ').title()} Knowledge]\n{extra_ctx}")

    # Fallback: general retrieval
    if not context_parts:
        context_parts.append(retriever.retrieve(query, top_k=top_k))

    return "\n\n=====\n\n".join(context_parts)
