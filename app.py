"""
app.py
======
Flask Web Application for the RAG-Based AI Test Case Generator.

Endpoints:
- GET  /            : Renders the web dashboard
- GET  /api/status  : System health check (FAISS index status, Gemini API key presence)
- POST /generate    : Full RAG pipeline execution (AST Analysis -> Semantic Search -> Gemini LLM)
- POST /export/csv  : Generates and streams downloadable test_cases.csv
- POST /export/json : Generates and streams downloadable test_cases.json
"""

import os
import sys
import json
import traceback
from flask import Flask, render_template, request, jsonify, Response, send_file
from dotenv import load_dotenv

load_dotenv()

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.code_analyzer import CodeAnalyzer
from services.rag_service import RAGService
from services.ai_service import AIService
from utils.validators import RequestValidator
from utils.exporters import TestExporter

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "rag-testgen-secret-2026")

# Lazy-loaded singleton services
_rag_service = None
_ai_service = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        try:
            _rag_service = RAGService()
        except Exception as e:
            print(f"[app] Error loading RAGService: {e}")
            raise RuntimeError(
                f"FAISS vector store is not available. Error: {str(e)}. "
                "Please run 'python scripts/build_vector_store.py' to initialize the knowledge base index."
            )
    return _rag_service


def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """Renders the main test case generation dashboard."""
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def api_status():
    """Returns runtime health status for RAG vector store and Gemini configuration."""
    status = {
        "status": "healthy",
        "faiss_ready": False,
        "total_chunks": 0,
        "gemini_api_key_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "embedding_mode": os.getenv("EMBEDDING_MODE", "auto"),
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    }
    try:
        rag = get_rag_service()
        status["faiss_ready"] = True
        status["total_chunks"] = len(rag.chunks)
    except Exception as e:
        status["faiss_error"] = str(e)

    return jsonify(status)


@app.route("/generate", methods=["POST"])
def generate():
    """
    Main RAG Test Generation Endpoint.
    Executes:
    1. Input Validation
    2. Code Preprocessing & AST Structural Analysis
    3. Retrieval Query Synthesis
    4. FAISS Vector Database Semantic Search (Top-K)
    5. Context Augmentation & Prompt Engineering
    6. LLM Inference (Google Gemini)
    7. Response Sanitization & JSON Schema Validation
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "error": "Invalid request: JSON body required."}), 400

        # 1. Validate incoming request
        is_valid, err_msg = RequestValidator.validate_generate_request(data)
        if not is_valid:
            return jsonify({"success": False, "error": err_msg}), 400

        code = data["code"]
        language = data.get("language", "Python")
        test_type = data.get("test_type", "All")
        num_cases = int(data.get("number_of_test_cases", 10))

        # 2. Code Analysis (AST / Language Parsing)
        analysis = CodeAnalyzer.analyze(code, language)

        # 3. RAG Retrieval Query Synthesis
        retrieval_query = CodeAnalyzer.create_retrieval_query(analysis, test_type)

        # 4. FAISS Semantic Search
        top_k = int(os.getenv("TOP_K", 5))
        rag = get_rag_service()
        retrieved_chunks = rag.retrieve(query=retrieval_query, top_k=top_k)

        # 5. Gemini AI Generation & Context Augmentation
        ai_service = get_ai_service()
        generation_result = ai_service.generate_test_cases(
            code=code,
            language=language,
            analysis=analysis,
            retrieved_knowledge=retrieved_chunks,
            test_type=test_type,
            num_test_cases=num_cases
        )

        return jsonify({
            "success": True,
            "query": retrieval_query,
            "code_analysis": analysis,
            "retrieved_context": retrieved_chunks,
            "data": generation_result
        })

    except Exception as exc:
        print(f"[app] /generate error: {exc}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"An error occurred while generating test cases: {str(exc)}"
        }), 500


@app.route("/export/csv", methods=["POST"])
def export_csv():
    """Generates and downloads a CSV export of test cases."""
    try:
        data = request.get_json(silent=True) or {}
        test_cases = data.get("test_cases", [])
        if not test_cases and "data" in data:
            test_cases = data["data"].get("test_cases", [])

        if not test_cases:
            return jsonify({"success": False, "error": "No test cases provided for export."}), 400

        csv_content = TestExporter.generate_csv_string(test_cases)

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=generated_test_cases.csv",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/export/json", methods=["POST"])
def export_json():
    """Generates and downloads a JSON export of the complete generation report."""
    try:
        data = request.get_json(silent=True) or {}
        if not data:
            return jsonify({"success": False, "error": "No data provided for export."}), 400

        json_content = TestExporter.generate_json_string(data)

        return Response(
            json_content,
            mimetype="application/json",
            headers={
                "Content-Disposition": "attachment; filename=generated_test_cases.json",
                "Content-Type": "application/json; charset=utf-8"
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1")
    print(f"[*] Starting RAG-Based AI Test Case Generator on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
