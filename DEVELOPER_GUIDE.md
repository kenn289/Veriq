# Developer Guide

## Backend setup
1. cd backend
2. python -m venv .venv
3. .venv\Scripts\activate
4. pip install -e .[dev]
5. uvicorn veriq.main:app --reload

## Frontend setup
1. cd frontend
2. npm install
3. npm run dev

## Testing
- Backend: pytest
- Frontend: npm run lint and npm run build

## Linting and formatting
- Python: ruff, black, mypy
- Frontend: eslint, prettier
