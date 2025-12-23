# 🐸 Jiraiya Service

**Jiraiya** is an AI-powered story generator microservice built for the Kuybi project.

> **Status:** 🟢 Production Ready
> **Version:** 1.0.0
> **Review Date:** December 24, 2025

## 📊 Current State

- ✅ **Core:** FastAPI structure, health checks (liveness/readiness), API documentation
- ✅ **AI:** Real Story Generation using LangChain + OpenAI (GPT-4o)
- ✅ **Security:** API Key Authentication (`X-API-KEY`)
- ✅ **Observability:** Structured JSON logging with correlation IDs
- ✅ **Resilience:** Retry logic for AI service calls

**See:** [Enterprise Review](./docs/ENTERPRISE_REVIEW.md) for detailed assessment

---

## 🎯 Quick Links

- **📋 [Quick Reference](./docs/QUICK_REFERENCE.md)** - Fast overview and priority fixes
- **📊 [Enterprise Review](./docs/ENTERPRISE_REVIEW.md)** - Detailed code review and gap analysis
- **🚀 [Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md)** - Step-by-step guide with code examples
- **📈 [Enterprise Progress](./docs/ENTERPRISE_PROGRESS.md)** - Full enhancement tracking

---

## Tech Stack

*   **Language:** Python 3.11+
*   **Framework:** FastAPI
*   **AI:** LangChain + OpenAI
*   **Validation:** Pydantic
*   **Dependencies:** Poetry
*   **Container:** Docker
*   **Logging:** Structlog

## Getting Started

### Prerequisites

*   Python 3.11+
*   Poetry
*   Docker & Docker Compose
*   OpenAI API Key

### Local Development

1.  **Clone and Install:**
    ```bash
    poetry install
    ```

2.  **Configure Environment:**
    ```bash
    cp .env.example .env
    # Edit .env and add your OPENAI_API_KEY and AUTH_API_KEY
    ```

3.  **Run Locally:**
    ```bash
    poetry run uvicorn src.main:app --reload
    ```
    - API: `http://localhost:8000`
    - Docs: `http://localhost:8000/docs`
    - ReDoc: `http://localhost:8000/redoc`

4.  **Run with Docker:**
    ```bash
    docker-compose up --build
    ```

## Development

*   **Format Code:** `poetry run black .`
*   **Lint Code:** `poetry run ruff check .`
*   **Run Tests:** `poetry run pytest`

## API Endpoints

### Core (v1)
*   `GET /` - Welcome message
*   `GET /api/v1/health` - Basic health check
*   `GET /api/v1/health/ready` - Readiness probe (checks OpenAI connection)
*   `POST /api/v1/generate` - Generate story using AI
    - Headers: `X-API-KEY: <your_key>`
    - Body: `{ "keywords": [...], "genre": "...", "tone": "..." }`

### Observability
*   `GET /metrics` - Prometheus metrics (Planned)

## 🚀 Enhancement Plan

The Core Phase is complete. Upcoming enhancements:

### Observability (Next)
- [ ] Prometheus metrics integration
- [ ] OpenTelemetry tracing

### Testing (In Progress)
- [ ] Comprehensive unit test suite
- [ ] Load testing with Artillery

**Total Estimated Effort:** ~20 hours remaining

See [Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md) for detailed step-by-step guide.

---

## 📚 Documentation

- **[Enterprise Review](./docs/ENTERPRISE_REVIEW.md)** - Comprehensive code review and recommendations
- **[Enterprise Progress](./docs/ENTERPRISE_PROGRESS.md)** - Phased enhancement roadmap
- **[Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md)** - Step-by-step implementation guide
- **[Quick Reference](./docs/QUICK_REFERENCE.md)** - Quick start and priority overview

---

## 🔗 Integration with Kuybi

This service integrates with the Kuybi Dashboard for story generation:

```typescript
// Example usage from Kuybi Dashboard / BFF
const story = await fetch('http://jiraiya-service:8000/api/v1/generate', {
  method: 'POST',
  headers: {
    'X-API-KEY': process.env.JIRAIYA_API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    keywords: ['dragon', 'adventure'],
    genre: 'fantasy',
    tone: 'epic',
    max_length: 500
  })
});
```

---

## 📝 License

Part of the Kuybi Project

---

**Last Updated:** December 24, 2025
**Current Status:** Production Ready (Phase 1 Complete)
