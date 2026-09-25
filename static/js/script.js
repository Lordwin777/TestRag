/**
 * static/js/script.js
 * ===================
 * Vanilla JavaScript Controller for the RAG-Based AI Test Case Generator.
 * Features:
 * - Dual Theme Switcher (Dark / Light) with LocalStorage persistence
 * - Ergonomic Tabbed Navigation for results (Test Cases, RAG Knowledge, AST Analysis, Full View)
 * - Dual Test Case Views (Expanded Cards vs Compact Table)
 * - Quick-jump Navigation & Floating Back-to-Top Button
 * - Keyboard shortcuts (Ctrl+Enter to generate)
 * - Real-time filtering, search, and CSV/JSON exports
 */

// Global Application State
window.currentResultData = null;
window.allTestCases = [];
window.currentTab = 'cases';
window.currentViewMode = 'cards';
window.allCardsExpanded = true;
window.allRAGExpanded = false;

// Sample Code Library for quick testing & demonstration
const CODE_SAMPLES = {
    discount: `def calculate_discount(price, discount):
    """Calculates discounted price with range and boundary verification."""
    if price < 0:
        return "Invalid price"

    if discount < 0 or discount > 100:
        return "Invalid discount"

    final_price = price - (price * discount / 100)
    return final_price`,

    auth: `def authenticate_user(username, password, attempts=0):
    """Defensive authentication function with lockout and credential validation."""
    if attempts >= 3:
        raise PermissionError("Account locked due to excessive failed attempts")

    if not username or len(username.strip()) < 3:
        return {"status": "error", "message": "Invalid username format"}

    if len(password) < 8 or len(password) > 64:
        return {"status": "error", "message": "Password must be 8-64 characters"}

    if username == "admin" and password == "SecurePass123!":
        return {"status": "success", "token": "session_tok_991823"}

    return {"status": "error", "message": "Invalid credentials"}`,

    array: `def filter_valid_scores(scores, threshold=50):
    """Processes numeric exam scores with loop iteration and edge cases."""
    if scores is None:
        raise ValueError("Scores collection cannot be None")

    passed = []
    for score in scores:
        if score < 0 or score > 100:
            continue
        if score >= threshold:
            passed.append(score)

    return passed`
};

// -----------------------------------------------------------------------------
// Initialization
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initScrollListener();
    checkSystemStatus();
    loadSample("discount");
    updateCharCount();
});

// -----------------------------------------------------------------------------
// Theme Management (Light / Dark)
// -----------------------------------------------------------------------------
function initTheme() {
    const savedTheme = localStorage.getItem("rag-app-theme");
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        // System preference default
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        setTheme(prefersDark ? "dark" : "light");
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    setTheme(newTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("rag-app-theme", theme);

    const label = document.getElementById("theme-label");
    if (label) {
        label.textContent = theme === "dark" ? "Dark" : "Light";
    }
}

// -----------------------------------------------------------------------------
// System Health Status Check
// -----------------------------------------------------------------------------
async function checkSystemStatus() {
    const vectorBadge = document.getElementById("vector-status-badge");
    const vectorText = document.getElementById("vector-status-text");
    const geminiBadge = document.getElementById("gemini-status-badge");
    const geminiText = document.getElementById("gemini-status-text");

    try {
        const res = await fetch("/api/status");
        const data = await res.json();

        // Vector store status
        if (data.faiss_ready) {
            vectorBadge.className = "status-pill status-ok";
            vectorText.textContent = `FAISS Ready (${data.total_chunks} Chunks)`;
        } else {
            vectorBadge.className = "status-pill status-warn";
            vectorText.textContent = "FAISS: Unbuilt";
        }

        // Gemini API key status
        if (data.gemini_api_key_configured) {
            geminiBadge.className = "status-pill status-ok";
            geminiText.textContent = `Gemini: Live (${data.model})`;
        } else {
            geminiBadge.className = "status-pill status-warn";
            geminiText.textContent = "Gemini: Offline (Demo Mode)";
        }
    } catch (err) {
        vectorBadge.className = "status-pill status-warn";
        vectorText.textContent = "Server Offline";
        geminiBadge.style.display = "none";
    }
}

// -----------------------------------------------------------------------------
// Sample Loaders & Textarea Helpers
// -----------------------------------------------------------------------------
function loadSample(key) {
    const codeArea = document.getElementById("code-input");
    const langSelect = document.getElementById("language-select");

    if (CODE_SAMPLES[key]) {
        codeArea.value = CODE_SAMPLES[key];
        langSelect.value = "Python";
        updateLanguageMode();
        updateCharCount();
    }
}

function clearCode() {
    const codeArea = document.getElementById("code-input");
    codeArea.value = "";
    updateCharCount();
    codeArea.focus();
}

function updateCharCount() {
    const code = document.getElementById("code-input").value;
    const charCounter = document.getElementById("char-counter");
    charCounter.textContent = `${code.length.toLocaleString()} characters`;
}

function updateLanguageMode() {
    const lang = document.getElementById("language-select").value;
    const indicator = document.getElementById("code-lang-indicator");
    indicator.textContent = lang.toLowerCase();
}

function handleTextareaKeydown(event) {
    // Ctrl+Enter or Cmd+Enter to run
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        document.getElementById("generate-form").requestSubmit();
    }
}

