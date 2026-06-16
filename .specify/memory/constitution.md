## Constitution

**Version:** 1.1.0 (2026-06-17)
**Last Updated By:** goose Agent

### 📜 Purpose and Scope

The purpose of this constitution is to serve as the foundational document defining:

1.  **Technical Principles:** The core architectural guidelines, technologies, and design philosophy for the `pygount` project.
2.  **Development Process (Goose Workflow):** The mandated multi-step process including specification, planning, task generation, implementation, testing, and documentation management.
3.  **Core Artifact Definitions:** Descriptions of key system components (e.g., State Management Layer, API Gateway, Core Logic Modules).

This document is the primary reference source and must be updated _before_ any major codebase changes are committed to ensure architectural coherence.

### 💡 Guiding Principles

1.  **Modularity First:** All features must be implementable via isolated, self-contained modules. High coupling is disallowed.
2.  **Single Source of Truth (SSOT):** Design decisions must originate from and be documented in the `design/artifacts` directory, governed by the `plan.md` artifact.
3.  **Defensive Code:** Implementations must anticipate failure states. Comprehensive logging and graceful degradation are mandatory for all external boundaries.
4.  **Iterative Refinement (PATCH Methodology):** No component is considered finished until it has undergone at least one full review/patch cycle, as demonstrated in the current process flow.

### 💾 Architectural Mandates

- **State Persistence:** The project MUST utilize asynchronous, transaction-safe persistence mechanisms (e.g., PostgreSQL with Sequelize/Alembic).
- **API Interaction:** All external communication must pass through a dedicated API Gateway module to enforce rate limiting, authentication, and schema validation.
- **Testing Coverage:** Unit tests must exceed 85% coverage, and integration tests must cover all critical user flows defined in the `tasks.md`.

---

_(End of Constitution Document)_"
