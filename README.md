# ATLAS: Enterprise Knowledge & Decision Intelligence Platform

ATLAS is a production-grade, multi-source enterprise AI decision intelligence platform designed to bridge structured corporate databases and unstructured document repositories.

Instead of operating as a simplistic document chatbot, ATLAS orchestrates a **Rust-powered ingestion & SQL guard engine** alongside a **LangGraph 5-agent decision graph (Gemini 2.5 Flash)** to analyze complex enterprise questions requiring quantitative database verification and qualitative policy grounding.

---

## Architecture Overview

```
                      ┌──────────────────────────────────────────────┐
                      │              Enterprise User                 │
                      └──────────────────────┬───────────────────────┘
                                             │ HTTP / Web Client
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │    AI Orchestrator (Python / FastAPI)        │
                      │               [Port 8002]                    │
                      │                                              │
                      │   ┌──────────────────────────────────────┐   │
                      │   │       LangGraph Decision Graph       │   │
                      │   │  - Query Planning Agent              │   │
                      │   │  - Document Retrieval Agent (Qdrant) │   │
                      │   │  - SQL Query Agent                   │   │
                      │   │  - Evidence Validation Agent         │   │
                      │   │  - Answer Generation Agent           │   │
                      │   └──────────────────┬───────────────────┘   │
                      └──────────────────────┼───────────────────────┘
                                             │
                       Protected HTTP Call   │ (Controlled NL-to-SQL AST Check)
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │     ATLAS Core Engine (Rust / Axum)          │
                      │               [Port 8080]                    │
                      │                                              │
                      │   ├── Document Ingestion & Tokenizer         │
                      │   ├── SHA-256 Cryptographic Deduplication    │
                      │   ├── Sliding-Window Chunking (UTF-8 safe)   │
                      │   └── AST-Level SQL Guard (Read-Only Safety) │
                      └──────────────┬───────────────────────┬───────┘
                                     │                       │
                                     ▼                       ▼
                         ┌───────────────────────┐   ┌───────────────┐
                         │      PostgreSQL       │   │ Qdrant Vector │
                         │   (Structured DB)     │   │     Store     │
                         └───────────────────────┘   └───────────────┘
```

---

## Key Platform Capabilities

### 1. Rust High-Performance Core Engine (`services/core-engine`)
- **Async Axum Web Server**: Built on `tokio` for non-blocking I/O and predictable sub-millisecond API response times.
- **Cryptographic Document Deduplication**: Real-time SHA-256 fingerprinting prevents redundant embeddings and vector bloat.
- **Sliding-Window UTF-8 Chunking**: Preserves character and word boundaries to eliminate tokenization artifacts.
- **Strict AST-Level SQL Guard**: Intercepts LLM-generated SQL; rejects all non-`SELECT`/`WITH` statements (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `ALTER`) and multi-statement injection attempts before touching PostgreSQL.

### 2. Multi-Agent AI Orchestrator (`services/ai-orchestrator`)
- **LangGraph StateGraph**:
  - `Query Planning Agent`: Decomposes user questions into structured SQL queries and unstructured document search vectors.
  - `Document Retrieval Agent`: Vector similarity search against Qdrant with access-level filtering.
  - `SQL Query Agent`: Bridges to the Rust Core Engine for validated read-only SQL execution.
  - `Evidence Validation Agent`: Cross-checks structured numerical data against documented memos.
  - `Answer Generation Agent`: Produces grounded executive synthesis with bracketed citations `[1]`, `[2]`.
- **Cost & Latency Telemetry**: Real-time token tracking and pricing accounting based on official Gemini schedules.

### 3. Enterprise Frontend (`services/web`)
- Minimalist, high-density enterprise dashboard.
- Real-time 5-agent execution timeline with status indicators.
- Interactive SQL Sandbox with AST guard validation warnings.
- Citation tracking tray mapping synthesis claims directly to database tables and PDF chunk offsets.

---

## Project Structure

```
atlas/
├── .github/workflows/
│   └── ci.yml                     # GitHub Actions CI for Rust & Python
├── deployments/
│   └── docker-compose.yml         # Multi-container local orchestration
├── services/
│   ├── core-engine/               # Rust Axum Core Backend
│   │   ├── Cargo.toml
│   │   ├── Dockerfile
│   │   ├── src/
│   │   │   ├── config.rs          # Strongly typed environment config
│   │   │   ├── ingestion.rs       # SHA-256 & sliding-window chunker
│   │   │   ├── models.rs          # Core domain structs (Serde)
│   │   │   ├── sql_guard.rs       # Strict AST-level read-only validator
│   │   │   ├── lib.rs
│   │   │   └── main.rs            # Axum router & endpoints
│   │   └── tests/
│   │       └── engine_tests.rs    # Unit tests for chunking, hashing & SQL guard
│   ├── ai-orchestrator/           # Python LangGraph & Gemini Layer
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── core/              # Config & Gemini LLM client
│   │   │   ├── agents/            # 5-Agent Decision Graph
│   │   │   └── main.py            # FastAPI service (:8002)
│   │   └── tests/
│   │       └── test_decision_graph.py
│   └── web/                       # Enterprise Management Interface
│       └── index.html
└── README.md
```

---

## Quickstart Guide

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose
- Or locally:
  - Rust 1.80+ (`cargo`)
  - Python 3.11+
  - PostgreSQL & Qdrant

### Running with Docker Compose

```powershell
docker compose -f deployments/docker-compose.yml up --build
```

Access endpoints:
- **Web UI**: `http://localhost:3000`
- **Rust Core Engine**: `http://localhost:8080/health`
- **AI Orchestrator**: `http://localhost:8002/health`
- **Qdrant Vector DB**: `http://localhost:6333/dashboard`

### Running Locally (Development Mode)

#### 1. Start Rust Core Engine
```powershell
cd services/core-engine
cargo run
```

#### 2. Start Python AI Orchestrator
```powershell
cd services/ai-orchestrator
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GEMINI_API_KEY="your-gemini-api-key"
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

---

## Verification & Testing

### Rust Core Engine Tests
```powershell
cd services/core-engine
cargo test
```
*Validates: Document hashing, sliding window chunking, and SQL Guard rejection of mutation tokens.*

### Python AI Orchestrator Tests
```powershell
cd services/ai-orchestrator
.\venv\Scripts\pytest.exe -v
```
*Validates: Multi-source state flow across all 5 agents, citation grounding, and cost accounting.*
