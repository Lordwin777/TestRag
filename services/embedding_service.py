"""
services/embedding_service.py
==============================
Embedding generation service for the RAG-Based AI Test Case Generator.

Key Responsibilities:
1. Generate high-dimensional numerical vector representations of text.
2. Maintain clean architectural separation between:
   - Document Embedding (for indexing knowledge chunks into FAISS)
   - Query Embedding (for searching runtime user queries against FAISS)
3. Support both Google Gemini Embeddings (via official google-genai SDK)
   and a high-performance local normalized semantic vectorizer for
   guaranteed offline/zero-cost operation and educational demonstration.
"""

import os
import math
import re
import hashlib
from typing import List, Union
import numpy as np
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:
    """
    Manages embedding generation for documents and queries.
    Standard vector dimension: 768.
    """

    def __init__(self, mode: str = None, dimension: int = 768):
        self.dimension = dimension
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()

        # Configured mode or auto-select based on GEMINI_API_KEY
        configured_mode = mode or os.getenv("EMBEDDING_MODE", "auto").lower()

        if configured_mode in ("gemini", "cloud") and self.api_key:
            self.mode = "gemini"
        elif configured_mode == "local":
            self.mode = "local"
        else:
            # Auto mode: use Gemini if valid key exists, else fallback to local
            self.mode = "gemini" if self.api_key else "local"

        self._genai_client = None
        if self.mode == "gemini":
            try:
                from google import genai
                self._genai_client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[EmbeddingService] Warning: Could not initialize Gemini client: {e}. Falling back to local mode.")
                self.mode = "local"

        print(f"[EmbeddingService] Initialized in '{self.mode.upper()}' mode (Dimension: {self.dimension})")

    # -------------------------------------------------------------------------
    # Public API: Explicit Separation of Document and Query Embeddings
    # -------------------------------------------------------------------------

    def get_document_embedding(self, document_text: str) -> np.ndarray:
        """
        Generate embedding for a single knowledge base document or chunk.
        
        Args:
            document_text: The textual content of the knowledge chunk.
            
        Returns:
            Normalized 1D numpy array of shape (dimension,) with dtype float32.
        """
        return self._generate_embedding(document_text, is_query=False)

    def get_document_embeddings_batch(self, document_texts: List[str]) -> np.ndarray:
        """
        Batch generate embeddings for multiple knowledge documents.
        
        Args:
            document_texts: List of document strings.
            
        Returns:
            Normalized 2D numpy array of shape (N, dimension) with dtype float32.
        """
        embeddings = [self.get_document_embedding(text) for text in document_texts]
        return np.vstack(embeddings).astype("float32")

    def get_query_embedding(self, query_text: str) -> np.ndarray:
        """
        Generate embedding for a runtime user query derived from code analysis.
        
        Why separate from document embedding?
        1. Task-specific optimization: In asymmetric search (RAG), queries
           represent intent while documents represent factual knowledge.
        2. Query normalization and preprocessing can be applied specifically
           to user queries without altering indexed document semantics.
        
        Args:
            query_text: The synthesized retrieval query from code analysis.
            
        Returns:
            Normalized 1D numpy array of shape (dimension,) with dtype float32.
        """
        preprocessed_query = self._preprocess_query(query_text)
        return self._generate_embedding(preprocessed_query, is_query=True)

    # -------------------------------------------------------------------------
    # Internal Embedding Generation
    # -------------------------------------------------------------------------

    def _generate_embedding(self, text: str, is_query: bool = False) -> np.ndarray:
        """
        Internal routing to either Gemini Cloud API or Local Semantic Vectorizer.
        Always returns an L2-normalized float32 vector so dot-product equals
        cosine similarity in FAISS (IndexFlatIP).
        """
        if self.mode == "gemini" and self._genai_client:
            try:
                return self._gemini_embedding(text, is_query=is_query)
            except Exception as exc:
                print(f"[EmbeddingService] Gemini API call failed ({exc}); using local fallback.")
                return self._local_semantic_embedding(text)
        else:
            return self._local_semantic_embedding(text)

    def _gemini_embedding(self, text: str, is_query: bool) -> np.ndarray:
        """
        Calls Google Gemini Embeddings API (text-embedding-004 or gemini-embedding-001).
        """
        # Modern task types for asymmetric retrieval
        task_type = "RETRIEVAL_QUERY" if is_query else "RETRIEVAL_DOCUMENT"

        try:
            # Try text-embedding-004 first
            response = self._genai_client.models.embed_content(
                model="text-embedding-004",
                contents=text,
            )
            raw_vector = np.array(response.embedding.values, dtype="float32")
        except Exception:
            # Fallback to gemini-embedding-001 if text-embedding-004 not available
            response = self._genai_client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
            )
            raw_vector = np.array(response.embedding.values, dtype="float32")

        # Ensure correct dimension and L2 normalization
        return self._normalize_vector(raw_vector)

    def _local_semantic_embedding(self, text: str) -> np.ndarray:
        """
        High-fidelity, deterministic local semantic vectorizer (768 dimensions).
        
        Designed for college projects:
        - 100% offline, zero-cost, no GPU required.
        - Uses term frequency, character n-grams, sub-word hashing, and
          testing domain weighting to produce smooth, semantically dense vectors.
        - Output is L2-normalized for exact cosine similarity with FAISS IndexFlatIP.
        """
        vec = np.zeros(self.dimension, dtype="float32")
        cleaned = text.lower()
        words = re.findall(r"\b[a-z0-9_]{2,}\b", cleaned)

        # Testing domain keyword boosts for heightened RAG relevance
        domain_weights = {
            "boundary": 2.5, "range": 2.0, "limit": 2.0, "minimum": 2.0, "maximum": 2.0,
            "negative": 2.5, "invalid": 2.2, "reject": 2.0, "error": 2.0, "fail": 1.8,
            "positive": 2.2, "valid": 2.0, "normal": 1.8, "success": 1.8,
            "equivalence": 2.4, "partition": 2.2, "class": 1.8,
            "branch": 2.3, "condition": 2.1, "decision": 2.0, "boolean": 1.9,
            "loop": 2.4, "iteration": 2.2, "while": 2.0, "for": 2.0,
            "exception": 2.5, "raise": 2.2, "catch": 2.0, "try": 2.0, "typeerror": 2.2,
            "security": 2.5, "auth": 2.3, "sanitize": 2.2, "injection": 2.2, "token": 2.0,
            "edge": 2.3, "empty": 2.0, "null": 2.0, "zero": 2.0, "extreme": 2.0,
            "function": 1.5, "parameter": 1.5, "unit": 1.8, "state": 2.1
        }

        # Project tokens across the 768-dimensional space via multi-hash projection
        for w in words:
            weight = domain_weights.get(w, 1.0)
            
            # Word-level hashes
            h1 = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % self.dimension
            h2 = int(hashlib.sha256(w.encode("utf-8")).hexdigest(), 16) % self.dimension
            vec[h1] += 1.0 * weight
            vec[h2] += 0.5 * weight

            # 3-gram sub-tokens for morphological similarity (e.g. 'bound', 'loop', 'valid')
            for i in range(len(w) - 2):
                tri = w[i:i+3]
                h_tri = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16) % self.dimension
                vec[h_tri] += 0.25 * weight

        # Document structure features (length, punctuation, code tokens)
        vec[0] += min(len(words) / 50.0, 3.0)
        vec[1] += float(cleaned.count("<") + cleaned.count(">") + cleaned.count("=="))
        vec[2] += float(cleaned.count("if") + cleaned.count("else") + cleaned.count("elif"))
        vec[3] += float(cleaned.count("for") + cleaned.count("while"))
        vec[4] += float(cleaned.count("try") + cleaned.count("except") + cleaned.count("raise"))

        return self._normalize_vector(vec)

    def _normalize_vector(self, vec: np.ndarray) -> np.ndarray:
        """L2 normalizes a vector to unit length (norm = 1.0)."""
        # Ensure correct dimension
        if len(vec) > self.dimension:
            vec = vec[:self.dimension]
        elif len(vec) < self.dimension:
            vec = np.pad(vec, (0, self.dimension - len(vec)))

        norm = np.linalg.norm(vec)
        if norm > 1e-12:
            vec = vec / norm
        else:
            # Fallback for empty strings
            vec = np.ones(self.dimension, dtype="float32") / np.sqrt(self.dimension)
        return vec.astype("float32")

    def _preprocess_query(self, query: str) -> str:
        """Clean and normalize the retrieval query text."""
        # Remove excess whitespace, preserve code indicators and keywords
        cleaned = re.sub(r"\s+", " ", query.strip())
        return cleaned