// -----------------------------------------------------------------------------
// Main Generation Flow (POST /generate)
// -----------------------------------------------------------------------------
async function handleGenerate(event) {
    event.preventDefault();

    const code = document.getElementById("code-input").value.trim();
    if (!code) {
        showAlert("Please enter or paste source code before generating test cases.", "error");
        return;
    }

    const language = document.getElementById("language-select").value;
    const testType = document.getElementById("test-type-select").value;
    const numCases = parseInt(document.getElementById("num-cases-input").value, 10) || 10;

    setGeneratingState(true);
    hideAlert();

    const payload = {
        code: code,
        language: language,
        test_type: testType,
        number_of_test_cases: numCases
    };

    try {
        setPipelineStep(1);
        await sleep(200);

        setPipelineStep(2);
        await sleep(250);

        setPipelineStep(3);

        const response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        setPipelineStep(4);
        await sleep(200);

        setPipelineStep(5);

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.error || "Failed to generate test cases.");
        }

        window.currentResultData = result;
        window.allTestCases = result.data.test_cases || [];

        // Render UI sections
        renderCodeAnalysis(result.code_analysis, result.query);
        renderRAGTransparency(result.retrieved_context);
        renderTestCases(window.allTestCases);
        renderTestCasesTable(window.allTestCases);

        // Update tab badges
        document.getElementById("tab-badge-cases").textContent = window.allTestCases.length;
        document.getElementById("tab-badge-rag").textContent = `${(result.retrieved_context || []).length} Chunks`;

        // Show Results container & activate Test Cases tab by default
        document.getElementById("results-container").style.display = "flex";
        switchResultsTab("cases");

        // Smooth scroll to the results navigation bar
        document.getElementById("results-nav-bar").scrollIntoView({ behavior: "smooth", block: "start" });

        // Update note about generation source
        const sourceNote = document.getElementById("tc-source-note");
        if (result.data.meta && result.data.meta.source) {
            sourceNote.textContent = `Generated via: ${result.data.meta.source} • Augmented with FAISS RAG Context`;
        }

        showAlert(`Successfully generated ${window.allTestCases.length} test cases with RAG! Use the navigation tabs below to inspect results.`, "success");

    } catch (err) {
        console.error("Generation error:", err);
        showAlert(err.message, "error");
    } finally {
        setGeneratingState(false);
    }
}

