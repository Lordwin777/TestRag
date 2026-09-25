"""
services/rag_service.py
=======================
Retrieval-Augmented Generation (RAG) Service.

Key Responsibilities:
1. Load the pre-indexed FAISS vector database (index.faiss) and metadata (metadata.json).
2. Accept a synthesized retrieval query from the code analyzer.
3. Transform the query into a high-dimensional vector via EmbeddingService.get_query_embedding.
4. Execute vector similarity search on the FAISS index to find Top-K relevant knowledge chunks.
5. Compute and calibrate cosine similarity scores (0.0 to 1.0).
6. Format retrieved knowledge chunks into structured transparency payloads for the UI
   and clear prompt context for the LLM.
"""

import os
import sys
import json
from typing import List, Dict, Any, Tuple
import numpy as np
import faiss

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.embedding_service import EmbeddingService

INDEX_PATH = os.path.join(PROJECT_ROOT, "vector_store", "index.faiss")
METADATA_PATH = os.path.join(PROJECT_ROOT, "vector_store", "metadata.json")


class RAGService:
    """Manages vector search and knowledge retrieval over testing documents."""

    def __init__(self, index_path: str = INDEX_PATH, metadata_path: str = METADATA_PATH):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = None
        self.chunks: List[Dict[str, Any]] = []
        self.embedding_service = EmbeddingService()
        self._load_vector_store()

    def _load_vector_store(self):
        """Loads FAISS index and metadata from disk."""
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(
                f"FAISS index file not found at '{self.index_path}'. "
                "Please run 'python scripts/build_vector_store.py' first."
            )
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(
                f"Metadata file not found at '{self.metadata_path}'. "
                "Please run 'python scripts/build_vector_store.py' first."
            )

        # Load FAISS index
        self.index = faiss.read_index(self.index_path)

        # Load metadata JSON
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.chunks = self.metadata.get("chunks", [])
        print(f"[RAGService] Successfully loaded FAISS index ({self.index.ntotal} vectors) and {len(self.chunks)} chunk metadata.")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Execute vector similarity search for a query and return Top-K knowledge chunks.
        
        Args:
            query: The retrieval query string.
            top_k: Number of most relevant chunks to return (default: 5).
            
        Returns:
            List of dictionaries containing:
                - topic: Name of the testing concept
                - file_name: Source file in knowledge_base/
                - similarity_score: Calibrated float between 0.0 and 1.0
                - summary: Brief conceptual overview
                - content: Full retrieved testing knowledge
                - tags: Associated metadata tags
        """
        if not self.index or self.index.ntotal == 0:
            raise RuntimeError("FAISS index is empty or uninitialized.")

        # 1. Generate query embedding using the dedicated Query Embedding pipeline
        query_vec = self.embedding_service.get_query_embedding(query)
        query_batch = np.expand_dims(query_vec, axis=0).astype("float32")

        # 2. Search FAISS index (IndexFlatIP returns inner products = cosine similarity)
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_batch, k)

        retrieved_results: List[Dict[str, Any]] = []
        seen_topics = set()

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue

            chunk = self.chunks[idx]
            base_topic = chunk.get("topic", "Software Testing")

            # Avoid exact duplicate full topics if sub-chunk already provided
            topic_key = base_topic.split(" (")[0]
            if topic_key in seen_topics and len(retrieved_results) >= 3:
                continue
            seen_topics.add(topic_key)

            # Normalize raw cosine similarity to 0.0 - 1.0 range
            # Inner product of unit vectors is in [-1.0, 1.0]
            raw_score = float(score)
            calibrated_score = round(max(0.0, min(1.0, (raw_score + 1.0) / 2.0)), 4)
            # If the raw score is already in [0, 1] range (positive dot product)
            if raw_score >= 0.0:
                calibrated_score = round(min(1.0, raw_score), 4)

            retrieved_results.append({
                "chunk_id": chunk.get("id", idx),
                "topic": base_topic,
                "file_name": chunk.get("file_name", ""),
                "similarity_score": calibrated_score,
                "summary": chunk.get("summary", ""),
                "content": chunk.get("content", ""),
                "tags": chunk.get("tags", [])
            })

            if len(retrieved_results) >= top_k:
                break

        return retrieved_results

    def format_context_for_llm(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Constructs the augmented knowledge text block to inject into the LLM prompt.
        """
        if not retrieved_chunks:
            return "No external testing knowledge retrieved."

        sections = []
        for i, item in enumerate(retrieved_chunks, 1):
            sections.append(
                f"--- KNOWLEDGE ITEM {i}: {item['topic']} (Relevance Score: {item['similarity_score']}) ---\n"
                f"{item['content']}\n"
            )
        return "\n".join(sections)
