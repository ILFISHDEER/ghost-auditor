"""Ghost Auditor — FastAPI app skeleton.

STUB STATUS: only GET /health is implemented. The /upload, /audit, and
/report/{run_id} endpoints return clearly-marked stub responses and do
NOT produce real audit results. See .kiro/specs/ghost-auditor/tasks.md
for the implementation order.

Run with: uvicorn backend.main:app --reload
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Ghost Auditor")

# Serve the single-page frontend from / (API routes take precedence).
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def index() -> FileResponse:
    """Serve the frontend page."""
    return FileResponse("frontend/index.html")


@app.get("/health")
def health() -> dict:
    """Liveness check. This endpoint is implemented."""
    return {"status": "ok", "service": "ghost-auditor"}


@app.post("/upload")
def upload() -> dict:
    """STUB — not implemented yet.

    TODO: accept orders + invoices files (CSV/XLSX), parse them via
    ingest.py, validate required columns, and return a run id.
    """
    return {
        "status": "stub",
        "message": "upload endpoint not implemented yet",
    }


@app.post("/audit")
def audit() -> dict:
    """STUB — not implemented yet.

    TODO: run the pipeline (portal capture -> normalize -> match ->
    evidence) for a run id and return the dossier JSON.
    """
    return {
        "status": "stub",
        "message": "audit endpoint not implemented yet",
    }


@app.get("/report/{run_id}")
def report(run_id: str) -> dict:
    """STUB — not implemented yet.

    TODO: render the stored dossier for run_id as a downloadable
    Markdown report.
    """
    return {
        "status": "stub",
        "message": "report endpoint not implemented yet",
        "run_id": run_id,
    }