// -----------------------------------------------------------------------------
// Results Tabs Switching (Smooth Navigation)
// -----------------------------------------------------------------------------
function switchResultsTab(tabName) {
    window.currentTab = tabName;

    // Update active tab button
    const buttons = {
        'cases': document.getElementById("tab-btn-cases"),
        'rag': document.getElementById("tab-btn-rag"),
        'ast': document.getElementById("tab-btn-ast"),
        'all': document.getElementById("tab-btn-all")
    };

    Object.keys(buttons).forEach(k => {
        if (buttons[k]) {
            buttons[k].classList.toggle("active", k === tabName);
        }
    });

    const paneCases = document.getElementById("pane-testcases");
    const paneRag = document.getElementById("pane-rag");
    const paneAst = document.getElementById("pane-ast");

    if (tabName === "all") {
        // Show all sections simultaneously
        paneCases.classList.add("active-pane");
        paneRag.classList.add("active-pane");
        paneAst.classList.add("active-pane");
    } else {
        paneCases.classList.toggle("active-pane", tabName === "cases");
        paneRag.classList.toggle("active-pane", tabName === "rag");
        paneAst.classList.toggle("active-pane", tabName === "ast");
    }
}

function scrollToEditor() {
    const editor = document.getElementById("editor-section");
    if (editor) {
        editor.scrollIntoView({ behavior: "smooth", block: "start" });
        document.getElementById("code-input").focus();
    }
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function initScrollListener() {
    const topBtn = document.getElementById("floating-top-btn");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 400) {
            topBtn.classList.add("visible");
        } else {
            topBtn.classList.remove("visible");
        }
    });
}

// -----------------------------------------------------------------------------
// View Mode: Cards vs Table
// -----------------------------------------------------------------------------
function setViewMode(mode) {
    window.currentViewMode = mode;

    const cardsBtn = document.getElementById("view-cards-btn");
    const tableBtn = document.getElementById("view-table-btn");
    const cardsContainer = document.getElementById("test-cases-list");
    const tableContainer = document.getElementById("test-cases-table-wrapper");

    if (mode === "table") {
        cardsBtn.classList.remove("active");
        tableBtn.classList.add("active");
        cardsContainer.style.display = "none";
        tableContainer.style.display = "block";
    } else {
        tableBtn.classList.remove("active");
        cardsBtn.classList.add("active");
        tableContainer.style.display = "none";
        cardsContainer.style.display = "flex";
    }
}

function toggleAllTestCases() {
    window.allCardsExpanded = !window.allCardsExpanded;
    const cards = document.querySelectorAll(".test-case-card");
    cards.forEach(c => {
        if (window.allCardsExpanded) {
            c.classList.remove("tc-card-collapsed");
        } else {
            c.classList.add("tc-card-collapsed");
        }
    });
    document.getElementById("btn-toggle-all-tc").textContent = window.allCardsExpanded ? "Collapse All" : "Expand All";
}

function toggleCard(cardHeader) {
    const card = cardHeader.closest(".test-case-card");
    card.classList.toggle("tc-card-collapsed");
}

function toggleAllRAGItems() {
    window.allRAGExpanded = !window.allRAGExpanded;
    const items = document.querySelectorAll(".rag-item");
    items.forEach(it => {
        if (window.allRAGExpanded) {
            it.classList.add("open");
        } else {
            it.classList.remove("open");
        }
    });
}

// -----------------------------------------------------------------------------
// Rendering: Code Structural Analysis
// -----------------------------------------------------------------------------
function renderCodeAnalysis(analysis, query) {
    document.getElementById("stat-functions").textContent = analysis.raw_counts.functions;
    document.getElementById("stat-conditions").textContent = analysis.raw_counts.conditions;
    document.getElementById("stat-loops").textContent = analysis.raw_counts.loops;
    document.getElementById("stat-exceptions").textContent = analysis.raw_counts.exceptions;

    const fnNames = (analysis.functions || []).map(f => f.name).join(", ") || "None";
    document.getElementById("detail-functions").textContent = `Names: ${fnNames}`;

    const condCount = (analysis.conditions || []).length;
    document.getElementById("detail-conditions").textContent = `${condCount} branch condition(s) discovered`;

    const loopCount = (analysis.loops || []).length;
    document.getElementById("detail-loops").textContent = `${loopCount} iteration construct(s)`;

    const excCount = (analysis.exceptions || []).length;
    document.getElementById("detail-exceptions").textContent = `${excCount} error handler(s)`;

    document.getElementById("analysis-summary-badge").textContent = `${analysis.language} AST Verified`;

    const condList = document.getElementById("conditions-list");
    condList.innerHTML = "";
    if (analysis.conditions && analysis.conditions.length > 0) {
        analysis.conditions.forEach(cond => {
            const li = document.createElement("li");
            li.className = "tag-item";
            li.textContent = cond;
            condList.appendChild(li);
        });
    } else {
        const li = document.createElement("li");
        li.className = "tag-item";
        li.textContent = "No conditional branches";
        condList.appendChild(li);
    }

    document.getElementById("retrieval-query-display").textContent = query;
}

