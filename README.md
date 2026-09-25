<div align="center">

# 🧪⚡ RAG-Based AI Test Case Generator
### *Automated Software Testing & Verification Powered by Retrieval-Augmented Generation (RAG) and Google Gemini*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![FAISS](https://img.shields.io/badge/Vector%20DB-FAISS%20CPU-00599C?style=for-the-badge&logo=meta&logoColor=white)](https://github.com/facebookresearch/faiss)
[![Google Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%20API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

<br/>

**"A Retrieval-Augmented Generative AI system that analyzes source code, retrieves relevant software-testing knowledge using semantic search, and generates structured software test cases using a Large Language Model."**

[Key Features](#-key-features) •
[System Architecture](#-system-architecture) •
[Live Walkthrough](#-live-walkthrough-example) •
[Quick Start](#-quick-start)

</div>

---

## 📑 Table of Contents

- [🌟 Key Features](#-key-features)
- [🎯 Problem Statement & Motivation](#-problem-statement--motivation)
- [🧠 What is RAG and Why is it Used?](#-what-is-rag-and-why-is-it-used)
- [🏛️ System Architecture](#-system-architecture)
- [🔄 Detailed Pipeline & Data Flow](#-detailed-pipeline--data-flow)
- [🛠️ Technology Stack](#-technology-stack)
- [📚 Local Testing Knowledge Base](#-local-testing-knowledge-base)
- [🧬 Embedding Pipeline & Vector Store](#-embedding-pipeline--vector-store)
- [🔍 AST Code Analyzer](#-ast-code-analyzer)
- [🤖 Prompt Engine & Gemini LLM Integration](#-prompt-engine--gemini-llm-integration)
- [🎨 Modern Web Dashboard](#-modern-web-dashboard)
- [🚀 Quick Start (One-Click Launcher)](#-quick-start-one-click-launcher)
- [💻 Manual Installation & Setup](#-manual-installation--setup)
- [🧪 Full Pipeline Walkthrough Example](#-full-pipeline-walkthrough-example)
- [📤 Export Options (CSV & JSON)](#-export-options-csv--json)
- [🔒 Security & Safe Execution Policy](#-security--safe-execution-policy)
- [📂 Project Directory Tree](#-project-directory-tree)

---

## 🌟 Key Features

* **Abstract Syntax Tree (AST) Parsing**: Deep static analysis extracting functions, arguments, return statements, conditional branches (`if`, `elif`), comparison boundaries (`<`, `<=`, `>`, `>=`, `==`), loops (`for`, `while`), and exception handlers (`try`, `except`, `raise`).
* **Retrieval-Augmented Generation (RAG)**: Synthesizes code findings into an intelligent search query and retrieves formal QA testing methodologies from a local knowledge base.
* **FAISS Vector Database**: Fast, dense vector similarity search using `faiss.IndexFlatIP` ($L_2$-normalized inner product = exact Cosine Similarity).
* **Asymmetric Embedding Engine**: Clean architectural separation between **Document Embeddings** (`RETRIEVAL_DOCUMENT`) and runtime **Query Embeddings** (`RETRIEVAL_QUERY`).
* **Google Gemini LLM Integration**: Uses the official `google-genai` SDK (`gemini-2.5-flash` / `gemini-3.8-flash`) with structured output enforcement.
* **Zero-Fail Offline Demonstration Mode**: Works 100% out-of-the-box even without an active internet connection or API key for offline student viva presentations.
* **Dual Display Modes (Cards vs. Table View)**: Inspect detailed test steps, inputs, and QA rationale in Cards View, or review 20+ test cases at a glance in a compact, responsive Table View.
* **Ergonomic Sticky Navigation**: Dedicated tabs for **Test Cases**, **RAG Knowledge**, **AST Analysis**, and **Full View** with an *"↑ Edit Code"* quick-jump button.
* **Light / Dark Mode**: Built-in theme switcher with automatic OS preference detection and `localStorage` persistence.
* **Multi-Format Export**: One-click RFC 4180 CSV export and validated JSON export.
* **Strict Static Safety**: **Zero arbitrary code execution** (`exec()` and `eval()` are strictly banned).

---

## 🎯 Problem Statement & Motivation

Traditional software testing suffers from high human cognitive overhead, missed edge cases, and off-by-one errors. 

When developers prompt standard generic LLMs:
1. **Hallucination**: The LLM often invents external databases, network calls, or non-existent parameters.
2. **Lack of QA Rigor**: The LLM guesses random test inputs rather than applying formal testing heuristics (e.g. failing to compute exact Boundary Value Analysis thresholds $min-1, min, max, max+1$).
3. **Unstructured Output**: Freeform conversational text cannot be programmatically validated or imported into automated testing frameworks.

**Our Solution**: Intercept user code with an AST analyzer, retrieve relevant QA knowledge via FAISS, and ground the LLM with both the **source code** and the **retrieved testing guidelines**.

---

## 🧠 What is RAG and Why is it Used?

**Retrieval-Augmented Generation (RAG)** is an AI framework that augments an LLM's prompt with retrieved domain-specific knowledge before generating an answer.

```text
               Without RAG (Naive Prompting):
User Code ──────────────────────────► LLM ─────────► Generic / Hallucinated Tests

                 With RAG (Our System):
User Code ──► Code Analysis ──► Semantic Search ──► FAISS Vector DB
                                                           │
                                                           ▼
User Code + AST Analysis + Retrieved Knowledge ────► LLM ──► Grounded Test Cases
```

### Why RAG is Essential for Automated Testing:
If a user submits:
```python
if discount < 0 or discount > 100:
```
The RAG pipeline retrieves **Boundary Value Analysis (BVA)** and **Equivalence Partitioning (EP)**. Gemini receives these exact heuristics in its context window and generates tests specifically targeting:
* Exact lower bound: `discount = 0` (Valid edge)
* Just below lower bound: `discount = -1` (Invalid error edge)
* Exact upper bound: `discount = 100` (Valid edge)
* Just above upper bound: `discount = 101` (Invalid error edge)

---

## 🏛️ System Architecture

```text
                                  ┌──────────────────────────┐
                                  │      USER / BROWSER      │
                                  └─────────────┬────────────┘
                                                │ (HTTP POST /generate)
                                                ▼
                                  ┌──────────────────────────┐
                                  │      FLASK BACKEND       │
                                  └─────────────┬────────────┘
                                                │
                                                ▼
                                  ┌──────────────────────────┐
                                  │   REQUEST VALIDATOR      │
                                  │ (Length, Type, Security) │
                                  └─────────────┬────────────┘
                                                │
                                                ▼
                                  ┌──────────────────────────┐
                                  │      CODE ANALYZER       │
                                  │   (Python AST Parser)    │
                                  └──────┬─────────────┬─────┘
                                         │             │
                    Functions / Logic ◄──┘             └──► Synthesized Query
                    Branches / Bounds                              │
                                                                   ▼
                                                       ┌────────────────────────┐
                                                       │   EMBEDDING SERVICE    │
                                                       │ (Query Embedding: 768d)│
                                                       └───────────┬────────────┘
                                                                   │
                                                                   ▼
                                                       ┌────────────────────────┐
                                                       │  FAISS VECTOR DATABASE │
                                                       │    (vector_store/)     │
                                                       └───────────┬────────────┘
                                                                   │
                                                       Top-K Knowledge Chunks
                                                                   │
                                                                   ▼
                                  ┌─────────────────────────────────────────────┐
                                  │            RAG CONTEXT ASSEMBLY             │
                                  │  Code + AST + Retrieved Knowledge + Rules   │
                                  └─────────────────────┬───────────────────────┘
                                                        │
                                                        ▼
                                  ┌─────────────────────────────────────────────┐
                                  │              GOOGLE GEMINI LLM              │
                                  │             (google-genai SDK)              │
                                  └─────────────────────┬───────────────────────┘
                                                        │
                                                        ▼
                                  ┌─────────────────────────────────────────────┐
                                  │         RESPONSE JSON VALIDATOR             │
                                  │    (Fence Stripping & Schema Check)         │
                                  └─────────────────────┬───────────────────────┘
                                                        │
                                                        ▼
                                  ┌─────────────────────────────────────────────┐
                                  │            MODERN WEB DASHBOARD             │
                                  │  (Cards/Table, Badges, Accordion, Filters)  │
                                  └──────┬───────────────────────────────┬──────┘
                                         │                               │
                                         ▼                               ▼
                                  CSV Download                      JSON Download
```

---

## 🔄 Detailed Pipeline & Data Flow

| Stage | Component | Action | Output |
|---|---|---|---|
| **1. Ingestion** | `app.py` | Receives source code & options via `/generate` | Validated payload |
| **2. AST Parsing** | `services/code_analyzer.py` | Inspects syntax tree without execution | Functions, Conditions, Loops, Exceptions |
| **3. Query Synthesis** | `services/code_analyzer.py` | Creates domain-rich retrieval tokens | Clean search query string |
| **4. Vectorization** | `services/embedding_service.py` | Computes $768$-dimensional $L_2$-normalized vector | Query vector $\vec{q} \in \mathbb{R}^{768}$ |
| **5. FAISS Search** | `services/rag_service.py` | Searches `vector_store/index.faiss` | Top-5 relevant testing chunks + scores |
| **6. Augmentation** | `services/ai_service.py` | Assembles prompt with strict QA constraints | Grounded prompt |
| **7. LLM Inference** | Google Gemini (`gemini-2.5-flash`) | Generates structured test suite | Raw JSON string |
| **8. Validation** | `utils/validators.py` | Strips code fences, checks required keys | Sanitized JSON dictionary |
| **9. Visualization** | Vanilla JS (`script.js`) | Updates AST counters, RAG accordion & cards/table | Interactive UI view |

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Zero frameworks (No React/Tailwind). Custom dark/light mode, CSS grid & flexbox |
| **Backend** | Python 3.10+, Flask 3.x | Lightweight WSGI server, modular service architecture |
| **Vector DB** | FAISS CPU (`faiss-cpu>=1.8.0`) | Facebook AI Similarity Search `IndexFlatIP` (Cosine Similarity) |
| **Embeddings** | Dual-Mode Embedding Engine | Google GenAI (`text-embedding-004`) + Local 768-dim offline semantic vectorizer |
| **LLM Engine** | Google Gemini API | Official `google-genai>=2.0.0` SDK (`gemini-2.5-flash` / `gemini-3.8-flash`) |
| **Code Parser** | Python `ast` Standard Library | Abstract Syntax Tree traversal using `ast.NodeVisitor` |
| **Data Format** | JSON & CSV | Strict JSON schema output & RFC 4180 CSV export |

---

## 📚 Local Testing Knowledge Base

Located in `knowledge_base/`, containing 13 structured, expert-written reference documents:

<details>
<summary><strong>Click to view all 13 knowledge base topics</strong></summary>

1. `functional_testing.txt`: Validation of core business rules and calculation logic.
2. `positive_testing.txt`: Happy path testing using standard, well-formed input data.
3. `negative_testing.txt`: Fault injection, error message validation, and unhandled crash prevention.
4. `boundary_value_analysis.txt`: Tests values at $min-1, min, min+1, max-1, max, max+1$.
5. `equivalence_partitioning.txt`: Splits input domain into valid and invalid classes.
6. `decision_table_testing.txt`: Complex compound boolean logic truth tables.
7. `state_transition_testing.txt`: Finite state machines, status lifecycles, and invalid transitions.
8. `edge_case_testing.txt`: Empty collections, null/zero values, extreme bounds, and unicode inputs.
9. `exception_testing.txt`: Validation of `try/except/raise` clauses and proper error propagation.
10. `unit_testing.txt`: Isolated component testing and deterministic assertions.
11. `branch_testing.txt`: 100% white-box branch coverage (ensuring every condition evaluates $True$ and $False$).
12. `loop_testing.txt`: Zero iterations, single iteration, multi-iterations, and termination checks.
13. `security_testing.txt`: Defensive verification (directory traversal prevention, input sanitization, token checks).
</details>

---

## 🧬 Embedding Pipeline & Vector Store

* **Vector Dimension**: $768$ dimensions.
* **Metric**: Cosine Similarity via Inner Product:
  $$\text{Cosine Similarity} = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2} = \vec{u} \cdot \vec{v} \quad (\text{since } \|\vec{u}\|_2 = \|\vec{v}\|_2 = 1.0)$$
* **Separation of Document vs. Query**:
  - `get_document_embedding(text)`: Used during indexing with `RETRIEVAL_DOCUMENT` task semantics.
  - `get_query_embedding(query)`: Used at runtime with `RETRIEVAL_QUERY` task semantics and query normalization.

---

## 🔍 AST Code Analyzer

The analyzer in `services/code_analyzer.py` extracts structural features without executing untrusted code:

```python
# Sample AST Extraction output:
{
    "language": "Python",
    "functions": [
        {"name": "calculate_discount", "parameters": ["price", "discount"]}
    ],
    "conditions": [
        "price < 0", 
        "discount < 0 or discount > 100"
    ],
    "boundary_comparisons": [
        "price < 0", 
        "discount < 0", 
        "discount > 100"
    ],
    "loops": [],
    "exceptions": []
}
```

---

## 🤖 Prompt Engine & Gemini LLM Integration

The prompt engine injects four pillars of grounded context:
1. **Source Code**: The exact implementation under test.
2. **AST Analysis**: The extracted functions, parameters, and conditional boundaries.
3. **Retrieved Knowledge**: The Top-5 knowledge chunks retrieved from FAISS.
4. **User Preferences**: Selected test type category and target count.

### Strict JSON Output Schema:
```json
{
  "analysis": {
    "language": "Python",
    "summary": "Calculates discounted price and enforces price/discount boundaries.",
    "functions_found": 1,
    "conditions_found": 2,
    "loops_found": 0,
    "exceptions_found": 0
  },
  "retrieved_knowledge": [
    {
      "topic": "Boundary Value Analysis (BVA)",
      "relevance": "Used to test exact discount percentage bounds 0 and 100."
    }
  ],
  "test_cases": [
    {
      "id": "TC001",
      "function": "calculate_discount",
      "title": "Calculate standard discount on normal price",
      "test_type": "Positive",
      "input": { "price": 100, "discount": 10 },
      "preconditions": ["Function is callable"],
      "steps": ["Call calculate_discount(100, 10)", "Verify return value"],
      "expected_result": "90.0",
      "priority": "High",
      "severity": "Medium",
      "reason": "Verifies normal happy path computation."
    }
  ]
}
```

---

## 🎨 Modern Web Dashboard

* **Sticky Results Navigation**: Dedicated tabs for **Test Cases**, **RAG Knowledge**, **AST Analysis**, and **Full View**.
* **Dual View (Cards vs Table)**: Switch between detailed cards or a compact data table.
* **Interactive Live Filters**: Filter instantly by Type, Priority, Severity, or keyword search.
* **Light / Dark Mode**: Seamless toggle with persistent storage.
* **Quick Presets**: Instant load buttons for Discount Calculator, User Authenticator, and Array Filter.
* **Floating Jump Button**: Smoothly scroll back to the code editor from anywhere on the page.

---

## 🚀 Quick Start (One-Click Launcher)

### For Windows:
Simply **double-click** the included batch script:
```cmd
run.bat
```
*It automatically checks Python, verifies `.env`, builds the FAISS vector database if missing, starts Flask, and opens `http://127.0.0.1:5000` in your default browser!*

---

## 💻 Manual Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/AI-Test-Case-Generator.git
cd AI-Test-Case-Generator
```

### 2. Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your settings:
```env
# Optional: Add your Gemini API Key (runs in Demo mode if empty)
GEMINI_API_KEY=your_gemini_api_key_here

EMBEDDING_MODE=local
TOP_K=5
GEMINI_MODEL=gemini-2.5-flash
PORT=5000
DEBUG=True
```

### 5. Build the FAISS Vector Database
```bash
python scripts/build_vector_store.py
```

### 6. Run the Application
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 🧪 Full Pipeline Walkthrough Example

### 1. Input Code:
```python
def calculate_discount(price, discount):
    if price < 0:
        return "Invalid price"
    if discount < 0 or discount > 100:
        return "Invalid discount"
    final_price = price - (price * discount / 100)
    return final_price
```

### 2. AST Analysis Extracted:
* Function: `calculate_discount(price, discount)`
* Conditions: `price < 0`, `discount < 0 or discount > 100`
* Boundaries: `0`, `100`

### 3. FAISS Retrieval (Top 5 Chunks):
1. **Branch and Condition Testing** *(Similarity: 0.6951)*
2. **Negative Testing** *(Similarity: 0.6340)*
3. **Boundary Value Analysis (BVA)** *(Similarity: 0.5896)*
4. **Equivalence Partitioning (EP)** *(Similarity: 0.5779)*
5. **Functional Testing** *(Similarity: 0.5138)*

### 4. Generated Test Suite:
* `TC001`: Positive — Normal 10% discount (`price=100, discount=10` $\rightarrow$ `90.0`)
* `TC002`: Boundary — Lower threshold 0% (`price=100, discount=0` $\rightarrow$ `100.0`)
* `TC003`: Boundary — Upper threshold 100% (`price=100, discount=100` $\rightarrow$ `0.0`)
* `TC004`: Negative — Negative price rejection (`price=-10, discount=10` $\rightarrow$ `"Invalid price"`)
* `TC005`: Negative — Exceeding 100% discount (`price=100, discount=105` $\rightarrow$ `"Invalid discount"`)
* `TC006`: Negative — Negative discount rejection (`price=100, discount=-5` $\rightarrow$ `"Invalid discount"`)
* `TC007`: Edge Case — Zero price item (`price=0, discount=20` $\rightarrow$ `0.0`)

---

## 📤 Export Options (CSV & JSON)

* **Copy JSON**: Copies validated JSON payload directly to the clipboard.
* **Export CSV**: Downloads RFC 4180 compliant CSV file with columns:
  `ID, Function, Title, Test Type, Input, Preconditions, Steps, Expected Result, Priority, Severity, Reason`.
* **Export JSON**: Downloads complete structured report including AST statistics and RAG context.

---

## 🔒 Security & Safe Execution Policy

* **No Code Execution**: The application parses code strictly using `ast.parse()`. Submitted code is never executed via `exec()` or `eval()`.
* **Input Rate & Size Limits**: Maximum code length is restricted to $50\text{ KB}$ to prevent memory exhaustion attacks.
* **Defensive Knowledge Only**: Security testing documents cover defensive validation (path traversal sanitization, token checks) without exploit instructions.
* **API Key Protection**: API keys are isolated on the server side in `.env` and never leaked to the client browser.

---

## 📂 Project Directory Tree

```text
AI-Test-Case-Generator/
├── app.py                         # Flask web application & REST API endpoints
├── run.bat                        # Windows one-click launcher
├── requirements.txt               # Dependencies
├── .env                           # Environment configurations
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── README.md                      # Complete project documentation
│
├── knowledge_base/                # 13 software testing domain knowledge documents
│   ├── functional_testing.txt
│   ├── positive_testing.txt
│   ├── negative_testing.txt
│   ├── boundary_value_analysis.txt
│   ├── equivalence_partitioning.txt
│   ├── decision_table_testing.txt
│   ├── state_transition_testing.txt
│   ├── edge_case_testing.txt
│   ├── exception_testing.txt
│   ├── unit_testing.txt
│   ├── branch_testing.txt
│   ├── loop_testing.txt
│   └── security_testing.txt
│
├── vector_store/                  # Serialized FAISS vector index & metadata
│   ├── index.faiss                # FAISS IndexFlatIP (Cosine Similarity)
│   └── metadata.json              # Chunks text, tags, and topic mappings
│
├── services/
│   ├── code_analyzer.py           # Python AST parser & query synthesizer
│   ├── embedding_service.py       # Asymmetric Document vs. Query embedding engine
│   ├── rag_service.py             # FAISS Top-K vector similarity search
│   └── ai_service.py              # Augmented prompt engine & Gemini LLM client
│
├── utils/
│   ├── validators.py              # Request limits & AI response JSON sanitization
│   └── exporters.py               # RFC 4180 CSV & JSON report generators
│
├── scripts/
│   └── build_vector_store.py      # FAISS vector database builder
│
├── templates/
│   └── index.html                 # Modern responsive HTML5 dashboard
│
├── static/
│   ├── css/
│   │   └── style.css              # Custom dual-theme CSS stylesheet
│   └── js/
│       └── script.js              # Vanilla JS frontend controller & live filters
│
├── tests/                         # Integration test suites
│   ├── test_analyzer.py           # AST analysis tests
│   ├── test_rag.py                # FAISS retrieval verification
│   └── test_full_pipeline.py      # Full integration test suite (6 passing suites)
│
└── exports/                       # Target directory for exported test artifacts
```
