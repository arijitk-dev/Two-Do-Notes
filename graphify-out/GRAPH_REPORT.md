# Graph Report - Two-Do-Notes  (2026-08-21)

## Corpus Check
- 75 files · ~19,113 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 455 nodes · 849 edges · 41 communities (35 shown, 6 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 62 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- User
- App.tsx
- todos.py
- api/auth.py
- user_today
- notes.py
- Session
- devDependencies
- compilerOptions
- What You Must Do When Invoked
- compilerOptions
- Two Do Notes
- graphify reference: extra exports and benchmark
- 0002_phase2_planning_carry_forward.py
- tsconfig.json
- vitest.polyfill.cjs
- graphify reference: query, path, explain
- conftest.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- AGENTS.md
- extraction-spec.md
- PointRepository
- get_calendar
- .recompute

## God Nodes (most connected - your core abstractions)
1. `TodoService` - 23 edges
2. `User` - 22 edges
3. `TodoRepository` - 21 edges
4. `Todo` - 17 edges
5. `user_today()` - 16 edges
6. `StreakService` - 16 edges
7. `Base` - 15 edges
8. `compilerOptions` - 15 edges
9. `PointRepository` - 12 edges
10. `What You Must Do When Invoked` - 12 edges

## Surprising Connections (you probably didn't know these)
- `register()` --uses--> `User`  [INFERRED]
  backend/app/api/auth.py → backend/app/models/user.py
- `login()` --uses--> `User`  [INFERRED]
  backend/app/api/auth.py → backend/app/models/user.py
- `get_calendar()` --uses--> `CalendarService`  [INFERRED]
  backend/app/api/calendar.py → backend/app/services/calendar_service.py
- `dashboard()` --uses--> `NoteRepository`  [INFERRED]
  backend/app/api/dashboard.py → backend/app/repositories/note_repository.py
- `dashboard()` --uses--> `PointRepository`  [INFERRED]
  backend/app/api/dashboard.py → backend/app/repositories/point_repository.py

## Import Cycles
- None detected.

## Communities (41 total, 6 thin omitted)

### Community 0 - "User"
Cohesion: 0.08
Nodes (39): Base, get_db(), Session, health(), get, startup_event(), PointTransaction, StrEnum (+31 more)

### Community 1 - "App.tsx"
Cohesion: 0.08
Nodes (26): api, addCalendarDays(), App(), CalendarPage(), todayForTimezone(), TodosPage(), CalendarView(), CarryForwardDialog() (+18 more)

### Community 2 - "todos.py"
Cohesion: 0.12
Nodes (31): carry_forward_todo(), carry_forward_todos(), complete_todo(), create_todo(), delete_todo(), get_todo(), list_todos(), miss_todo() (+23 more)

### Community 3 - "api/auth.py"
Cohesion: 0.13
Nodes (27): run_migrations_offline(), login(), logout(), me(), CurrentUser, DbSession, get, post (+19 more)

### Community 4 - "user_today"
Cohesion: 0.11
Nodes (22): dashboard(), CurrentUser, DbSession, get, get_streak(), CurrentUser, DbSession, get (+14 more)

### Community 5 - "notes.py"
Cohesion: 0.15
Nodes (22): create_note(), delete_note(), get_note(), get_note_endpoint(), list_notes(), CurrentUser, DbSession, delete (+14 more)

### Community 6 - "Session"
Cohesion: 0.46
Nodes (3): date, Session, Todo

### Community 7 - "devDependencies"
Cohesion: 0.05
Nodes (41): autoprefixer, dependencies, react, react-dom, react-router-dom, @tanstack/react-query, devDependencies, autoprefixer (+33 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, isolatedModules, jsx, lib, module (+12 more)

### Community 9 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 10 - "compilerOptions"
Cohesion: 0.12
Nodes (15): compilerOptions, allowImportingTsExtensions, lib, module, moduleDetection, moduleResolution, noEmit, skipLibCheck (+7 more)

### Community 11 - "Two Do Notes"
Cohesion: 0.20
Nodes (9): Architecture, Environment variables, Future phases, Local development, Phase 1 and Phase 2 scope, Phase 2 rules, Run with Docker, Tests (+1 more)

### Community 12 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 14 - "0002_phase2_planning_carry_forward.py"
Cohesion: 0.50
Nodes (3): Allow revision identifiers longer than Alembic's 32-character default., upgrade(), _widen_alembic_version_column()

### Community 29 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 30 - "conftest.py"
Cohesion: 0.60
Nodes (4): auth_client(), clean_db(), client(), fixture

### Community 31 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 32 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 33 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 38 - "PointRepository"
Cohesion: 0.19
Nodes (12): points_history(), points_summary(), CurrentUser, DbSession, get, PointRepository, date, Session (+4 more)

### Community 39 - "get_calendar"
Cohesion: 0.50
Nodes (4): get_calendar(), CurrentUser, DbSession, get

### Community 40 - ".recompute"
Cohesion: 0.50
Nodes (3): date, Session, User

## Knowledge Gaps
- **108 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+103 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `todos.py`, `api/auth.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `TodoRepository` connect `User` to `todos.py`, `user_today`, `Session`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `TodoService` connect `todos.py` to `User`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `TodoService` (e.g. with `complete_todo()` and `create_todo()`) actually correct?**
  _`TodoService` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `User` (e.g. with `login()` and `register()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TodoRepository` (e.g. with `dashboard()` and `list_todos()`) actually correct?**
  _`TodoRepository` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Todo` (e.g. with `PointRepository` and `TodoRepository`) actually correct?**
  _`Todo` has 6 INFERRED edges - model-reasoned connections that need verification._