// -----------------------------------------------------------------------------
// Rendering: RAG Transparency (FAISS Retrieved Context)
// -----------------------------------------------------------------------------
function renderRAGTransparency(retrievedChunks) {
    const container = document.getElementById("rag-items-container");
    const countBadge = document.getElementById("rag-count-badge");
    container.innerHTML = "";

    if (!retrievedChunks || retrievedChunks.length === 0) {
        countBadge.textContent = "0 Chunks Retrieved";
        container.innerHTML = "<p class='text-muted'>No external testing knowledge retrieved.</p>";
        return;
    }

    countBadge.textContent = `${retrievedChunks.length} Chunks Retrieved from FAISS`;

    retrievedChunks.forEach((chunk, index) => {
        const item = document.createElement("div");
        item.className = "rag-item" + (index === 0 ? " open" : "");

        const scorePercent = Math.round(chunk.similarity_score * 100);

        item.innerHTML = `
            <div class="rag-item-header" onclick="toggleAccordion(this)">
                <div class="rag-item-title-group">
                    <span class="rag-score-pill">Similarity: ${chunk.similarity_score} (${scorePercent}%)</span>
                    <span class="rag-topic-name">${escapeHTML(chunk.topic)}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span class="rag-item-meta">Source: <code>${escapeHTML(chunk.file_name)}</code></span>
                    <span class="rag-toggle-icon">&#9660;</span>
                </div>
            </div>
            <div class="rag-item-content">
                <p><strong>Concept Summary:</strong> ${escapeHTML(chunk.summary)}</p>
                <div style="margin-top: 0.75rem; border-top: 1px dashed var(--border-color); padding-top: 0.75rem;">
                    <strong>Retrieved Knowledge & Rules:</strong>
                    <div style="font-family: var(--font-mono); font-size: 0.8rem; margin-top: 0.35rem; color: var(--text-muted);">${escapeHTML(chunk.content)}</div>
                </div>
            </div>
        `;

        container.appendChild(item);
    });
}

function toggleAccordion(headerElement) {
    const parentItem = headerElement.closest(".rag-item");
    parentItem.classList.toggle("open");
}

