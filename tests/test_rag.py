import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.code_analyzer import CodeAnalyzer
from services.rag_service import RAGService

SAMPLE_CODE = """def calculate_discount(price, discount):
    if price < 0:
        return "Invalid price"
    if discount < 0 or discount > 100:
        return "Invalid discount"
    final_price = price - (price * discount / 100)
    return final_price
"""

def test_rag():
    print("1. Analyzing Code...")
    analysis = CodeAnalyzer.analyze(SAMPLE_CODE, "Python")
    query = CodeAnalyzer.create_retrieval_query(analysis, "All")
    print("Retrieval Query:\n", query)

    print("\n2. Initializing RAG Service...")
    rag = RAGService()
    results = rag.retrieve(query, top_k=5)

    print(f"\n3. Retrieved {len(results)} items from FAISS:")
    for r in results:
        print(f" - [{r['similarity_score']}] {r['topic']} (File: {r['file_name']})")
        print(f"   Summary: {r['summary'][:90]}...")

if __name__ == "__main__":
    test_rag()
