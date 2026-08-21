Two Do Notes is a personal productivity and accountability application.

Before modifying code:

1. Read this file.
2. Read relevant files under .graphify/.
3. Identify affected requirements and business rules.
4. Inspect the existing implementation.
5. Make the smallest appropriate change.
6. Run relevant tests.
7. Run the full test suite when appropriate.
8. Update .graphify/ documentation if architecture, rules,
   dependencies, entities, APIs, or important decisions changed.

Architecture:

React + TypeScript
↓
FastAPI
↓
Service Layer
↓
Repository Layer
↓
PostgreSQL

Important rules:

- Point history is immutable.
- A Todo cannot receive the same reward twice.
- Business logic belongs in services, not API routes.
- Users may only access their own data.
- Date calculations must respect the user's timezone.
- A successful day requires every planned Todo to be resolved and at least 80% completed; zero-Todo days are neutral.
- Daily Reviews are optional reflection records and never affect points.
- Accountability metrics derive from canonical Todo and point-ledger data; do not store duplicate aggregates.
- The normal Todo history/reuse interface is limited to the latest 15 calendar days. Older Todo rows are retained unless a future audited retention process is added, so accountability and point history remain trustworthy.
- Tests are required for business-rule changes.
- Do not introduce unnecessary infrastructure.
- Do not implement future-phase features without explicit approval.

Source code and passing tests are the ultimate source of truth.
.graphify/ provides project context and relationships.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