// -----------------------------------------------------------------------------
// Rendering: Test Cases Cards View
// -----------------------------------------------------------------------------
function renderTestCases(testCases) {
    const container = document.getElementById("test-cases-list");
    container.innerHTML = "";

    document.getElementById("total-tc-count").textContent = window.allTestCases.length;
    document.getElementById("visible-tc-count").textContent = testCases.length;

    if (!testCases || testCases.length === 0) {
        container.innerHTML = `
            <div class="panel" style="text-align: center; padding: 2rem;">
                <p style="color: var(--text-muted); font-size: 0.95rem;">No test cases match the selected filter criteria.</p>
            </div>
        `;
        return;
    }

    testCases.forEach(tc => {
        const card = document.createElement("div");
        card.className = "test-case-card";

        const typeClass = getBadgeClassForType(tc.test_type);
        const prioClass = getPriorityBadgeClass(tc.priority);

        const stepsHtml = (tc.steps || [])
            .map(step => `<li>${escapeHTML(step)}</li>`)
            .join("");

        const inputFormatted = typeof tc.input === "object" 
            ? JSON.stringify(tc.input, null, 2) 
            : String(tc.input);

        const preHtml = (tc.preconditions || [])
            .map(p => `&bull; ${escapeHTML(p)}`)
            .join(" ");

        card.innerHTML = `
            <div class="tc-card-top" onclick="toggleCard(this)" title="Click to collapse / expand this test case">
                <div class="tc-id-title">
                    <span class="tc-id">${escapeHTML(tc.id)}</span>
                    <span class="tc-title">${escapeHTML(tc.title)}</span>
                </div>
                <div class="tc-badges">
                    <span class="badge ${typeClass}">${escapeHTML(tc.test_type)}</span>
                    <span class="badge ${prioClass}">Priority: ${escapeHTML(tc.priority)}</span>
                    <span class="badge badge-info">Severity: ${escapeHTML(tc.severity)}</span>
                </div>
            </div>

            <div class="tc-details">
                <div class="tc-body">
                    <div>
                        <div class="tc-section-title">Target Function</div>
                        <div style="font-family: var(--font-mono); font-weight: 600; color: var(--color-primary); margin-bottom: 0.65rem;">
                            ${escapeHTML(tc.function)}()
                        </div>

                        <div class="tc-section-title">Input Parameters</div>
                        <pre class="tc-code-block">${escapeHTML(inputFormatted)}</pre>

                        ${preHtml ? `
                            <div class="tc-section-title" style="margin-top: 0.65rem;">Preconditions</div>
                            <div style="font-size: 0.78rem; color: var(--text-muted);">${preHtml}</div>
                        ` : ""}
                    </div>

                    <div>
                        <div class="tc-section-title">Execution Steps</div>
                        <ol class="tc-steps-list">
                            ${stepsHtml}
                        </ol>

                        <div class="tc-section-title" style="margin-top: 0.85rem;">Expected Result</div>
                        <div class="tc-expected-box">
                            ${escapeHTML(tc.expected_result)}
                        </div>
                    </div>
                </div>

                <div class="tc-reason-box">
                    <strong>QA Rationale:</strong>
                    <span>${escapeHTML(tc.reason)}</span>
                </div>
            </div>
        `;

        container.appendChild(card);
    });
}

