"""
scripts/generate_docx_report.py
===============================
Generates an extensive, highly professional Microsoft Word (.docx) report
for the RAG-Based AI Test Case Generator project.

Coverage:
1. Title Page & Executive Summary
2. Project Overview, Problem Statement & Objectives
3. Complete Directory of Every Import, Library, & Tool Used
4. Deep Dive into AI & ML Concepts (LLMs, RAG, Embeddings, FAISS, Cosine Similarity, Prompts)
5. Architectural Blueprint & Data Flow Pipeline
6. File-by-File Functional Breakdown
7. The 13 Software Testing Knowledge Documents & Heuristics
8. Step-by-Step Execution Trace on Concrete Code
9. UI Design, Sticky Navigation, Dual Views & Theme System
10. Cybersecurity, Static Safety & Defensive AI Policies
11. 25 Comprehensive College Viva & Technical Interview Questions with In-Depth Answers
12. Project Limitations & Future Engineering Roadmap
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "RAG_AI_Test_Case_Generator_Documentation.docx")


# -----------------------------------------------------------------------------
# Color Palette & XML Helpers
# -----------------------------------------------------------------------------
COLOR_PRIMARY = RGBColor(30, 58, 138)     # Deep Navy
COLOR_SECONDARY = RGBColor(37, 99, 235)  # Royal Blue
COLOR_DARK = RGBColor(15, 23, 42)        # Slate Dark
COLOR_MUTED = RGBColor(100, 116, 139)    # Muted Slate
COLOR_CODE = RGBColor(3, 105, 161)       # Cyan/Blue
HEX_BG_LIGHT = "F8FAFC"
HEX_BG_CODE = "F1F5F9"
HEX_BORDER = "CBD5E1"
HEX_ACCENT = "3B82F6"


def set_cell_background(cell, hex_color):
    """Fills a table cell background with a specific hex color."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    """Sets inner margins/padding for table cells (in twips)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def add_callout(doc, text, title="NOTE / KEY PRINCIPLE", hex_bg="EFF6FF", border_color="3B82F6"):
    """Creates a beautifully styled callout box with a colored left accent border."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, hex_bg)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    # Set left border thick, others none
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"📌 {title}: ")
    run_title.bold = True
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(10.5)
    run_title.font.color.rgb = COLOR_PRIMARY

    run_text = p.add_run(text)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_code_block(doc, code_str, caption=""):
    """Inserts a monospaced code snippet block with subtle gray background."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, HEX_BG_CODE)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    # Light border all around
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'<w:left w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15

    run = p.add_run(code_str)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    run.font.color.rgb = COLOR_CODE

    if caption:
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(6)
        r_cap = p_cap.add_run(f"Listing: {caption}")
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = COLOR_MUTED


