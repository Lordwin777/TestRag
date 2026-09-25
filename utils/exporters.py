"""
utils/exporters.py
==================
Handles CSV and JSON exports for generated test cases.

Supports:
1. Exporting formatted CSV with all mandatory test specification columns.
2. Exporting complete validated JSON payload.
3. Safe disk persistence to the exports/ directory.
"""

import os
import csv
import json
import io
from typing import Dict, Any, List


class TestExporter:
    """Provides CSV and JSON serialization for generated test cases."""

    CSV_HEADERS = [
        "ID",
        "Function",
        "Title",
        "Test Type",
        "Input",
        "Preconditions",
        "Steps",
        "Expected Result",
        "Priority",
        "Severity",
        "Reason"
    ]

    @classmethod
    def generate_csv_string(cls, test_cases: List[Dict[str, Any]]) -> str:
        """
        Converts a list of test case dictionaries into standard RFC 4180 CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Write header
        writer.writerow(cls.CSV_HEADERS)

        # Write data rows
        for tc in test_cases:
            # Format inputs nicely
            inputs_str = json.dumps(tc.get("input", {}))
            
            # Format preconditions as newline-separated list
            preconditions = tc.get("preconditions", [])
            pre_str = " | ".join(preconditions) if isinstance(preconditions, list) else str(preconditions)

            # Format steps as numbered sequence
            steps = tc.get("steps", [])
            if isinstance(steps, list):
                steps_str = " -> ".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
            else:
                steps_str = str(steps)

            writer.writerow([
                tc.get("id", ""),
                tc.get("function", ""),
                tc.get("title", ""),
                tc.get("test_type", ""),
                inputs_str,
                pre_str,
                steps_str,
                tc.get("expected_result", ""),
                tc.get("priority", ""),
                tc.get("severity", ""),
                tc.get("reason", "")
            ])

        return output.getvalue()

    @classmethod
    def generate_json_string(cls, data: Dict[str, Any]) -> str:
        """Serializes full test generation report to formatted JSON string."""
        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def save_to_disk(cls, content: str, filename: str, export_dir: str = "exports") -> str:
        """Persists exported file to the exports/ directory."""
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path
