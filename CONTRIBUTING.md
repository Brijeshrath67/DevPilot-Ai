# Contributing to DevPilot AI

Thank you for your interest in contributing to DevPilot!

## Code of Conduct
We aim to foster an open, welcoming, and secure community. Please be respectful and constructive in all communication channels.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/DevPilot-AI.git
   cd DevPilot-AI
   ```

2. **Backend Setup**:
   - Create a virtual environment: `python -m venv venv`
   - Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
   - Install requirements: `pip install -r backend/requirements.txt`
   - Run the FastAPI application: `uvicorn app.main:app --reload`

3. **Frontend Setup**:
   - Install node modules: `npm install`
   - Launch Vite development server: `npm run dev`

## Pull Request Guidelines
- Follow the agent guidelines outlined in `AGENTS.md`.
- Ensure type annotations and tests cover new endpoints or skills.
- Make clean, progressive git commits.
