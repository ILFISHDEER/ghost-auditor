"""Ghost Auditor — FastAPI app.

Implements the demo-critical path: upload -> audit -> dossier ->
Markdown report. Runs are stored in sqlite (backend/runs.db, ignored
by .gitignore). The frontend single page is served from /.

Run from the repo root with: uvicorn backend.main:app --reload
"""

import json
import pathlib
import sqlite3
import uuid

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:  # running as `uvicorn backend.main:app` from the repo root
    from backend import evidence as evidence_mod
    from backend import ingest as ingest_mod
    from backend import match as match_mod
    from backend import normalize as normalize_mod
    from backend import portal as portal_mod
except ImportError:  # running as `uvicorn main:app` from backend/
    import evidence as evidence_mod
    import ingest as ingest_mod
    import match as match_mod
    import normalize as normalize_mod
    import portal as portal_mod

BASE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
FRONTEND_DIR = REPO_ROOT / "frontend"
DB_PATH = BASE_DIR / "runs.db"

app = FastAPI(title="Ghost Auditor")

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


def _init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                created_at TEXT DEFAULT (datetime('now')),
                status TEXT,
                source TEXT,
                orders_json TEXT,
                invoices_json TEXT,
                portal_status TEXT,
                dossier_json TEXT,
                report_md TEXT
            )
            """
        )


_init_db()


def _to_jsonable(value: object) -> object:
    """Convert numpy/pandas scalars to plain JSON-safe Python values."""
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if pd.isna(value):
        return None
    if hasattr(value, "item"):  # numpy scalar
        return value.item()
    return value


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    return [_to_jsonable(r) for r in df.to_dict("records")]


def _records_to_df(records: list[dict]) -> pd.DataFrame:
    return pd.DataFrame.from_records(records)


class AuditRequest(BaseModel):
    run_id: str


@app.get("/")
def index() -> FileResponse:
    """Serve the frontend page."""
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/health")
def health() -> dict:
    """Liveness check."""
    return {"status": "ok", "service": "ghost-auditor"}


@app.post("/upload")
async def upload(
    orders_file: UploadFile | None = File(default=None),
    invoices_file: UploadFile | None = File(default=None),
) -> dict:
    """Accept orders + invoices files (CSV/XLSX) and return a run id.

    Both files or neither: with neither, the bundled synthetic sample
    data is used (the demo path). With only one file, a clear error is
    returned. Files are parsed and validated here; matching happens in
    /audit.
    """
    try:
        if orders_file is None and invoices_file is None:
            orders_df, invoices_df = ingest_mod.load_sample_data()
            source = "sample"
        elif orders_file is None or invoices_file is None:
            raise HTTPException(
                status_code=400,
                detail="upload both an orders file and an invoices file, "
                "or neither (to use the bundled sample data)",
            )
        else:
            orders_df = ingest_mod.parse_upload(
                orders_file.filename, await orders_file.read(), "orders"
            )
            invoices_df = ingest_mod.parse_upload(
                invoices_file.filename, await invoices_file.read(), "invoices"
            )
            source = "upload"
    except ingest_mod.IngestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    run_id = uuid.uuid4().hex[:12]
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO runs (run_id, status, source, orders_json, invoices_json)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                run_id,
                "uploaded",
                source,
                json.dumps(_df_to_records(orders_df)),
                json.dumps(_df_to_records(invoices_df)),
            ),
        )
    return {
        "run_id": run_id,
        "status": "uploaded",
        "source": source,
        "orders_count": len(orders_df),
        "invoices_count": len(invoices_df),
    }


@app.post("/audit")
def audit(req: AuditRequest) -> dict:
    """Run the pipeline for a run id and return the dossier JSON."""
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT orders_json, invoices_json FROM runs WHERE run_id = ?",
            (req.run_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"unknown run_id: {req.run_id}")

    try:
        orders = normalize_mod.normalize_orders(_records_to_df(json.loads(row[0])))
        invoices = normalize_mod.normalize_invoices(_records_to_df(json.loads(row[1])))
    except normalize_mod.NormalizeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Crew step 1 — Capture (best effort; file-only matching on failure).
    try:
        portal_rows = portal_mod.capture_portal_rows()
        portal_df = normalize_mod.normalize_portal_rows(portal_rows)
        portal_status = f"captured {len(portal_rows)} rows from the mock portal"
    except portal_mod.PortalCaptureError as exc:
        portal_df = None
        portal_status = f"unavailable ({exc}); audit ran on file data only"

    # Crew steps 2–4 — Normalize (done) -> Match -> Explain.
    matched, exceptions = match_mod.match(orders, invoices)
    evidenced = evidence_mod.attach_evidence(exceptions, orders, invoices, portal_df)
    dossier = evidence_mod.build_dossier(evidenced, matched, total_orders=len(orders))
    report_md = evidence_mod.render_markdown_report(dossier)

    orphan_ids = sorted(
        {str(r["order_id"]) for _, r in invoices.iterrows()}
        - {str(r["order_id"]) for _, r in orders.iterrows()}
    )
    dossier["orphan_invoice_order_ids"] = orphan_ids

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE runs SET status = ?, portal_status = ?, dossier_json = ?,"
            " report_md = ? WHERE run_id = ?",
            ("done", portal_status, json.dumps(_to_jsonable(dossier)), report_md, req.run_id),
        )
    return {"run_id": req.run_id, "portal_status": portal_status, **_to_jsonable(dossier)}


@app.get("/report/{run_id}")
def report(run_id: str) -> PlainTextResponse:
    """Return the stored dossier for run_id as a downloadable Markdown report."""
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT report_md FROM runs WHERE run_id = ? AND status = 'done'",
            (run_id,),
        ).fetchone()
    if row is None or row[0] is None:
        raise HTTPException(
            status_code=404,
            detail=f"no completed audit for run_id: {run_id}",
        )
    return PlainTextResponse(
        row[0],
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=ghost-auditor-report-{run_id}.md"
        },
    )
