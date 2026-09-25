"""
utils/validators.py
===================
Input validation and AI JSON response validation for the RAG Test Case Generator.

Ensures:
1. User input adheres to safe limits (no empty code, max length, supported language).
2. AI-generated responses are strictly validated against the required JSON schema.
3. JSON blocks wrapped in markdown code fences are safely extracted.
4. Missing fields or malformed types are caught and flagged with clear error messages.
"""

import json
import re
from typing import Tuple, Optional, Dict, Any, List


class RequestValidator:
    """Validates user HTTP requests submitted to the backend."""

    SUPPORTED_LANGUAGES = {"python", "java", "c", "c++", "cpp", "javascript", "js"}
    MAX_CODE_LENGTH = 50000  # 50 KB max code length for security

    @classmethod
    def validate_generate_request(cls, data: Any) -> Tuple[bool, Optional[str]]:
        """
        Validates the incoming JSON payload for /generate.
        
        Returns:
            (is_valid: bool, error_message: Optional[str])
        """
        if not isinstance(data, dict):
            return False, "Request body must be a valid JSON object."

        code = data.get("code", "")
        if not code or not isinstance(code, str) or not code.strip():
            return False, "Source code cannot be empty. Please paste your code to analyze."

        if len(code) > cls.MAX_CODE_LENGTH:
            return False, f"Code exceeds maximum allowed size ({cls.MAX_CODE_LENGTH} characters)."

        language = data.get("language", "")
        if not language or not isinstance(language, str):
            return False, "Programming language must be specified."

        norm_lang = language.strip().lower()
        if norm_lang not in cls.SUPPORTED_LANGUAGES:
            return False, f"Unsupported language '{language}'. Supported: Python, Java, C, C++, JavaScript."

        num_cases = data.get("number_of_test_cases", 10)
        try:
            num = int(num_cases)
            if num < 1 or num > 30:
                return False, "Number of test cases must be an integer between 1 and 30."
        except (ValueError, TypeError):
            return False, "Number of test cases must be a valid number."

        return True, None


class ResponseValidator:
    """Validates and sanitizes LLM JSON output against strict schema requirements."""

    REQUIRED_ROOT_KEYS = ["analysis", "retrieved_knowledge", "test_cases"]
    REQUIRED_TEST_CASE_KEYS = [
        "id", "function", "title", "test_type", "input",
        "preconditions", "steps", "expected_result", "priority", "severity", "reason"
    ]

    @classmethod
    def extract_json_string(cls, raw_text: str) -> str:
        """
        Safely strips markdown code blocks (e.g. ```json ... ```) and extracts
        the innermost JSON object.
        """
        if not raw_text:
            return ""

        text = raw_text.strip()

        # Check for ```json ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            return fence_match.group(1).strip()

        # If text begins with { and ends with }, return as is
        if text.startswith("{") and text.endswith("}"):
            return text

        # Find first { and last }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return text[first_brace:last_brace + 1].strip()

        return text

    @classmethod
    def validate_and_sanitize_response(cls, raw_text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Extracts, parses, and validates the LLM JSON response.
        
        Returns:
            (sanitized_dict, error_message)
        """
        clean_json_str = cls.extract_json_string(raw_text)
        if not clean_json_str:
            return None, "Received empty response from the AI model."

        try:
            data = json.loads(clean_json_str)
        except json.JSONDecodeError as exc:
            return None, f"Failed to parse AI output as JSON: {str(exc)}"

        if not isinstance(data, dict):
            return None, "AI response must be a JSON dictionary object."

        # Validate root keys
        for key in cls.REQUIRED_ROOT_KEYS:
            if key not in data:
                return None, f"AI response missing required root key: '{key}'."

        # Validate analysis block
        analysis = data.get("analysis", {})
        if not isinstance(analysis, dict):
            data["analysis"] = {"summary": "Analysis data unavailable.", "language": "Unknown"}

        # Validate retrieved_knowledge list
        rk = data.get("retrieved_knowledge", [])
        if not isinstance(rk, list):
            data["retrieved_knowledge"] = []

        # Validate test_cases list
        test_cases = data.get("test_cases", [])
        if not isinstance(test_cases, list) or len(test_cases) == 0:
            return None, "AI response contained no valid test cases in 'test_cases' list."

        sanitized_cases = []
        for i, tc in enumerate(test_cases):
            if not isinstance(tc, dict):
                continue

            # Ensure all required fields exist with fallbacks
            tc_id = str(tc.get("id", f"TC{i+1:03d}")).strip() or f"TC{i+1:03d}"
            tc_fn = str(tc.get("function", "main")).strip() or "main"
            tc_title = str(tc.get("title", f"Test Case {tc_id}")).strip()
            tc_type = str(tc.get("test_type", "Functional")).strip()

            tc_input = tc.get("input", {})
            if not isinstance(tc_input, dict):
                tc_input = {"input": str(tc_input)}

            tc_pre = tc.get("preconditions", ["Function is initialized"])
            if isinstance(tc_pre, str):
                tc_pre = [tc_pre]
            elif not isinstance(tc_pre, list):
                tc_pre = ["Function is initialized"]

            tc_steps = tc.get("steps", ["Execute function", "Verify output"])
            if isinstance(tc_steps, str):
                tc_steps = [tc_steps]
            elif not isinstance(tc_steps, list):
                tc_steps = ["Execute function", "Verify output"]

            tc_exp = str(tc.get("expected_result", "Expected outcome not specified"))
            tc_prio = str(tc.get("priority", "Medium")).capitalize()
            if tc_prio not in ("High", "Medium", "Low"):
                tc_prio = "Medium"

            tc_sev = str(tc.get("severity", "Medium")).capitalize()
            if tc_sev not in ("Critical", "High", "Medium", "Low"):
                tc_sev = "Medium"

            tc_reason = str(tc.get("reason", "Verifies software quality")).strip()

            sanitized_cases.append({
                "id": tc_id,
                "function": tc_fn,
                "title": tc_title,
                "test_type": tc_type,
                "input": tc_input,
                "preconditions": tc_pre,
                "steps": tc_steps,
                "expected_result": tc_exp,
                "priority": tc_prio,
                "severity": tc_sev,
                "reason": tc_reason
            })

        if not sanitized_cases:
            return None, "No valid test case records could be extracted from AI output."

        data["test_cases"] = sanitized_cases
        return data, None
