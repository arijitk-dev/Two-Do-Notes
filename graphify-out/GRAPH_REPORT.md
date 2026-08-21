# Graph Report - Two-Do-Notes  (2026-08-21)

## Corpus Check
- 86 files · ~24,393 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 565 nodes · 1139 edges · 42 communities (36 shown, 6 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 82 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `edf6e266`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- User
- App.tsx
- TodoService
- devDependencies
- api/auth.py
- user_today
- DailyReviewService
- notes.py
- AccountabilityService
- TodoRepository
- What You Must Do When Invoked
- dashboard.py
- compilerOptions
- compilerOptions
- Two Do Notes
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- 0002_phase2_planning_carry_forward.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- tsconfig.json
- AGENTS.md
- extraction-spec.md
- vitest.polyfill.cjs

## God Nodes (most connected - your core abstractions)
1. `User` - 31 edges
2. `TodoService` - 30 edges
3. `AccountabilityService` - 28 edges
4. `user_today()` - 27 edges
5. `Todo` - 24 edges
6. `TodoRepository` - 23 edges
7. `StreakService` - 18 edges
8. `Base` - 17 edges
9. `TodoStatus` - 15 edges
10. `compilerOptions` - 15 edges

## Surprising Connections (you probably didn't know these)
- `accountability()` --uses--> `AccountabilityService`  [INFERRED]
  backend/app/api/accountability.py → backend/app/services/accountability_service.py
- `register()` --uses--> `User`  [INFERRED]
  backend/app/api/auth.py → backend/app/models/user.py
- `login()` --uses--> `User`  [INFERRED]
  backend/app/api/auth.py → backend/app/models/user.py
- `dashboard()` --uses--> `NoteRepository`  [INFERRED]
  backend/app/api/dashboard.py → backend/app/repositories/note_repository.py
- `dashboard()` --uses--> `TodoRepository`  [INFERRED]
  backend/app/api/dashboard.py → backend/app/repositories/todo_repository.py

## Import Cycles
- None detected.

## Communities (42 total, 6 thin omitted)

### Community 0 - "User"
Cohesion: 0.08
Nodes (40): accountability_message(), miss_reason_label(), MissReasonCode, StrEnum, Select a stable message for a context without showing one on every action., Base, health(), get (+32 more)

### Community 1 - "App.tsx"
Cohesion: 0.06
Nodes (37): api, addCalendarDays(), App(), CalendarPage(), DailyReviewPage(), todayForTimezone(), todoDateFromSearch(), TodosPage() (+29 more)

### Community 2 - "TodoService"
Cohesion: 0.11
Nodes (34): carry_forward_todo(), carry_forward_todos(), complete_todo(), create_todo(), delete_todo(), get_todo(), list_todos(), miss_todo() (+26 more)

### Community 3 - "devDependencies"
Cohesion: 0.05
Nodes (41): autoprefixer, dependencies, react, react-dom, react-router-dom, @tanstack/react-query, devDependencies, autoprefixer (+33 more)

### Community 4 - "api/auth.py"
Cohesion: 0.12
Nodes (29): run_migrations_offline(), login(), logout(), me(), CurrentUser, DbSession, get, post (+21 more)

### Community 5 - "user_today"
Cohesion: 0.10
Nodes (27): get_streak(), CurrentUser, DbSession, get, date, datetime, user_today(), user_tomorrow() (+19 more)

### Community 6 - "DailyReviewService"
Cohesion: 0.13
Nodes (25): accountability(), CurrentUser, date, DbSession, get, create_review(), get_review(), CurrentUser (+17 more)

### Community 7 - "notes.py"
Cohesion: 0.15
Nodes (22): create_note(), delete_note(), get_note(), get_note_endpoint(), list_notes(), CurrentUser, DbSession, delete (+14 more)

### Community 8 - "AccountabilityService"
Cohesion: 0.15
Nodes (13): AccountabilityService, DayMetrics, date, datetime, Session, Todo, User, Calculates accountability from Todo and point-ledger data, never stored metrics. (+5 more)

### Community 9 - "TodoRepository"
Cohesion: 0.15
Nodes (15): get_calendar(), CurrentUser, DbSession, get, date, Session, Todo, TodoRepository (+7 more)

### Community 10 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 11 - "dashboard.py"
Cohesion: 0.15
Nodes (16): dashboard(), CurrentUser, DbSession, get, points_history(), points_summary(), CurrentUser, DbSession (+8 more)

### Community 12 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, isolatedModules, jsx, lib, module (+12 more)

### Community 13 - "compilerOptions"
Cohesion: 0.12
Nodes (15): compilerOptions, allowImportingTsExtensions, lib, module, moduleDetection, moduleResolution, noEmit, skipLibCheck (+7 more)

### Community 14 - "Two Do Notes"
Cohesion: 0.17
Nodes (11): Architecture, Environment variables, Future phases, Local development, Phase 1 and Phase 2 scope, Phase 2 rules, Phase 3 rules, Run with Docker (+3 more)

### Community 15 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 16 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 17 - "0002_phase2_planning_carry_forward.py"
Cohesion: 0.50
Nodes (3): Allow revision identifiers longer than Alembic's 32-character default., upgrade(), _widen_alembic_version_column()

### Community 18 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 19 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 20 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **115 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+110 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `TodoService`, `api/auth.py`, `user_today`, `DailyReviewService`, `AccountabilityService`, `TodoRepository`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `AccountabilityService` connect `AccountabilityService` to `User`, `dashboard.py`, `DailyReviewService`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `TodoService` connect `TodoService` to `User`, `TodoRepository`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `User` (e.g. with `login()` and `register()`) actually correct?**
  _`User` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `TodoService` (e.g. with `complete_todo()` and `create_todo()`) actually correct?**
  _`TodoService` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `AccountabilityService` (e.g. with `accountability()` and `dashboard()`) actually correct?**
  _`AccountabilityService` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Todo` (e.g. with `PointRepository` and `TodoRepository`) actually correct?**
  _`Todo` has 7 INFERRED edges - model-reasoned connections that need verification._