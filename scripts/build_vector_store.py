"""
scripts/build_vector_store.py
=============================
Builds the FAISS vector database from knowledge documents in knowledge_base/.

Workflow:
1. Scans knowledge_base/ for all .txt files.
2. Extracts document content, topics, and metadata.
3. Splits into semantic chunks (both full topic overviews and focused sections).
4. Generates high-dimensional vector embeddings using EmbeddingService.
5. Populates a FAISS IndexFlatIP (Cosine Similarity) index.
6. Serializes the index to vector_store/index.faiss.
7. Saves metadata mappings to vector_store/metadata.json.

Run directly via:
    python scripts/build_vector_store.py
"""

import os
import sys
import json
import re
from typing import List, Dict, Any
import numpy as np
import faiss

# Ensure root directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.embedding_service import EmbeddingService

KNOWLEDGE_BASE_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")
VECTOR_STORE_DIR = os.path.join(PROJECT_ROOT, "vector_store")
INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "index.faiss")
METADATA_PATH = os.path.join(VECTOR_STORE_DIR, "metadata.json")


def parse_topic_name(file_name: str, content: str) -> str:
    """Extract topic name from file header or file name."""
    match = re.search(r"^Concept Name:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    base = os.path.splitext(file_name)[0]
    return base.replace("_", " ").title()


def chunk_document(file_name: str, content: str) -> List[Dict[str, Any]]:
    """
    Chunks a testing knowledge document into semantic units.
    Creates:
    1. Primary Full Document chunk (for comprehensive knowledge retrieval).
    2. Focused Sub-chunks if sections are distinctly partitioned.
    """
    topic = parse_topic_name(file_name, content)
    chunks = []

    # Clean lines
    clean_content = content.strip()

    # Create summary (first 2-3 sentences or definition block)
    summary_match = re.search(r"Definition:\s*\n(.*?)(?=\n\n|\n[A-Z]|\Z)", clean_content, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else clean_content[:200] + "..."

    # Extract tags from topic and content
    words = re.findall(r"\b[a-zA-Z]{3,}\b", topic.lower())
    tags = list(set(words))

    # Chunk 1: Comprehensive Topic Chunk
    chunks.append({
        "file_name": file_name,
        "topic": topic,
        "chunk_type": "full_overview",
        "content": clean_content,
        "summary": summary,
        "tags": tags
    })

    # Sub-chunk: Rules & Guidance (Very useful for prompt augmentation)
    guidance_match = re.search(r"(Guidance for Generating Test Cases:.*)", clean_content, re.DOTALL)
    if guidance_match:
        chunks.append({
            "file_name": file_name,
            "topic": f"{topic} (Generation Rules)",
            "chunk_type": "guidance",
            "content": f"Topic: {topic}\n\n{guidance_match.group(1).strip()}",
            "summary": f"Key rules and actionable heuristics for {topic} test case generation.",
            "tags": tags + ["rules", "heuristics", "guidance"]
        })

    return chunks


def build_vector_store():
    """Build and save the FAISS vector database and metadata."""
    print("=" * 70)
    print("      BUILDING FAISS VECTOR STORE FOR TESTING KNOWLEDGE BASE")
    print("=" * 70)

    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        raise FileNotFoundError(f"Knowledge base directory not found at: {KNOWLEDGE_BASE_DIR}")

    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

    txt_files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith(".txt")]
    if not txt_files:
        raise ValueError(f"No .txt knowledge documents found in: {KNOWLEDGE_BASE_DIR}")

    print(f"[*] Found {len(txt_files)} knowledge documents in knowledge_base/")

    # 1. Parse and chunk all documents
    all_chunks: List[Dict[str, Any]] = []
    for file_name in sorted(txt_files):
        file_path = os.path.join(KNOWLEDGE_BASE_DIR, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_chunks = chunk_document(file_name, content)
        for chunk in file_chunks:
            chunk["id"] = len(all_chunks)
            all_chunks.append(chunk)

    print(f"[*] Generated {len(all_chunks)} semantic chunks for indexing")

    # 2. Initialize Embedding Service
    embedder = EmbeddingService()
    print(f"[*] Generating vector embeddings (Mode: {embedder.mode.upper()}, Dim: {embedder.dimension})...")

    # 3. Generate embeddings for all document chunks
    chunk_texts = [chunk["content"] for chunk in all_chunks]
    embeddings_matrix = embedder.get_document_embeddings_batch(chunk_texts)

    num_vectors, dim = embeddings_matrix.shape
    print(f"[*] Embeddings matrix shape: {num_vectors} vectors x {dim} dimensions")

    # 4. Construct FAISS IndexFlatIP (Cosine similarity via inner product on normalized vectors)
    print("[*] Creating FAISS IndexFlatIP (Inner Product / Cosine Similarity)...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings_matrix)

    # 5. Persist FAISS index to disk
    faiss.write_index(index, INDEX_PATH)
    print(f"[+] FAISS index written to: {INDEX_PATH}")

    # 6. Persist metadata to disk
    metadata_payload = {
        "total_chunks": len(all_chunks),
        "dimension": dim,
        "embedding_mode": embedder.mode,
        "chunks": all_chunks
    }
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2, ensure_ascii=False)
    print(f"[+] Metadata written to: {METADATA_PATH}")

    print("=" * 70)
    print("SUCCESS: Vector database built successfully!")
    print(f"Total documents indexed: {len(txt_files)}")
    print(f"Total chunks indexed:    {len(all_chunks)}")
    print(f"FAISS index file:        {INDEX_PATH}")
    print(f"Metadata file:           {METADATA_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    build_vector_store()
