# MemoryGraph 🧠

> A conversational AI backend that **remembers everything** — using a Neo4j Knowledge Graph + MySQL to give your chatbot long-term, queryable memory.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129-009688?style=flat-square&logo=fastapi&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-GraphRAG-008CC1?style=flat-square&logo=neo4j&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-FF6F00?style=flat-square)
![License](https://img.shields.io/badge/License-Apache%202.0-green?style=flat-square)

---

## What is MemoryGraph?

Most chatbots forget everything the moment a session ends. **MemoryGraph** solves this by combining two databases:

| Layer | Database | Purpose |
|---|---|---|
| **Short-term** | MySQL | Stores raw message history per session |
| **Long-term** | Neo4j | Stores a Knowledge Graph of entities, facts, and relationships extracted from conversations |

Every 10 messages, the agent automatically pipelines recent conversation into a **Neo4j Knowledge Graph**. After 10 total messages, a **Graph RAG tool** becomes available to the LangGraph agent — letting it semantically query everything it has ever learned about the user.

---

## Architecture Overview

```
User Request (HTTP)
       │
       ▼
  FastAPI Server
       │
       ├──▶ MySQL (chat history / session store)
       │         └── last N messages → short-term context
       │
       ├──▶ LangGraph Agent (ChatOllama LLM)
       │         ├── < 10 messages: basic chat with one-question profiling
       │         └── ≥ 10 messages: + chat_history_tool (Graph RAG)
       │
       └──▶ Neo4j (Knowledge Graph)
                 ├── SimpleKGPipeline builds graph from conversation text
                 ├── VectorCypherRetriever for semantic retrieval
                 └── GraphRAG generates grounded answers
```

### Key Design Decisions

- **Dual-database memory**: MySQL handles fast, ordered retrieval; Neo4j handles semantic, relationship-aware querying.
- **Automatic graph refresh**: Every 10 messages the latest 10 are fed into the KG pipeline, keeping the graph current without manual triggers.
- **Tool-augmented agent**: Below the threshold the agent is a lean conversational profiler; above it a full RAG-capable agent. The switch is seamless.
- **Session isolation**: Each session gets its own Neo4j database (named by `session_id`), keeping memories fully scoped per user.

---

## Project Structure

```
sethuram2003-memorygraph/
├── src/
│   ├── main.py                          # FastAPI app, lifespan, CORS, routing
│   ├── api/
│   │   └── routes/
│   │       ├── HealthCheck.py           # GET  /health
│   │       ├── ClearDB.py               # DELETE /neo4j-clear-database
│   │       ├── RagQuery.py              # PUT  /neo4j-rag-query
│   │       ├── TestEndpoint.py          # POST /neo4j-pipeline-kg
│   │       └── CustomLangGraphTesting.py# POST /dynamic-kg-query  ← main endpoint
│   └── core/
│       ├── agent_logic/
│       │   ├── agent.py                 # LangGraph agent + memory orchestration
│       │   └── prompts.py               # System prompts (basic + RAG-augmented)
│       ├── mysql_database/
│       │   ├── mysql_manager.py         # Full CRUD: sessions, messages
│       │   └── mysql_service.py         # Singleton service wrapper
│       └── neo4j_database/
│           ├── neo4j_manager.py         # KG pipeline + RAG query logic
│           ├── neo4j_service.py         # Singleton service wrapper
│           ├── prompts.py               # RAG template
│           └── schema.py               # Graph schema (nodes, relationships, patterns)
├── static/
│   └── index.html                       # Built-in chat UI (served at /)
├── TestData/
│   └── ChatTest_1.txt                   # Sample conversation for testing
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── .env                                 # (you create this — see below)
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended — runs everything)
- **Or**, if running locally without Docker:
  - Python 3.12+
  - MySQL 8.0 running locally
  - Neo4j 5+ running locally
  - [Ollama](https://ollama.ai/) with your chosen models pulled

---

## Quick Start (Docker — Recommended)

### 1. Clone the repository

```bash
git clone https://github.com/sethuram2003/memorygraph.git
cd memorygraph
```

### 2. Create your `.env` file

Create a file named `.env` in the project root:

```env
# ── Neo4j ──────────────────────────────────────────────────────
NEO4J_URI=bolt://neo4j_db:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123
NEO4J_DATABASE=memorygraph

# ── MySQL ──────────────────────────────────────────────────────
MYSQL_HOST=mysql_db
MYSQL_USER=root
MYSQL_PASSWORD=root_password
MYSQL_DATABASE=chat_history_db

# ── Ollama ─────────────────────────────────────────────────────
# Make sure these models are pulled on your Ollama host
OLLAMA_LLM_MODEL=kimi-k2:1t-cloud
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_EMBEDDING_DIMENSION=768
```

> **Note on Ollama:** The app calls Ollama on your host machine. If running inside Docker, point `OLLAMA_HOST` to `http://host.docker.internal:11434` or your Ollama server address.

### 3. Start everything

```bash
docker compose up --build
```

Docker will spin up three containers:

| Container | Port | Notes |
|---|---|---|
| `server` | `8000` | FastAPI app |
| `mysql_db` | `3306` | MySQL 8.0 |
| `neo4j_db` | `7474` / `7687` | Neo4j (Browser + Bolt) |

### 4. Open the chat UI

Navigate to **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## Running Locally (Without Docker)

### 1. Start MySQL and Neo4j

Make sure MySQL and Neo4j are running. Update your `.env` to point to `localhost` instead of the Docker service names:

```env
NEO4J_URI=bolt://localhost:7687
MYSQL_HOST=localhost
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start the server

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## API Reference

All endpoints are served at `http://localhost:8000`.

### `POST /dynamic-kg-query` — Main Chat Endpoint

Send a user message and receive an AI response. Pass a `session_id` to maintain history across requests; omit it to start a fresh session.

```bash
curl -X POST http://localhost:8000/dynamic-kg-query \
  -F "query=Tell me about yourself" \
  -F "session_id=my-session-001"
```

**Response:**
```json
{
  "answer": "I'd love to help! What's on your mind today?",
  "session_id": "my-session-001"
}
```

---

### `PUT /neo4j-rag-query` — Direct RAG Query

Query the Neo4j knowledge graph directly without going through the agent.

```bash
curl -X PUT http://localhost:8000/neo4j-rag-query \
  -F "query=What do I know about the user's job?"
```

---

### `POST /neo4j-pipeline-kg` — Ingest Text into Graph

Manually push text into the knowledge graph pipeline.

```bash
curl -X POST http://localhost:8000/neo4j-pipeline-kg \
  -F "content=Alice is a software engineer who lives in Austin and loves hiking."
```

---

### `DELETE /neo4j-clear-database` — Clear Neo4j

Wipe all nodes and relationships from the configured Neo4j database.

```bash
curl -X DELETE http://localhost:8000/neo4j-clear-database
```

---

### `GET /health` — Health Check

```bash
curl http://localhost:8000/health
# {"message": "Service is up and running"}
```

---

## How the Memory System Works

```
Message 1–9     ──▶ Stored in MySQL only
                    Agent uses last 5 messages as context window

Message 10      ──▶ MySQL store + KG pipeline triggered
                    Last 10 messages extracted → Neo4j graph built for session
                    Agent now has access to chat_history_tool

Message 11+     ──▶ Agent uses BOTH:
                    • MySQL (last 5 messages) for conversational flow
                    • Neo4j RAG (entire history as graph) for factual recall

Every 10 msgs   ──▶ KG pipeline re-runs, keeping the graph current
```

### Graph Schema

The knowledge graph uses the following node and relationship types:

**Nodes:** `User`, `Agent`, `Session`, `Message`, `Fact`, `Entity`

**Relationships:**
```
User ──HAS_SESSION──▶ Session
Session ──CONTAINS_THREAD──▶ Message
Message ──NEXT_MESSAGE──▶ Message
Message ──SENT_BY──▶ User / Agent
User ──KNOWS_FACT──▶ Fact
Fact ──EXTRACTED_FROM──▶ Session
Message ──MENTIONS_ENTITY──▶ Entity
Entity ──RELATED_TO──▶ Entity
```

---

## Chat UI

The app ships with a built-in chat interface at `http://localhost:8000` (served from `static/index.html`).

Features:
- **Multi-session** management with persistent local storage
- **Graph RAG Active** indicator appears after the memory threshold is crossed
- **Knowledge Graph notification** appears when conversation is stored to Neo4j
- Health status indicator in the sidebar
- Mobile responsive

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `NEO4J_URI` | `neo4j://localhost:7687` | Neo4j connection URI |
| `NEO4J_USERNAME` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password` | Neo4j password |
| `NEO4J_DATABASE` | _(required)_ | Default Neo4j database name |
| `MYSQL_HOST` | `localhost` | MySQL host |
| `MYSQL_USER` | `root` | MySQL username |
| `MYSQL_PASSWORD` | _(required)_ | MySQL password |
| `MYSQL_DATABASE` | `chat_history_db` | MySQL database name |
| `OLLAMA_LLM_MODEL` | _(required)_ | Ollama model for chat (e.g. `llama3.2`) |
| `OLLAMA_EMBEDDING_MODEL` | _(required)_ | Ollama model for embeddings (e.g. `nomic-embed-text`) |
| `OLLAMA_EMBEDDING_DIMENSION` | `3072` | Embedding vector dimensions |

---

## Neo4j Browser

While the stack is running, you can explore the knowledge graph visually at:

**[http://localhost:7474](http://localhost:7474)**

- Username: `neo4j`
- Password: `password123` (as set in `compose.yaml`)

Try this Cypher query to see all nodes and relationships:
```cypher
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50
```

---

## Tech Stack

| Category | Technology |
|---|---|
| **API Framework** | FastAPI + Uvicorn |
| **LLM Orchestration** | LangChain + LangGraph |
| **LLM / Embeddings** | Ollama (local inference) |
| **Knowledge Graph** | Neo4j + `neo4j-graphrag` |
| **KG Builder** | `SimpleKGPipeline` (entity + relationship extraction) |
| **Vector Retrieval** | `VectorCypherRetriever` (cosine similarity + Cypher traversal) |
| **Chat History DB** | MySQL 8.0 |
| **Containerization** | Docker + Docker Compose |
| **Frontend** | Vanilla HTML/CSS/JS (zero dependencies) |

---

## License

Licensed under the [Apache License 2.0](LICENSE).