// -----------------------------------------------------------------------------
// Rendering: Test Cases Table View (Compact)
// -----------------------------------------------------------------------------
function renderTestCasesTable(testCases) {
    const tbody = document.getElementById("test-cases-table-body");
    tbody.innerHTML = "";

    if (!testCases || testCases.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">No test cases match filter.</td></tr>`;
        return;
    }

    testCases.forEach(tc => {
        const tr = document.createElement("tr");
        const typeClass = getBadgeClassForType(tc.test_type);
        const prioClass = getPriorityBadgeClass(tc.priority);
        const inputStr = typeof tc.input === "object" ? JSON.stringify(tc.input) : String(tc.input);

        tr.innerHTML = `
            <td><strong class="tc-id">${escapeHTML(tc.id)}</strong></td>
            <td><code>${escapeHTML(tc.function)}()</code></td>
            <td style="font-weight: 600;">${escapeHTML(tc.title)}</td>
            <td><span class="badge ${typeClass}">${escapeHTML(tc.test_type)}</span></td>
            <td><code class="tc-code-block" style="padding: 2px 6px;">${escapeHTML(inputStr)}</code></td>
            <td style="color: var(--color-success); font-weight: 600;">${escapeHTML(tc.expected_result)}</td>
            <td><span class="badge ${prioClass}">${escapeHTML(tc.priority)}</span></td>
            <td><span class="badge badge-info">${escapeHTML(tc.severity)}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function getBadgeClassForType(testType) {
    const t = (testType || "").toLowerCase();
    if (t.includes("pos")) return "badge-positive";
    if (t.includes("neg")) return "badge-negative";
    if (t.includes("bound")) return "badge-boundary";
    if (t.includes("edge")) return "badge-edge-case";
    if (t.includes("except")) return "badge-exception";
    if (t.includes("sec")) return "badge-security";
    if (t.includes("branch") || t.includes("logic")) return "badge-branch";
    return "badge-functional";
}

function getPriorityBadgeClass(priority) {
    const p = (priority || "").toLowerCase();
    if (p === "high") return "badge-prio-high";
    if (p === "low") return "badge-prio-low";
    return "badge-prio-med";
}

// -----------------------------------------------------------------------------
// Interactive Filtering
// -----------------------------------------------------------------------------
function applyFilters() {
    if (!window.allTestCases) return;

    const filterType = document.getElementById("filter-type").value;
    const filterPrio = document.getElementById("filter-priority").value;
    const filterSev = document.getElementById("filter-severity").value;
    const searchKeyword = document.getElementById("filter-search").value.toLowerCase().trim();

    const filtered = window.allTestCases.filter(tc => {
        if (filterType !== "All" && tc.test_type.toLowerCase() !== filterType.toLowerCase()) {
            return false;
        }
        if (filterPrio !== "All" && tc.priority.toLowerCase() !== filterPrio.toLowerCase()) {
            return false;
        }
        if (filterSev !== "All" && tc.severity.toLowerCase() !== filterSev.toLowerCase()) {
            return false;
        }
        if (searchKeyword) {
            const titleMatch = (tc.title || "").toLowerCase().includes(searchKeyword);
            const fnMatch = (tc.function || "").toLowerCase().includes(searchKeyword);
            const reasonMatch = (tc.reason || "").toLowerCase().includes(searchKeyword);
            const inputMatch = JSON.stringify(tc.input || {}).toLowerCase().includes(searchKeyword);
            if (!titleMatch && !fnMatch && !reasonMatch && !inputMatch) {
                return false;
            }
        }
        return true;
    });

    renderTestCases(filtered);
    renderTestCasesTable(filtered);
}

// -----------------------------------------------------------------------------
// Export Handlers
// -----------------------------------------------------------------------------
async function exportData(format) {
    if (!window.currentResultData || !window.allTestCases.length) {
        showAlert("No test cases available to export.", "error");
        return;
    }

    try {
        const endpoint = format === "csv" ? "/export/csv" : "/export/json";
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                test_cases: window.allTestCases,
                data: window.currentResultData.data
            })
        });

        if (!response.ok) {
            throw new Error(`Export ${format.toUpperCase()} failed.`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = `test_cases_${Date.now()}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        showAlert(`Exported test cases as ${format.toUpperCase()} successfully!`, "success");
    } catch (err) {
        showAlert(err.message, "error");
    }
}

function copyTestCasesJSON() {
    if (!window.currentResultData) {
        showAlert("No test cases to copy.", "error");
        return;
    }

    const jsonStr = JSON.stringify(window.currentResultData.data, null, 2);
    navigator.clipboard.writeText(jsonStr).then(() => {
        showAlert("Validated Test Cases JSON copied to clipboard!", "success");
    }).catch(() => {
        showAlert("Could not access clipboard.", "error");
    });
}

// -----------------------------------------------------------------------------
// Helper UI Utilities
// -----------------------------------------------------------------------------
function setGeneratingState(isGenerating) {
    const btn = document.getElementById("btn-submit");
    const btnText = btn.querySelector(".btn-text");
    const spinner = document.getElementById("btn-spinner");
    const stepper = document.getElementById("pipeline-stepper");

    if (isGenerating) {
        btn.disabled = true;
        btnText.textContent = "Executing RAG Pipeline...";
        spinner.style.display = "inline-block";
        stepper.style.display = "flex";
    } else {
        btn.disabled = false;
        btnText.textContent = "Generate Test Cases (RAG + AI)";
        spinner.style.display = "none";
    }
}

function setPipelineStep(activeStepNumber) {
    for (let i = 1; i <= 5; i++) {
        const stepEl = document.getElementById(`step-${i}`);
        if (!stepEl) continue;
        stepEl.classList.remove("active", "completed");
        if (i < activeStepNumber) {
            stepEl.classList.add("completed");
        } else if (i === activeStepNumber) {
            stepEl.classList.add("active");
        }
    }
}

function showAlert(message, type = "error") {
    const banner = document.getElementById("alert-banner");
    banner.className = `alert-banner alert-${type}`;
    banner.textContent = message;
    banner.style.display = "flex";
}

function hideAlert() {
    const banner = document.getElementById("alert-banner");
    banner.style.display = "none";
}

function escapeHTML(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
