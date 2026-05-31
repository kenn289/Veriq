Deployment notes for Vercel / container hosting

Summary:
- The backend is an ASGI FastAPI app exposed at `veriq.api.app:app`.
- For production, build a container (Dockerfile provided) and run with Uvicorn/Gunicorn.

Vercel considerations:
- Vercel's Python serverless environment has limitations for long-running tasks
  and background workers. For full production workloads consider deploying
  the container to a provider that supports long-running containers (Railway,
  Fly, Render, AWS ECS, GCP Cloud Run) or run the executor via a worker.

Quick start (Docker):

```powershell
docker build -t veriq-backend:latest -f Dockerfile .
docker run -p 8000:8000 --env-file .env -e DATABASE_URL="postgresql://..." veriq-backend:latest
```

Notes:
- The `LocalTestExecutor` runs test cases synchronously during `start_test_run`.
  For scale, switch this to an async worker (Celery/RQ) and keep the API fast.
- Ensure environment variables for DB and secret keys are set in production.

Playwright executor (optional):
- To enable browser-driven execution, install the optional dependency and browsers:

```powershell
cd backend
pip install -e .[playwright]
python -m playwright install
```

- Set `VERIQ_EXECUTION_BACKEND=playwright` and `VERIQ_PLAYWRIGHT_BROWSER=chromium|firefox|webkit`.
- Playwright needs browser binaries and system libs; for production run the worker in a container that includes them (see Playwright Docker images).