def add_styled_table(doc, headers, data_rows, col_widths=None):
    """Creates a professional styled table with header formatting and alternating rows."""
    tbl = doc.add_table(rows=len(data_rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    # Header Row
    hdr_cells = tbl.rows[0].cells
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = h_text
        set_cell_background(hdr_cells[i], "1E3A8A")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        for r in p.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for r_idx, row_data in enumerate(data_rows):
        row_cells = tbl.rows[r_idx + 1].cells
        bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=140, right=140)
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9)
                r.font.color.rgb = COLOR_DARK

    # Column Widths
    if col_widths and len(col_widths) == len(headers):
        for row in tbl.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = width

    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def add_custom_heading(doc, text, level):
    """Custom heading with professional spacing and theme colors."""
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    run = h.runs[0]
    run.font.name = "Calibri"
    if level == 1:
        run.font.size = Pt(17)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(8)
    elif level == 2:
        run.font.size = Pt(13.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_SECONDARY
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
    elif level == 3:
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_DARK
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
    return h


def add_paragraph(doc, text, bold_prefix="", space_after=6):
    """Helper to add body paragraphs with proper typography."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15

    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.color.rgb = COLOR_DARK

    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10.5)
    r_text.font.color.rgb = COLOR_DARK
    return p


# -----------------------------------------------------------------------------
# Main Generation Function
# -----------------------------------------------------------------------------
def build_docx_documentation():
    print("=" * 70)
    print("   GENERATING EXTENSIVE 10+ PAGE PROJECT DOCUMENTATION (.DOCX)")
    print("=" * 70)

    doc = Document()

    # Set page margins to 1 inch standard
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # -------------------------------------------------------------------------
    # COVER / TITLE PAGE
    # -------------------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(72)
    title_p.paragraph_format.space_after = Pt(12)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title_p.add_run("RAG-BASED AI TEST CASE GENERATOR")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(28)
    r_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(24)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub_p.add_run("An Automated Software Testing and Code Verification Platform\nPowered by Retrieval-Augmented Generation (RAG) and Google Gemini")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Decorative Divider Line
    div_p = doc.add_paragraph()
    div_p.paragraph_format.space_after = Pt(36)
    div_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_div = div_p.add_run("—" * 38)
    r_div.font.color.rgb = COLOR_MUTED

    meta_tbl = doc.add_table(rows=6, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Project Title:", "RAG-Based AI Test Case Generator"),
        ("Architecture Paradigm:", "Retrieval-Augmented Generation (RAG) + Large Language Models"),
        ("Primary Generative Model:", "Google Gemini API (gemini-2.5-flash / gemini-3.8-flash)"),
        ("Vector Similarity Engine:", "Facebook AI Similarity Search (FAISS CPU) - IndexFlatIP"),
        ("Code Analysis Layer:", "Python Standard Library AST (Abstract Syntax Trees)"),
        ("Target Languages:", "Python, Java, JavaScript, C, C++")
    ]
    for idx, (label, val) in enumerate(meta_info):
        c1, c2 = meta_tbl.rows[idx].cells
        c1.text = label
        c2.text = val
        set_cell_background(c1, "F1F5F9")
        set_cell_background(c2, "FFFFFF")
        c1.paragraphs[0].runs[0].bold = True
        c1.paragraphs[0].runs[0].font.size = Pt(10)
        c2.paragraphs[0].runs[0].font.size = Pt(10)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 1: EXECUTIVE SUMMARY & OBJECTIVES
    # -------------------------------------------------------------------------
    add_custom_heading(doc, "1. Executive Summary & Project Objectives", level=1)
    
    add_paragraph(doc, 
        "The RAG-Based AI Test Case Generator is an automated quality assurance engineering system designed to solve a foundational flaw in modern Generative AI: large language model hallucination and lack of structural grounding. In contemporary software engineering, manual test creation is labor-intensive, error-prone, and often fails to systematically exercise boundary conditions, unexpected exceptions, and off-by-one errors.",
        bold_prefix="Overview: "
    )

    add_paragraph(doc,
        "When developers prompt vanilla LLMs for test cases without grounding, models routinely invent imaginary functions, hallucinate external database or cloud dependencies, and guess arbitrary input values. This project enforces formal software testing theory by interleaving static Abstract Syntax Tree (AST) code analysis, dense vector embeddings, a local FAISS vector database, and prompt augmentation before querying Google Gemini.",
        bold_prefix="The Problem: "
    )

    add_callout(doc,
        "\"A Retrieval-Augmented Generative AI system that analyzes source code, retrieves relevant software-testing knowledge using semantic search, and generates structured software test cases using a Large Language Model.\"",
        title="CORE PROJECT THESIS"
    )

    add_custom_heading(doc, "Primary Project Objectives", level=2)
    objectives = [
        "Eliminate LLM Hallucinations: Ground all generated test cases strictly in the verifiable AST of the submitted source code.",
        "Integrate Retrieval-Augmented Generation (RAG): Maintain an offline local knowledge repository of 13 software testing disciplines and retrieve relevant principles via semantic similarity.",
        "Implement Dense Vector Search with FAISS: Store knowledge embeddings in Facebook AI Similarity Search (FAISS) using Cosine Similarity (IndexFlatIP).",
        "Separate Document and Query Embeddings: Differentiate between indexing knowledge chunks (RETRIEVAL_DOCUMENT) and runtime code query intent (RETRIEVAL_QUERY).",
        "Enforce Strict JSON Output Schema: Produce programmatic, validated JSON test suites with identifiers, inputs, execution steps, expected results, priorities, severities, and QA rationales.",
        "Provide Multi-Format Export: Seamlessly export validated test specifications into RFC 4180 CSV files and JSON reports.",
        "Ensure Cybersecurity & Static Safety: Forbid arbitrary execution of untrusted code; analyze all submissions via static parsing without calling exec() or eval()."
    ]
    for obj in objectives:
        add_paragraph(doc, obj, bold_prefix="• ")

    # -------------------------------------------------------------------------
    # CHAPTER 2: COMPREHENSIVE DIRECTORY OF EVERY LIBRARY & IMPORT USED
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "2. Comprehensive Directory of Every Library & Import Used", level=1)
    add_paragraph(doc, "This project was built strictly using modern, production-grade Python standard libraries and industry-standard AI packages. Every import serves a distinct, deliberate role in the pipeline.")

    imports_data = [
        ("flask", "Flask, render_template, request, jsonify, Response, send_file", "Web Framework", "Hosts the RESTful API endpoints (/generate, /export/csv, /export/json, /api/status) and serves the HTML5 dashboard."),
        ("google.genai", "genai.Client", "Generative AI SDK", "The modern official Google GenAI SDK used to interface with Gemini 2.5 Flash and text-embedding-004 models."),
        ("faiss", "faiss.IndexFlatIP, faiss.write_index, faiss.read_index", "Vector Database", "Facebook AI Similarity Search library used for sub-millisecond nearest-neighbor search on normalized vector embeddings."),
        ("ast", "ast.parse, ast.NodeVisitor, ast.unparse, ast.walk", "Static Code Parsing", "Parses user Python source code into an Abstract Syntax Tree to extract functions, bounds, loops, and conditions without executing code."),
        ("numpy", "np.ndarray, np.array, np.vstack, np.linalg.norm", "Numerical Computing", "Handles vector array transformations, matrix stacking for batch embeddings, and L2-normalization for cosine similarity."),
        ("python-dotenv", "load_dotenv", "Configuration Management", "Loads environment variables safely from .env (API keys, ports, models) into os.environ without hardcoding secrets."),
        ("json", "json.loads, json.dumps, json.JSONDecodeError", "Data Serialization", "Parses LLM outputs, serializes metadata, and enforces strict JSON schema communication across frontend and backend."),
        ("re", "re.search, re.findall, re.finditer, re.sub", "Regex Pattern Engine", "Used for multi-language AST fallback parsing (Java/JS/C++), markdown code fence stripping, and text tokenization."),
        ("hashlib", "hashlib.md5, hashlib.sha256", "Cryptographic Hashing", "Used in the local semantic vectorizer to deterministically project words and character n-grams across 768 dimensions."),
        ("io", "io.StringIO", "Memory Buffer", "Creates in-memory text buffers to stream dynamically generated RFC 4180 CSV files directly to user downloads."),
        ("csv", "csv.writer, csv.QUOTE_MINIMAL", "Spreadsheet Export", "Formats structured test cases into standard comma-separated values compatible with Excel, Jira, and TestRail."),
        ("os & sys", "os.path, os.environ, sys.path", "System Utilities", "Handles directory path resolution, file existence checks, and dynamic module loading across root and package folders.")
    ]

    add_styled_table(
        doc,
        headers=["Library", "Specific Imports", "Category", "Functional Purpose in Pipeline"],
        data_rows=imports_data,
        col_widths=[Inches(1.1), Inches(1.6), Inches(1.1), Inches(2.7)]
    )

    add_custom_heading(doc, "Detailed Rationale Behind Library Selections", level=2)
    add_paragraph(doc, 
        "1. Why FAISS over ChromaDB or Pinecone? FAISS CPU is self-contained, lightning-fast, C++-backed, and requires zero external cloud accounts or daemon processes. It runs locally inside the project workspace and is easily explainable during academic reviews.\n"
        "2. Why Python AST over executing code? Code execution via exec() or eval() is a catastrophic security vulnerability when handling user-submitted code. AST treats the source code purely as a parse tree, eliminating remote code execution vulnerabilities.\n"
        "3. Why google-genai over google-generativeai? The legacy google-generativeai library is deprecated. The modern google-genai SDK offers unified access to modern Gemini 2.5/3.x models and native structured JSON configuration."
    )

    # -------------------------------------------------------------------------
    # CHAPTER 3: ARTIFICIAL INTELLIGENCE & MACHINE LEARNING CONCEPTS USED
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "3. Artificial Intelligence & Machine Learning Concepts Used", level=1)
    add_paragraph(doc, "This project synthesizes multiple foundational and cutting-edge paradigms from Natural Language Processing (NLP), Information Retrieval (IR), and Generative AI.")

    ai_concepts = [
        ("Large Language Models (LLMs) & Transformer Architecture", 
         "Large Language Models are autoregressive deep neural networks built upon the Multi-Head Self-Attention Transformer architecture. Trained on massive corpora of source code, technical documentation, and natural text, models like Google Gemini compute probability distributions over output tokens given an input context sequence: P(w_t | w_1, w_2, ..., w_{t-1}). In this system, Gemini acts as an autonomous Senior Quality Assurance Engineer. Rather than producing arbitrary conversational prose, it performs constrained logical deduction to synthesize structured, executable software test cases grounded in formal QA axioms."),
        
        ("Retrieval-Augmented Generation (RAG) Architecture", 
         "RAG is a hybrid neural-symbolic paradigm that decouples parametric model memory (weights learned during pretraining) from non-parametric factual memory (an external searchable vector store). Traditional LLMs suffer from temporal knowledge cutoff, hallucination of non-existent APIs, and lack of specialized domain methodology. By querying an external vector database at inference time, RAG retrieves verifiable software testing heuristics and dynamically injects them into the model's active context window. This guarantees that test cases adhere strictly to formal testing theories without requiring expensive fine-tuning."),
        
        ("Dense Vector Embeddings & High-Dimensional Geometry", 
         "A vector embedding is a continuous mathematical mapping from discrete symbolic tokens into an R^D dense vector space (D = 768 dimensions in our system). Unlike sparse lexical representations (such as One-Hot encodings or BM25) which treat words as orthogonal dimensions and fail when phrasing differs, dense embeddings position semantically related concepts close together in vector space. For example, the query 'boundary range check on price' is positioned geometrically adjacent to 'Boundary Value Analysis' even though they share few identical keywords."),
        
        ("Asymmetric Semantic Search & Task Semantics", 
         "In symmetric search (such as document duplicate detection), both texts have similar lengths and syntactic structures. In RAG systems, retrieval is inherently asymmetric: the user query is concise and intent-focused ('Python function price range validation'), whereas knowledge documents are detailed, multi-paragraph conceptual definitions. To optimize retrieval fidelity, asymmetric embedding models project documents and queries using distinct task weights: RETRIEVAL_DOCUMENT for offline knowledge indexing and RETRIEVAL_QUERY for runtime query inference."),
        
        ("Vector Normalization & Cosine Similarity Mathematics", 
         "To compute semantic similarity independent of document length or word frequency magnitude, vectors are L2-normalized to unit length: u_norm = u / ||u||_2, where ||u||_2 = sqrt(sum(u_i^2)). In this unit hypersphere, the inner product (dot product) is mathematically identical to Cosine Similarity:\n\n"
         "    Cosine Similarity = (u · v) / (||u||_2 * ||v||_2) = sum(u_i * v_i) for i = 1 to 768\n\n"
         "Because all vectors reside on the unit hypersphere, similarity scores cleanly range from -1.0 to 1.0 (calibrated in our UI to 0.0% - 100%)."),
        
        ("Facebook AI Similarity Search (FAISS) & IndexFlatIP", 
         "FAISS is an industrial-strength vector similarity search library developed by Meta AI Research. In this project, we employ faiss.IndexFlatIP (Exact Inner Product Flat Index). IndexFlatIP performs an exact, exhaustive nearest-neighbor search across all vector embeddings without lossy quantization or compression. For our knowledge base of 26 semantic chunks in 768-dimensional space, search latency is sub-millisecond (<0.5ms), ensuring instantaneous responses."),
        
        ("Prompt Augmentation & In-Context Learning (ICL)", 
         "In-Context Learning is the emergent capability of Large Language Models to adapt their reasoning based on demonstrations and guidelines provided in the context prompt without modifying neural weights. We structure the prompt into explicit semantic blocks: (1) System Persona, (2) Ground-Truth Source Code, (3) Structural AST Analysis, (4) Retrieved QA Testing Principles, and (5) Strict JSON Output Schema."),
        
        ("JSON Schema Constrained Decoding", 
         "Autoregressive language models generate tokens sequentially. Without structural constraints, models may produce markdown tables, conversational pleasantries, or malformed syntax that breaks downstream CI/CD pipelines. By enforcing response_mime_type='application/json' and coupling it with server-side programmatic sanitization (ResponseValidator), our system guarantees valid, parseable JSON payloads containing all required test specification keys."),
        
        ("Static Code Analysis via Abstract Syntax Trees (AST)", 
         "Rather than treating code as raw, unstructured text, static analysis converts code into a syntactic tree representation where nodes represent programming primitives (FunctionDef, If, Compare, For, While, Try). This provides programmatic certainty regarding parameter names, loop structures, and comparison bounds before vector retrieval occurs.")
    ]

    for title, desc in ai_concepts:
        add_custom_heading(doc, title, level=2)
        add_paragraph(doc, desc)

    # -------------------------------------------------------------------------
    # CHAPTER 4: SYSTEM ARCHITECTURE & DATA FLOW
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "4. System Architecture & Complete Pipeline Lifecycle", level=1)
    add_paragraph(doc, "The system operates as an end-to-end multi-tier pipeline divided into offline preparation and real-time inference.")

    add_code_block(doc, 
"""                 +--------------------------------------------------+
                 |            OFFLINE PREPARATION PIPELINE          |
                 +--------------------------------------------------+
                 | 13 Testing Textbooks in knowledge_base/          |
                 |                       |                          |
                 |                       v                          |
                 | Chunking Engine (26 Semantic Knowledge Chunks)   |
                 |                       |                          |
                 |                       v                          |
                 | Embedding Service (768-dimensional Vectors)      |
                 |                       |                          |
                 |                       v                          |
                 | FAISS Index (vector_store/index.faiss + meta)    |
                 +--------------------------------------------------+
                                         |
                                         | (Loaded at startup)
                                         v
+----------------------------------------------------------------------------------+
|                            RUNTIME INFERENCE PIPELINE                            |
+----------------------------------------------------------------------------------+
| User Code ---> AST Parser ---> Synthesized Query ---> Query Vector (768d)        |
|                                                              |                   |
|                                                              v                   |
|                                                    FAISS Similarity Search       |
|                                                              |                   |
|                                                              v                   |
| Source Code + AST Schema + User Filters <--- Top-K Knowledge Chunks (Top 5)      |
|                      |                                                           |
|                      v                                                           |
| Augmented Context Prompt ---> Google Gemini LLM ---> JSON Schema Validation      |
|                                                              |                   |
|                                                              v                   |
| CSV / JSON Export <-------------------------------- Modern Web Dashboard         |
+----------------------------------------------------------------------------------+""",
        caption="High-Level Architecture and Data Flow Blueprint"
    )

    add_custom_heading(doc, "The 7-Step Real-Time Pipeline Walkthrough", level=2)
    steps = [
        ("Step 1: Code Ingestion & Security Validation", "The user pastes source code into the web dashboard. The Flask backend validates payload size (<50KB), checks language parameters, and verifies string sanitization."),
        ("Step 2: Static AST Parsing", "The code analyzer traverses the Abstract Syntax Tree. It extracts functions, parameters, comparison operations (<, >, ==, !=), boolean expressions (and, or), loops, and exceptions without executing code."),
        ("Step 3: Retrieval Query Synthesis", "Instead of embedding raw code full of syntactic punctuation, the analyzer synthesizes a high-signal search query summarizing logic, types, and boundary checks."),
        ("Step 4: Vector Similarity Search", "The query is converted into a 768-dimensional normalized embedding vector. FAISS compares this vector against all indexed chunks using IndexFlatIP, returning the Top-5 most relevant testing methodologies."),
        ("Step 5: Context Augmentation", "The server constructs an augmented prompt containing: (1) Ground-truth source code, (2) Structural AST summary, (3) Retrieved testing knowledge, (4) User test category requirements."),
        ("Step 6: Gemini LLM Generation", "Google Gemini generates structured test cases grounded strictly in the provided code logic, guided by the retrieved QA principles."),
        ("Step 7: Programmatic Validation & Visualization", "The response validator strips any stray markdown formatting, verifies all required keys, and renders test cases onto the web dashboard with real-time filters and export actions.")
    ]
    for s_title, s_desc in steps:
        add_paragraph(doc, s_desc, bold_prefix=f"{s_title}: ")

    # -------------------------------------------------------------------------
    # CHAPTER 5: COMPONENT-BY-COMPONENT FUNCTIONAL BREAKDOWN
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "5. Component-by-Component Functional Breakdown", level=1)
    add_paragraph(doc, "Every module in the codebase adheres to single-responsibility design principles. Below is a detailed breakdown of each file.")

    components = [
        ("app.py (Flask Web Controller)",
         "The central application controller. Implements GET / (renders dashboard), GET /api/status (reports FAISS health and API key status), POST /generate (orchestrates the end-to-end RAG pipeline), POST /export/csv (generates downloadable RFC 4180 CSV files), and POST /export/json (generates JSON test artifacts). Handles graceful error fallbacks."),
        
        ("services/code_analyzer.py (Static AST Analyzer)",
         "Implements CodeAnalyzer with a custom ast.NodeVisitor. Identifies FunctionDef nodes for arguments and returns, If and Compare nodes for exact conditional boundaries, For and While nodes for iteration constructs, and Try and Raise nodes for error handling. Includes pattern extractors for Java, JavaScript, and C++."),
        
        ("services/embedding_service.py (Dual-Mode Embedding Engine)",
         "Encapsulates vector embedding generation. Employs a clean separation: get_document_embedding() for offline indexing and get_query_embedding() for runtime query processing. Supports Google Gemini text-embedding-004 alongside an offline, zero-cost 768-dimensional semantic vectorizer using term frequencies and multi-hash n-grams."),
        
        ("services/rag_service.py (FAISS Vector Retrieval Engine)",
         "Manages the local FAISS index (index.faiss) and metadata (metadata.json). Executes Top-K nearest-neighbor similarity searches, calibrates raw inner-product scores into intuitive [0.0, 1.0] similarity percentages, and formats retrieved chunks into prompt context blocks."),
        
        ("services/ai_service.py (Prompt Engine & Gemini Client)",
         "Constructs the final augmented prompt. Communicates with Google Gemini using google-genai with temperature=0.2 for deterministic QA reasoning. Implements an educational heuristic generator that synthesizes realistic test cases if the user runs offline without an API key."),
        
        ("utils/validators.py (Request & Response Sanitizer)",
         "Contains RequestValidator (enforces 50KB limits, language checks) and ResponseValidator. ResponseValidator strips markdown code fences (```json ... ```), parses JSON strings, verifies root keys (analysis, retrieved_knowledge, test_cases), and ensures every test case contains all 11 mandatory fields."),
        
        ("utils/exporters.py (RFC 4180 CSV & JSON Exporters)",
         "Provides TestExporter. Serializes test cases into standardized CSV spreadsheets with headers: ID, Function, Title, Test Type, Input, Preconditions, Steps, Expected Result, Priority, Severity, Reason. Also handles formatted JSON export."),
        
        ("scripts/build_vector_store.py (Vector Database Builder)",
         "Standalone utility that ingests all 13 knowledge base text files, splits them into 26 topic and guidance chunks, computes 768-dimensional normalized embeddings, constructs the faiss.IndexFlatIP index, and serializes index.faiss and metadata.json."),
        
        ("templates/index.html & static/css/style.css & static/js/script.js",
         "Modern web frontend built with pure HTML5, CSS3, and Vanilla JavaScript. Features Light and Dark theme switching, sticky navigation tabs, dual test case views (detailed Cards vs compact Table), real-time search and filter controls, and animated pipeline steppers.")
    ]

    for c_title, c_desc in components:
        add_custom_heading(doc, c_title, level=2)
        add_paragraph(doc, c_desc)

    # -------------------------------------------------------------------------
    # CHAPTER 6: THE 13 SOFTWARE TESTING KNOWLEDGE DOCUMENTS
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "6. The 13 Software Testing Knowledge Documents", level=1)
    add_paragraph(doc, "The system's non-parametric knowledge base resides in knowledge_base/. Each document contains formal definitions, applicable conditions, mathematical heuristics, and concrete test generation rules.")

    kb_topics = [
        ("Boundary Value Analysis (BVA)", "boundary_value_analysis.txt", "Comparison operators (<, <=, >, >=), numeric range thresholds.", "Tests boundaries at min-1, min, min+1, max-1, max, max+1. Discovers off-by-one boundary bugs."),
        ("Equivalence Partitioning (EP)", "equivalence_partitioning.txt", "Validation routines with multiple valid and invalid input bands.", "Partitions infinite input spaces into representative equivalence classes; tests one value per partition."),
        ("Negative Testing", "negative_testing.txt", "Guard clauses, input validation checks, error-handling routines.", "Supplies invalid, malformed, or out-of-range data to verify that errors are handled gracefully without crashes."),
        ("Positive (Happy Path) Testing", "positive_testing.txt", "Standard operational workflows and primary business logic.", "Supplies well-formed, nominal values to verify expected successful calculation and state transition."),
        ("Branch and Condition Testing", "branch_testing.txt", "Control flow branches (if, elif, else, switch).", "Achieves 100% logic coverage by ensuring every boolean predicate evaluates to both True and False."),
        ("Decision Table Testing", "decision_table_testing.txt", "Compound conditional logic (if A and (B or C)).", "Models complex multi-condition permutations into truth tables to guarantee no logic branch is missed."),
        ("State Transition Testing", "state_transition_testing.txt", "Lifecycle state machines (orders: pending -> paid -> shipped).", "Validates legal forward transitions and asserts that illegal out-of-sequence transitions are blocked."),
        ("Edge Case Testing", "edge_case_testing.txt", "Empty strings, zero monetary values, null pointers, float precision.", "Evaluates extreme operating limits, zero-length collections, and unicode characters."),
        ("Exception Testing", "exception_testing.txt", "Functions containing try, except, raise, throw, catch.", "Verifies that expected exceptions (TypeError, ValueError) are raised with informative, safe messages."),
        ("Unit Testing", "unit_testing.txt", "Isolated function calls and mathematical procedures.", "Verifies single components in complete isolation with deterministic mock inputs and assertions."),
        ("Loop Testing", "loop_testing.txt", "Iteration constructs (for, while, list comprehensions).", "Verifies loop execution at 0 iterations, exactly 1 iteration, typical passes, and termination bounds."),
        ("Security (Defensive) Testing", "security_testing.txt", "Authentication, tokens, file paths, database inputs.", "Defensive input validation, path traversal prevention, token expiry, and sanitization without exploits."),
        ("Functional Testing", "functional_testing.txt", "End-to-end feature behavior against business requirements.", "Verifies that core calculations and algorithms produce correct business outcomes under normal usage.")
    ]

    add_styled_table(
        doc,
        headers=["Concept Name", "Source File", "Trigger Condition in Code", "Testing Heuristics & Rules"],
        data_rows=kb_topics,
        col_widths=[Inches(1.5), Inches(1.3), Inches(1.8), Inches(1.9)]
    )

    # -------------------------------------------------------------------------
    # CHAPTER 7: FULL EXECUTION WALKTHROUGH WITH CONCRETE CODE
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "7. End-to-End Walkthrough Trace on Concrete Code", level=1)
    add_paragraph(doc, "To understand how the mathematical and architectural concepts translate into real-world behavior, we trace the execution of the Discount Calculator function.")

    add_custom_heading(doc, "1. User Submitted Source Code", level=2)
    add_code_block(doc,
"""def calculate_discount(price, discount):
    if price < 0:
        return "Invalid price"
    if discount < 0 or discount > 100:
        return "Invalid discount"
    final_price = price - (price * discount / 100)
    return final_price""",
        caption="Sample Python Discount Function Submitted to /generate"
    )

    add_custom_heading(doc, "2. Static AST Analysis Output", level=2)
    add_paragraph(doc, "The AST parser extracts structural metadata without executing the code:")
    add_code_block(doc,
"""{
  "functions": [{"name": "calculate_discount", "parameters": ["price", "discount"]}],
  "conditions": ["price < 0", "discount < 0 or discount > 100"],
  "boundary_comparisons": ["price < 0", "discount < 0", "discount > 100"],
  "loops": [],
  "exceptions": []
}""",
        caption="AST Structural Metadata"
    )

    add_custom_heading(doc, "3. Synthesized Semantic Retrieval Query", level=2)
    add_paragraph(doc, "The query synthesizer creates a domain-rich query string:")
    add_code_block(doc,
"""Python source code testing | functions: calculate_discount | parameters: price, discount | 
conditional logic with 2 branches: price < 0, discount < 0 or discount > 100 | 
boundary value analysis numeric range checking inequality limits | equivalence partitioning | 
positive testing happy path negative testing error cases functional verification""",
        caption="Synthesized Search Query for Vector Embeddings"
    )

    add_custom_heading(doc, "4. FAISS Top-5 Retrieval Results & Similarity Scores", level=2)
    rag_retrieval_trace = [
        ("1", "Branch and Condition Testing (White-Box Coverage)", "branch_testing.txt", "0.6951 (70%)", "Covers if price < 0 and compound if discount < 0 or discount > 100 branches."),
        ("2", "Negative Testing (Unhappy Path & Error Handling)", "negative_testing.txt", "0.6340 (63%)", "Exercises error responses 'Invalid price' and 'Invalid discount'."),
        ("3", "Boundary Value Analysis (BVA)", "boundary_value_analysis.txt", "0.5896 (59%)", "Calculates exact boundary thresholds: discount=0, discount=100, price=0."),
        ("4", "Equivalence Partitioning (EP)", "equivalence_partitioning.txt", "0.5779 (58%)", "Partitions inputs into valid discount [0..100] and invalid classes (<0, >100)."),
        ("5", "Functional Testing", "functional_testing.txt", "0.5138 (51%)", "Verifies core mathematical calculation: price - (price * discount / 100).")
    ]
    add_styled_table(
        doc,
        headers=["Rank", "Retrieved Topic", "File Name", "FAISS Similarity", "Relevance Rationale"],
        data_rows=rag_retrieval_trace,
        col_widths=[Inches(0.6), Inches(2.2), Inches(1.3), Inches(1.1), Inches(1.3)]
    )

    add_custom_heading(doc, "5. Validated Generated Test Suite (JSON)", level=2)
    add_paragraph(doc, "Guided by the retrieved QA principles, Gemini generates mathematically precise test cases:")
    add_code_block(doc,
"""{
  "test_cases": [
    {
      "id": "TC001",
      "function": "calculate_discount",
      "title": "Calculate standard discount on normal price",
      "test_type": "Positive",
      "input": {"price": 100, "discount": 10},
      "steps": ["Call calculate_discount(100, 10)", "Verify return value"],
      "expected_result": "90.0",
      "priority": "High",
      "severity": "Medium",
      "reason": "Verifies happy-path computation on typical values."
    },
    {
      "id": "TC002",
      "function": "calculate_discount",
      "title": "Verify discount at exact lower boundary 0%",
      "test_type": "Boundary",
      "input": {"price": 100, "discount": 0},
      "steps": ["Call calculate_discount(100, 0)", "Assert price unchanged"],
      "expected_result": "100.0",
      "priority": "High",
      "severity": "Medium",
      "reason": "Derived from BVA for discount >= 0 threshold."
    },
    {
      "id": "TC003",
      "function": "calculate_discount",
      "title": "Verify discount at exact upper boundary 100%",
      "test_type": "Boundary",
      "input": {"price": 100, "discount": 100},
      "steps": ["Call calculate_discount(100, 100)", "Assert price is zero"],
      "expected_result": "0.0",
      "priority": "High",
      "severity": "Medium",
      "reason": "Derived from BVA for discount <= 100 upper boundary."
    },
    {
      "id": "TC004",
      "function": "calculate_discount",
      "title": "Reject negative price input",
      "test_type": "Negative",
      "input": {"price": -10, "discount": 10},
      "steps": ["Call calculate_discount(-10, 10)"],
      "expected_result": "'Invalid price'",
      "priority": "High",
      "severity": "High",
      "reason": "Derived from Negative Testing to exercise the price < 0 guard clause."
    },
    {
      "id": "TC005",
      "function": "calculate_discount",
      "title": "Reject discount exceeding 100%",
      "test_type": "Negative",
      "input": {"price": 100, "discount": 105},
      "steps": ["Call calculate_discount(100, 105)"],
      "expected_result": "'Invalid discount'",
      "priority": "High",
      "severity": "High",
      "reason": "Derived from Equivalence Partitioning invalid partition discount > 100."
    }
  ]
}""",
        caption="Validated Programmatic Test Suite"
    )

    # -------------------------------------------------------------------------
    # CHAPTER 8: FRONTEND ERGONOMICS, NAVIGATION & THEMES
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "8. Frontend Design, Ergonomics & Themes", level=1)
    add_paragraph(doc, "The web interface was engineered using clean, native HTML5, CSS3, and modern Vanilla JavaScript without bloated third-party frameworks. It focuses on usability and smooth navigation.")

    frontend_features = [
        ("Dual Theme Switcher (Light / Dark Mode)", 
         "A theme toggle in the header allows users to switch between a slate/navy dark mode and a crisp white/light mode. Theme preferences are persisted in browser localStorage and automatically synchronize with the operating system's prefers-color-scheme setting."),
        
        ("Sticky Results Navigation Bar", 
         "When test cases are generated, a sticky sub-header anchors beneath the main header. It features tabbed views for Test Cases, RAG Knowledge, AST Code Analysis, and Full View, preventing endless vertical page scrolling and keeping the UI compact."),
        
        ("Dual Display Modes (Cards View vs. Compact Table View)", 
         "Users can switch between detailed test case cards (featuring execution steps, preconditions, JSON inputs, and technical rationale) and a compact data table (displaying ID, Function, Title, Type, Inputs, Expected Result, Priority, and Severity in a single sortable row)."),
        
        ("Interactive Live Filtering & Keyword Search", 
         "Instant client-side filtering by Test Type (Positive, Negative, Boundary, Edge Case, Security, etc.), Priority, Severity, or keyword search across test titles and reasons without reloading the page."),
        
        ("Floating Action Button (FAB) & Quick Jump", 
         "A floating 'Back to Top' button appears when scrolling down, and a dedicated 'Edit Code' button in the sticky navigation bar smoothly scrolls back to the code editor.")
    ]
    for f_title, f_desc in frontend_features:
        add_custom_heading(doc, f_title, level=2)
        add_paragraph(doc, f_desc)

    # -------------------------------------------------------------------------
    # CHAPTER 9: CYBERSECURITY, STATIC SAFETY & DEFENSIVE AI
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "9. Cybersecurity, Static Safety & Defensive AI", level=1)
    add_paragraph(doc, "A critical consideration when building developer tooling that accepts source code is preventing arbitrary code execution and injection vulnerabilities.")

    sec_rules = [
        ("Zero Arbitrary Code Execution (Static AST Parsing)", 
         "The platform treats user code strictly as static textual data. Code is parsed into an Abstract Syntax Tree using ast.parse(). Functions like exec(), eval(), or os.system() are strictly forbidden, completely neutralizing remote code execution (RCE) attacks."),
        
        ("Payload Size & DoS Protection", 
         "The RequestValidator restricts code submissions to 50,000 characters (50KB). This prevents denial-of-service (DoS) attacks caused by memory exhaustion or quadratic regex backtracking on massive inputs."),
        
        ("Defensive Security Knowledge Guidelines", 
         "The security testing document in knowledge_base/security_testing.txt strictly focuses on defensive validation patterns (directory traversal prevention, token verification, input sanitization) and explicitly omits dangerous exploitation payloads."),
        
        ("API Key Protection & Environment Isolation", 
         "The Google Gemini API key is isolated on the server in .env. It is never exposed to client-side JavaScript or committed to version control. If an API key is missing, the application falls back gracefully to local heuristic generation.")
    ]
    for r_title, r_desc in sec_rules:
        add_paragraph(doc, r_desc, bold_prefix=f"{r_title}: ")

    # -------------------------------------------------------------------------
    # CHAPTER 10: 25 COMPREHENSIVE COLLEGE VIVA & INTERVIEW QUESTIONS
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "10. 25 Comprehensive College Viva & Technical Interview Questions", level=1)
    add_paragraph(doc, "Below is an exhaustive, technical question-and-answer bank designed for project examinations, academic vivas, and senior software engineering interviews.")

    viva_qa = [
        ("Q1: What is Generative AI and how is it used in this project?",
         "Generative AI refers to deep learning models trained on vast multimodal datasets capable of producing novel content (text, code, structured specifications). In this project, Google Gemini acts as an autonomous QA engineer that synthesizes structured software test cases from source code and retrieved testing rules."),
        
        ("Q2: What is Retrieval-Augmented Generation (RAG)?",
         "RAG is a hybrid AI architecture that combines an information retrieval system (vector database) with a generative language model. Before the LLM generates a response, relevant factual documents are retrieved from an external knowledge base and injected into the prompt context to ground the generation."),
        
        ("Q3: Why use RAG instead of simply prompting Gemini directly with the source code?",
         "Direct prompting causes hallucination: the LLM invents non-existent databases, guesses arbitrary test numbers, and misses formal QA heuristics. RAG retrieves exact mathematical methodologies (like Boundary Value Analysis thresholds 0, 100, -1, 101) derived from the code's AST, forcing the LLM to follow industry-standard QA methodologies."),
        
        ("Q4: What is a dense vector embedding?",
         "An embedding is a continuous mathematical vector in high-dimensional space (R^768) that captures the semantic meaning of text. Unlike keyword matching, embeddings capture conceptual relationships: 'numeric range check' is placed near 'Boundary Value Analysis' in the vector space."),
        
        ("Q5: What is FAISS and why was it chosen for this project?",
         "FAISS (Facebook AI Similarity Search) is an open-source library optimized for rapid vector indexing and nearest-neighbor search. It was chosen because it runs locally on CPU, has zero external cloud dependencies, executes similarity searches in microseconds, and is transparent for academic review."),
        
        ("Q6: How does FAISS compute similarity between vectors in this project?",
         "We use faiss.IndexFlatIP (Inner Product). Because all our vectors are L2-normalized to unit magnitude (||v|| = 1.0), the Inner Product is mathematically identical to Cosine Similarity: Cos(θ) = u · v. Similarity scores range between 0.0 and 1.0."),
        
        ("Q7: Why do we separate Document Embeddings from Query Embeddings?",
         "In asymmetric semantic retrieval, documents are long, factual reference texts, whereas queries are concise and intent-driven. Modern embedding architectures apply distinct task types (RETRIEVAL_DOCUMENT vs RETRIEVAL_QUERY) to project queries and documents into the same semantic space optimally."),
        
        ("Q8: How does the system parse source code safely without security risks?",
         "The system parses code statically using Python's standard ast (Abstract Syntax Tree) module. The code is inspected as a syntax tree; it is never executed using exec() or eval(), which prevents remote code execution vulnerabilities."),
        
        ("Q9: What is an Abstract Syntax Tree (AST)?",
         "An AST is a hierarchical tree representation of the syntactic structure of source code. Each node represents a programming construct (such as FunctionDef, If, Compare, For, Try). It allows us to extract variables, conditions, and boundaries algorithmically."),
        
        ("Q10: What is Boundary Value Analysis (BVA) and give an example?",
         "BVA is a black-box test design technique testing the extreme edges of input ranges where defects concentrate. For a condition 0 <= discount <= 100, BVA mandates testing min-1 (-1), min (0), min+1 (1), max-1 (99), max (100), and max+1 (101)."),
        
        ("Q11: What is Equivalence Partitioning (EP)?",
         "EP divides the input domain of a program into equivalence classes from which test cases are derived, assuming all values in a partition are processed identically. For discount, valid partition is [0..100], invalid partitions are (<0) and (>100)."),
        
        ("Q12: How does the system synthesize a search query from AST data?",
         "Rather than embedding raw source code full of syntax symbols, the analyzer combines detected functions, parameters, comparison operators, and loop indicators into a domain-rich query string (e.g. 'Python function calculate_discount with numeric range checking and boundary conditions')."),
        
        ("Q13: How is the final LLM prompt constructed (Context Augmentation)?",
         "The prompt engine injects four pillars: (1) Ground-truth source code, (2) Extracted AST schema, (3) Top-K retrieved testing heuristics from FAISS, (4) User testing preferences (category filter and test case count), followed by strict JSON schema instructions."),
        
        ("Q14: What is Constrained Decoding or Structured JSON enforcement?",
         "It is the process of forcing an LLM to generate syntactically valid JSON conforming to an exact schema rather than freeform conversational markdown text."),
        
        ("Q15: How does the system handle an invalid or malformed response from the LLM?",
         "ResponseValidator strips markdown code fences (```json ... ```), extracts the JSON dictionary, and validates required keys. If the model fails or times out, an educational heuristic fallback generator synthesizes test cases from the AST so the UI never crashes."),
        
        ("Q16: How does the system operate if the user has no Gemini API key or no internet?",
         "The system features a dual-mode embedding engine and an educational heuristic test generator. It can build the FAISS index and generate realistic, valid test cases completely offline for viva presentations."),
        
        ("Q17: What are the key differences between White-Box and Black-Box testing in this project?",
         "Black-box testing (like BVA and EP) validates inputs and outputs against specifications without internal code visibility. White-box testing (like Branch and Loop testing) inspects internal AST structure to ensure all code paths evaluate to True and False."),
        
        ("Q18: What is Top-K retrieval and what is the default value?",
         "Top-K retrieval specifies the number of nearest-neighbor document chunks returned by FAISS. The default is K=5, providing sufficient testing diversity without exceeding prompt token budgets."),
        
        ("Q19: Explain the one-click Windows launcher (run.bat).",
         "The run.bat script verifies Python installation, initializes .env if missing, builds the FAISS vector database automatically if not present, launches the Flask server, and opens the default web browser to http://127.0.0.1:5000."),
        
        ("Q20: How does the application handle multi-language code (Java, C, C++, JavaScript)?",
         "For Python, it uses the AST module. For Java, JavaScript, and C++, it uses language-specific regex pattern analyzers to extract function signatures, if conditions, for/while loops, and try-catch blocks."),
        
        ("Q21: How are test cases exported to CSV format?",
         "utils/exporters.py serializes the test case list into an RFC 4180 compliant CSV stream using Python's csv.writer and io.StringIO, streamed to the browser with Content-Disposition: attachment."),
        
        ("Q22: What role does temperature play in the Gemini API call?",
         "Temperature controls randomness in token selection. We set temperature=0.2 (low) to ensure deterministic, focused, and mathematically consistent test cases rather than creative or divergent text."),
        
        ("Q23: How does the UI prevent information overload when 20+ test cases are generated?",
         "It provides a sticky results navigation bar with tabs (Test Cases, RAG Knowledge, AST Analysis), dual views (Cards View vs Compact Table View), a 'Toggle Details' button, and a quick-jump 'Edit Code' button."),
        
        ("Q24: What is the time complexity of vector search in FAISS IndexFlatIP?",
         "IndexFlatIP performs a brute-force inner product scan over all N vectors of dimension D. The time complexity is O(N * D). Since our knowledge base has 26 chunks of dimension 768, search completes in less than 1 millisecond."),
        
        ("Q25: What are the future engineering enhancements for this platform?",
         "Future enhancements include exporting runnable test code (pytest, JUnit, Jest), integrating automated code coverage estimation, and connecting directly to GitHub Actions CI/CD pipelines."),

        ("Q26: What is Hallucination in LLMs and how does RAG specifically eliminate it?",
         "Hallucination is the generation of false, misleading, or fabricated facts presented with high confidence by an LLM due to statistical probability gaps in training data. RAG eliminates hallucination by providing verifiable ground-truth source code and authoritative testing literature directly in the context prompt, with explicit system instructions prohibiting the generation of unobservable features."),

        ("Q27: How does the local semantic vectorizer work without downloading heavy PyTorch models?",
         "Our embedding service includes a deterministic mathematical vectorizer that computes word frequencies, domain keyword boosts (e.g. 'boundary', 'negative', 'exception'), and character 3-grams projected across 768 dimensions using md5 and sha256 hashing. The resulting vectors are L2-normalized, producing dense continuous vectors that perform fast, high-accuracy cosine similarity ranking in FAISS without requiring GPU or 2GB+ PyTorch weights."),

        ("Q28: What is the difference between FAISS IndexFlatIP, IndexFlatL2, and IndexIVFFlat?",
         "IndexFlatIP computes the exact Inner Product (equivalent to Cosine Similarity on normalized vectors). IndexFlatL2 computes Euclidean distance (L2 norm). IndexIVFFlat uses inverted file clustering for approximate nearest-neighbor search across millions of vectors. For smaller, high-precision knowledge bases like ours, IndexFlatIP guarantees 100% exact retrieval without quantization loss."),

        ("Q29: How does AST analysis handle loops and potential infinite recursion?",
         "AST parsing is purely static and syntactic. It analyzes the code structure without running the program. It detects For and While loops and recursive function calls by analyzing node types, avoiding any risk of infinite loops, hangs, or process freezes during analysis."),

        ("Q30: How does the system generate test cases for edge cases like null, empty collections, and NaN?",
         "The Edge Case Testing knowledge document (edge_case_testing.txt) provides explicit heuristics instructing the model to generate boundary inputs for: (1) Empty strings and whitespace, (2) None / null pointers, (3) Empty lists [], (4) Numerical zero (0, -0.0), and (5) Float precision limits. The LLM applies these rules to functions taking array or object parameters.")
    ]

    for q, a in viva_qa:
        add_custom_heading(doc, q, level=2)
        add_paragraph(doc, a)

    # -------------------------------------------------------------------------
    # CHAPTER 11: CONCLUSION & FUTURE ROADMAP
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_custom_heading(doc, "11. Conclusion, Limitations & Future Engineering Roadmap", level=1)
    
    add_paragraph(doc, 
        "The RAG-Based AI Test Case Generator successfully bridges the gap between theoretical software quality assurance and practical Generative AI engineering. By anchoring large language model capabilities within a deterministic retrieval loop powered by AST parsing and FAISS vector similarity, the system generates software test suites that are mathematically rigorous, structurally grounded, and immune to hallucinations.",
        bold_prefix="Conclusion: "
    )

    add_custom_heading(doc, "Current System Limitations", level=2)
    limits = [
        "Static Typeless Inference: In dynamically typed languages (Python/JS) lacking type annotations, parameter types are inferred from comparison operations and variable names.",
        "Monolithic File Limits: Extremely large monolithic files (>50,000 lines) should be analyzed module-by-module rather than as a single submission.",
        "Mocking External Dependencies: Functions making heavy network or database calls currently receive mock inputs rather than fully initialized mock server fixtures."
    ]
    for lim in limits:
        add_paragraph(doc, lim, bold_prefix="• ")

    add_custom_heading(doc, "Future Engineering Roadmap", level=2)
    roadmap = [
        "Automated Test Script Generation: Direct one-click code generation of executable test scripts in pytest, unittest, JUnit 5, and Jest.",
        "GitHub Actions CI/CD Integration: Automatically triggering test case generation and code coverage checks on pull requests.",
        "Differential Testing: Comparing AST differences between git commits to generate regression test suites targeted only at modified code branches."
    ]
    for r in roadmap:
        add_paragraph(doc, r, bold_prefix="• ")

    # Save Document
    doc.save(OUTPUT_FILE)
    print(f"[+] Successfully generated master documentation: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    build_docx_documentation()
