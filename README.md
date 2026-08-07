# DevPilot AI

AI Powered Developer Productivity Platform

## Overview
DevPilot AI is a modular, production-grade SaaS platform that helps engineering teams analyze repositories, review code, generate documentation and tests, chat with their codebase, and monitor project health.

## Architecture
- Frontend: React + Vite + TailwindCSS + shadcn/ui + React Router + Axios + React Query
- Backend: FastAPI + Python + SQLAlchemy + Pydantic
- AI: Gemini API, LangChain (as needed), Sentence Transformers, ChromaDB
- Database: PostgreSQL
- Auth: JWT (GitHub OAuth optional)
- Deployment: Vercel (frontend), Railway/Render (backend)
- CI/CD: GitHub Actions

## Folder structure
- frontend/
- backend/
- docs/
- .github/

## Project goals
- Build an AI developer productivity platform.
- Cover repository analysis, code review, documentation, test generation, repository QA chat, and health monitoring.
- Design according to modular SaaS architecture principles.
