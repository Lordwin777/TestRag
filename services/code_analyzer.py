"""
services/code_analyzer.py
=========================
Performs deep structural and semantic analysis of user-provided source code.

Features:
1. Python AST (Abstract Syntax Tree) parsing:
   - Identifies functions, methods, parameters, return expressions.
   - Extracts exact condition logic (ast.unparse on If nodes).
   - Identifies loops (For, While), exception handling (Try, Except, Raise).
   - Flags boundary comparisons, security markers, and guard clauses.
2. Lightweight parser for Java, C, C++, and JavaScript.
3. Query Synthesis: Converts the code analysis into a focused, domain-rich
   retrieval query for RAG semantic search.
"""

import ast
import re
from typing import Dict, Any, List


class CodeAnalyzer:
    """Analyzes source code across supported languages and builds RAG queries."""

    SUPPORTED_LANGUAGES = ["Python", "Java", "C", "C++", "JavaScript"]

    @classmethod
    def analyze(cls, code: str, language: str = "Python") -> Dict[str, Any]:
        """
        Main entry point for analyzing source code.
        
        Args:
            code: Source code string.
            language: Selected language (Python, Java, C, C++, JavaScript).
            
        Returns:
            Dictionary with structured analysis metadata.
        """
        normalized_lang = cls._normalize_language(language)

        if normalized_lang == "Python":
            try:
                return cls._analyze_python(code)
            except SyntaxError as e:
                # If AST parsing fails due to syntax error or snippet fragment,
                # fall back gracefully to pattern-based analyzer
                fallback = cls._analyze_pattern_based(code, "Python")
                fallback["syntax_warning"] = f"AST syntax warning: {str(e)}. Used fallback pattern analyzer."
                return fallback
        else:
            return cls._analyze_pattern_based(code, normalized_lang)

    @classmethod
    def create_retrieval_query(cls, analysis: Dict[str, Any], test_type: str = "All") -> str:
        """
        Synthesizes a high-signal search query from the code analysis.
        
        Section 13 requirement:
        Instead of blindly embedding the raw source code, produce a query
        describing the logical nature, inputs, boundaries, and testing needs.
        """
        lang = analysis.get("language", "Generic")
        functions = analysis.get("functions", [])
        conditions = analysis.get("conditions", [])
        loops = analysis.get("loops", [])
        exceptions = analysis.get("exceptions", [])
        security_flags = analysis.get("security_indicators", [])
        comparisons = analysis.get("boundary_comparisons", [])

        query_tokens = [f"{lang} source code testing"]

        # Function signatures
        if functions:
            fn_names = [f["name"] for f in functions]
            query_tokens.append(f"functions: {', '.join(fn_names)}")
            all_params = []
            for f in functions:
                all_params.extend(f.get("parameters", []))
            if all_params:
                query_tokens.append(f"parameters: {', '.join(all_params)}")

        # Conditional logic & boundaries
        if conditions:
            query_tokens.append(f"conditional logic with {len(conditions)} branches")
            for cond in conditions[:4]:
                query_tokens.append(f"branch: {cond}")

        if comparisons:
            query_tokens.append("boundary value analysis numeric range checking inequality limits")
            query_tokens.append("equivalence partitioning valid and invalid input classes")

        # Loops
        if loops:
            query_tokens.append(f"loop testing iteration {len(loops)} loops zero and multiple iterations")

        # Exceptions
        if exceptions:
            query_tokens.append("exception testing error handling raise catch unhandled inputs")

        # Security
        if security_flags:
            query_tokens.append(f"defensive security testing input validation: {', '.join(security_flags)}")

        # Targeted test type
        if test_type and test_type.lower() != "all":
            query_tokens.append(f"specific focus: {test_type} testing")

        # General quality keywords
        query_tokens.append("positive testing happy path negative testing error cases functional verification")

        return " | ".join(query_tokens)

    # -------------------------------------------------------------------------
    # Python AST Analyzer
    # -------------------------------------------------------------------------

    @classmethod
    def _analyze_python(cls, code: str) -> Dict[str, Any]:
        """Deep AST analysis for Python source code."""
        tree = ast.parse(code)

        functions = []
        conditions = []
        loops = []
        exceptions = []
        boundary_comparisons = []
        security_indicators = []
        external_calls = []

        class ASTVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                params = [arg.arg for arg in node.args.args]
                return_types = []
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Return) and subnode.value is not None:
                        try:
                            return_types.append(ast.unparse(subnode.value))
                        except Exception:
                            return_types.append("value")

                docstring = ast.get_docstring(node) or ""
                functions.append({
                    "name": node.name,
                    "parameters": params,
                    "docstring": docstring[:100],
                    "returns": return_types[:3]
                })
                self.generic_visit(node)

            def visit_If(self, node):
                try:
                    cond_str = ast.unparse(node.test)
                except Exception:
                    cond_str = "condition"
                conditions.append(cond_str)
                self.generic_visit(node)

            def visit_Compare(self, node):
                try:
                    comp_str = ast.unparse(node)
                    boundary_comparisons.append(comp_str)
                except Exception:
                    pass
                self.generic_visit(node)

            def visit_For(self, node):
                try:
                    target = ast.unparse(node.target)
                    iter_source = ast.unparse(node.iter)
                    loops.append(f"for {target} in {iter_source}")
                except Exception:
                    loops.append("for loop")
                self.generic_visit(node)

            def visit_While(self, node):
                try:
                    cond = ast.unparse(node.test)
                    loops.append(f"while {cond}")
                except Exception:
                    loops.append("while loop")
                self.generic_visit(node)

            def visit_Try(self, node):
                handlers = []
                for h in node.handlers:
                    if h.type:
                        try:
                            handlers.append(ast.unparse(h.type))
                        except Exception:
                            handlers.append("Exception")
                    else:
                        handlers.append("All Exceptions")
                exceptions.append(f"try-except block handling: {', '.join(handlers)}")
                self.generic_visit(node)

            def visit_Raise(self, node):
                if node.exc:
                    try:
                        exceptions.append(f"raise {ast.unparse(node.exc)}")
                    except Exception:
                        exceptions.append("raise Exception")
                self.generic_visit(node)

            def visit_Call(self, node):
                try:
                    func_name = ast.unparse(node.func)
                    # Check for security indicators
                    sec_keywords = ["auth", "token", "password", "secret", "file", "open", "exec", "eval", "query", "sql"]
                    for sec in sec_keywords:
                        if sec in func_name.lower():
                            security_indicators.append(f"Call to '{func_name}'")
                    external_calls.append(func_name)
                except Exception:
                    pass
                self.generic_visit(node)

        visitor = ASTVisitor()
        visitor.visit(tree)

        # Check raw code for security markers
        cls._detect_security_strings(code, security_indicators)

        summary = (
            f"Python code with {len(functions)} function(s), "
            f"{len(conditions)} conditional check(s), {len(loops)} loop(s), "
            f"and {len(exceptions)} exception construct(s)."
        )

        return {
            "language": "Python",
            "summary": summary,
            "functions": functions,
            "conditions": list(dict.fromkeys(conditions)),
            "loops": list(dict.fromkeys(loops)),
            "exceptions": list(dict.fromkeys(exceptions)),
            "boundary_comparisons": list(dict.fromkeys(boundary_comparisons)),
            "security_indicators": list(dict.fromkeys(security_indicators)),
            "external_calls": list(dict.fromkeys(external_calls))[:5],
            "raw_counts": {
                "functions": len(functions),
                "conditions": len(conditions),
                "loops": len(loops),
                "exceptions": len(exceptions)
            }
        }

    # -------------------------------------------------------------------------
    # Multi-Language Pattern Analyzer (Java, C, C++, JavaScript)
    # -------------------------------------------------------------------------

    @classmethod
    def _analyze_pattern_based(cls, code: str, language: str) -> Dict[str, Any]:
        """Robust pattern extraction for non-Python or fallback code."""
        functions = []
        conditions = []
        loops = []
        exceptions = []
        boundary_comparisons = []
        security_indicators = []

        # 1. Extract functions
        if language in ("Java", "C", "C++"):
            # Matches: public int calculateDiscount(int price, int discount)
            fn_matches = re.finditer(
                r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)",
                code
            )
            for m in fn_matches:
                fn_name = m.group(1)
                raw_params = m.group(2).strip()
                if fn_name not in ("if", "for", "while", "switch", "catch"):
                    params = [p.strip().split()[-1] for p in raw_params.split(",") if p.strip()]
                    functions.append({"name": fn_name, "parameters": params})
        elif language == "JavaScript":
            # Matches: function calculateDiscount(price, discount) or const calc = (price, discount) =>
            fn_matches = re.finditer(
                r"(?:function\s+([a-zA-Z_]\w*)|(?:const|let|var)\s+([a-zA-Z_]\w*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>)\s*(?:\(([^)]*)\))?",
                code
            )
            for m in fn_matches:
                fn_name = m.group(1) or m.group(2)
                raw_params = m.group(4) or m.group(3) or ""
                if fn_name:
                    params = [p.strip() for p in raw_params.split(",") if p.strip()]
                    functions.append({"name": fn_name, "parameters": params})

        # Fallback if no functions caught via syntax
        if not functions:
            generic_fn = re.findall(r"([a-zA-Z_]\w*)\s*\(([^)]*)\)\s*\{", code)
            for name, raw_p in generic_fn:
                if name not in ("if", "for", "while", "switch", "catch"):
                    params = [p.strip() for p in raw_p.split(",") if p.strip()]
                    functions.append({"name": name, "parameters": params[:4]})

        # 2. Extract conditions: if (...)
        cond_matches = re.findall(r"if\s*\((.*?)\)", code)
        for c in cond_matches:
            c_clean = c.strip()
            conditions.append(c_clean)
            if any(op in c_clean for op in ("<", ">", "<=", ">=", "==", "!=")):
                boundary_comparisons.append(c_clean)

        # 3. Extract loops: for (...), while (...)
        for_matches = re.findall(r"for\s*\((.*?)\)", code)
        for f in for_matches:
            loops.append(f"for ({f.strip()})")

        while_matches = re.findall(r"while\s*\((.*?)\)", code)
        for w in while_matches:
            loops.append(f"while ({w.strip()})")

        # 4. Extract exceptions
        if re.search(r"try\s*\{", code):
            exceptions.append("try-catch block")
        throws = re.findall(r"throw\s+(?:new\s+)?([a-zA-Z_]\w*)", code)
        for t in throws:
            exceptions.append(f"throw {t}")

        # 5. Security markers
        cls._detect_security_strings(code, security_indicators)

        summary = (
            f"{language} code with {len(functions)} identified function(s), "
            f"{len(conditions)} conditional branch(es), {len(loops)} loop construct(s)."
        )

        return {
            "language": language,
            "summary": summary,
            "functions": functions,
            "conditions": list(dict.fromkeys(conditions)),
            "loops": list(dict.fromkeys(loops)),
            "exceptions": list(dict.fromkeys(exceptions)),
            "boundary_comparisons": list(dict.fromkeys(boundary_comparisons)),
            "security_indicators": list(dict.fromkeys(security_indicators)),
            "external_calls": [],
            "raw_counts": {
                "functions": len(functions),
                "conditions": len(conditions),
                "loops": len(loops),
                "exceptions": len(exceptions)
            }
        }

    # -------------------------------------------------------------------------
    # Helper utilities
    # -------------------------------------------------------------------------

    @classmethod
    def _normalize_language(cls, lang: str) -> str:
        """Map user selection to recognized language string."""
        cleaned = (lang or "").strip().lower()
        if "python" in cleaned:
            return "Python"
        elif "javascript" in cleaned or "js" in cleaned:
            return "JavaScript"
        elif "java" in cleaned:
            return "Java"
        elif "c++" in cleaned or "cpp" in cleaned:
            return "C++"
        elif "c" == cleaned:
            return "C"
        return "Python"

    @classmethod
    def _detect_security_strings(cls, code: str, output_list: List[str]):
        """Detect defensive security markers in code strings."""
        patterns = {
            "password": "Password handling detected",
            "token": "Security token/bearer operation detected",
            "auth": "Authentication / Authorization routine detected",
            "admin": "Administrative role check detected",
            "sql": "Database query detected",
            "select": "SQL statement pattern detected",
            "exec": "Dynamic execution / shell call detected",
            "eval": "Dynamic evaluation detected"
        }
        lowered = code.lower()
        for kw, desc in patterns.items():
            if kw in lowered and desc not in output_list:
                output_list.append(desc)
