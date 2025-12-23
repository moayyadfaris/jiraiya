# 🐸 Jiraiya Service

**Jiraiya** is an AI-powered story generator microservice built for the Kuybi project.

> **Status:** 🟡 Basic Implementation - Enterprise Enhancement In Progress  
> **Version:** 0.1.0  
> **Review Date:** December 23, 2025

## 📊 Current State

- ✅ **Working:** Basic FastAPI structure, health checks, API documentation
- ⚠️ **In Progress:** Mock AI implementation (needs LangChain integration)
- ❌ **Missing:** Authentication, logging, monitoring, comprehensive testing

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
    # Edit .env and add your OPENAI_API_KEY and JWT_SECRET
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

### Current (v0.1.0)
*   `GET /` - Welcome message
*   `GET /api/v1/health` - Basic health check
*   `POST /api/v1/generate` - Generate story (⚠️ mock implementation)

### Coming Soon
*   `GET /api/v1/health/ready` - Readiness probe
*   `GET /api/v1/health/live` - Liveness probe
*   `GET /metrics` - Prometheus metrics
*   Enhanced `/generate` with real AI

## 🚀 Enhancement Plan

This service is being enhanced to enterprise production standards:

### Critical (Week 1)
- [ ] Structured logging with correlation IDs (6h)
- [ ] Enhanced configuration with validation (4h)
- [ ] Custom exceptions and error handling (5h)
- [ ] Comprehensive health checks (4h)

### High Priority (Week 2)
- [ ] Real LangChain + OpenAI integration (8h)
- [ ] Authentication (JWT/API keys) (6h)
- [ ] Rate limiting (2h)
- [ ] Security headers and CORS (2h)

### Testing (Week 2-3)
- [ ] Unit tests (target 80% coverage) (8h)
- [ ] Integration tests (6h)
- [ ] Load tests (4h)

### Observability (Week 3)
- [ ] Prometheus metrics (5h)
- [ ] OpenTelemetry tracing (6h)

**Total Estimated Effort:** ~88 hours (2-3 weeks)

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
// Example usage from Kuybi Dashboard
const story = await fetch('http://jiraiya-service:8000/api/v1/generate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwt}`,
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

**Last Updated:** December 23, 2025  
**Next Milestone:** Complete Phase 1 (Core Infrastructure)
