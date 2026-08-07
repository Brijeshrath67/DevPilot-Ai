# DevPilot AI Release Plan

## Release Phases

### Phase 1: Architecture and scaffold
- Deliver architecture documentation
- Create folder structure and initial repository scaffolding
- Define API contracts and shared service modules

### Phase 2: Core backend and frontend foundation
- Implement API routing and Pydantic schemas
- Add backend service scaffolding and agent orchestrator
- Build frontend navigation and landing pages

### Phase 3: Repository ingestion and analysis
- Build repository ingestion workflow
- Implement parser service and repository analyzer agent
- Persist repository metadata and analysis reports

### Phase 4: AI workflows
- Implement documentation generation agent
- Implement testing generation agent
- Implement code review agent
- Implement repository chat agent with RAG

### Phase 5: Project health and dashboard
- Calculate health metrics
- Build health dashboard and frontend scorecards
- Store health recommendations in DB

### Phase 6: Production hardening
- Enable JWT auth and GitHub OAuth optional
- Add logging and error handling
- Add CI/CD and deploy to Vercel/Railway
- Add tests and release documentation

## Delivery checklist
- `README.md` updated
- `docs/ARCHITECTURE.md` complete
- `docs/ROADMAP.md` complete
- `docs/API_CONTRACTS.md` complete
- `docs/TESTING.md` complete
- Backend scaffold and core endpoints available
- Frontend shell with pages and routing available
- CI workflows defined and passing (`backend.yml`, `frontend.yml`, `test.yml`)
- Deploy pipeline defined (`deploy.yml`) with Docker images and Compose
- Unit and end-to-end tests green locally and in CI
- Developer scripts (`setup`, `run`, `seed`, `cleanup`) runnable

## Release notes
The first delivery should demonstrate the full architecture, a working repository analyzer API, and the dashboard UI shell. Subsequent releases add AI agents and RAG-based repository chat.
