"""
tests/test_full_pipeline.py
===========================
End-to-End integration test suite for the RAG-Based AI Test Case Generator.
Tests all Flask endpoints, FAISS retrieval, AST analysis, JSON schema validation, and CSV/JSON exports.
"""

import sys
import os
import json

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app

SAMPLE_CODE = """def calculate_discount(price, discount):
    if price < 0:
        return "Invalid price"
    if discount < 0 or discount > 100:
        return "Invalid discount"
    final_price = price - (price * discount / 100)
    return final_price
"""

def run_tests():
    print("=" * 70)
    print("     STARTING FULL PIPELINE INTEGRATION TESTS (PHASE 14)")
    print("=" * 70)

    client = app.test_client()

    # Test 1: GET / (Dashboard HTML)
    print("\n[TEST 1] GET / (Dashboard HTML)")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert b"AI Test Case Generator" in res.data, "Dashboard title missing in HTML"
    print("  [PASS] Dashboard loaded successfully (HTTP 200)")

    # Test 2: GET /api/status (Health & Vector Store check)
    print("\n[TEST 2] GET /api/status (Health & FAISS check)")
    res = client.get("/api/status")
    assert res.status_code == 200
    status = json.loads(res.data)
    assert status.get("faiss_ready") is True, "FAISS vector store reported not ready"
    assert status.get("total_chunks", 0) > 0, "No chunks reported in FAISS store"
    print(f"  [PASS] System status: FAISS Ready ({status['total_chunks']} chunks indexed)")

    # Test 3: POST /generate (Complete RAG Pipeline)
    print("\n[TEST 3] POST /generate (AST -> Retrieval -> Generation)")
    payload = {
        "code": SAMPLE_CODE,
        "language": "Python",
        "test_type": "All",
        "number_of_test_cases": 8
    }
    res = client.post("/generate", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.data}"
    data = json.loads(res.data)
    assert data.get("success") is True, "Response success flag was False"
    
    # Verify AST Analysis
    analysis = data.get("code_analysis", {})
    assert len(analysis.get("functions", [])) == 1, "Expected 1 function in AST analysis"
    assert analysis["functions"][0]["name"] == "calculate_discount"
    assert len(analysis.get("conditions", [])) >= 2, "Expected at least 2 conditions"
    print(f"  [PASS] AST Code Analysis: Found function '{analysis['functions'][0]['name']}' with {len(analysis['conditions'])} conditions")

    # Verify RAG Retrieved Context
    retrieved = data.get("retrieved_context", [])
    assert len(retrieved) > 0, "Expected at least 1 retrieved knowledge chunk"
    topics = [r["topic"] for r in retrieved]
    print(f"  [PASS] RAG Semantic Retrieval: Retrieved {len(retrieved)} knowledge chunks:")
    for r in retrieved:
        print(f"         - [{r['similarity_score']}] {r['topic']}")

    # Verify Generated Test Cases Schema
    ai_result = data.get("data", {})
    test_cases = ai_result.get("test_cases", [])
    assert len(test_cases) > 0, "No test cases returned in generation result"
    print(f"  [PASS] Generated {len(test_cases)} structured test cases. Validating schema:")

    required_keys = ["id", "function", "title", "test_type", "input", "preconditions", "steps", "expected_result", "priority", "severity", "reason"]
    for tc in test_cases:
        for k in required_keys:
            assert k in tc, f"Missing required key '{k}' in test case: {tc}"
    print(f"         - All {len(test_cases)} test cases strictly conform to required schema!")

    # Test 4: POST /export/csv
    print("\n[TEST 4] POST /export/csv")
    res_csv = client.post("/export/csv", data=json.dumps({"test_cases": test_cases}), content_type="application/json")
    assert res_csv.status_code == 200
    assert res_csv.content_type.startswith("text/csv")
    csv_text = res_csv.data.decode("utf-8")
    assert "ID,Function,Title,Test Type" in csv_text
    assert "TC001" in csv_text
    print("  [PASS] CSV Export generated with correct RFC headers and data rows")

    # Test 5: POST /export/json
    print("\n[TEST 5] POST /export/json")
    res_json = client.post("/export/json", data=json.dumps(ai_result), content_type="application/json")
    assert res_json.status_code == 200
    assert res_json.content_type.startswith("application/json")
    exported_data = json.loads(res_json.data)
    assert "test_cases" in exported_data
    print("  [PASS] JSON Export generated and validated")

    # Test 6: Input Error Handling
    print("\n[TEST 6] Input Validation and Error Handling")
    empty_res = client.post("/generate", data=json.dumps({"code": "", "language": "Python"}), content_type="application/json")
    assert empty_res.status_code == 400
    empty_err = json.loads(empty_res.data)
    assert empty_err.get("success") is False
    print(f"  [PASS] Empty code correctly rejected (HTTP 400: '{empty_err.get('error')}')")

    unsupported_lang = client.post("/generate", data=json.dumps({"code": "x = 1", "language": "Brainfuck"}), content_type="application/json")
    assert unsupported_lang.status_code == 400
    print("  [PASS] Unsupported language correctly rejected (HTTP 400)")

    print("\n" + "=" * 70)
    print("  ALL 6 INTEGRATION TEST SUITES PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
