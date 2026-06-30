import logging
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_reference_check_run, init_db, list_reference_check_runs, save_reference_check_run
from document_loader import load_document_secure
from models import ClauseSetSchema, PipelineRequest, PipelineResponse
from pipeline import check_complaint_statements, extract_reference_clauses, merge_clause_sets

logging.basicConfig(level="INFO")
logger = logging.getLogger("backend")

app = FastAPI(title="AI Reference Clause Crosscheck Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract_reference_clauses", response_model=ClauseSetSchema)
async def extract_reference_clauses_file(
    reference_files: List[UploadFile] = File(...),
):
    clause_sets = []
    for file in reference_files:
        clause_sets.append(extract_reference_clauses(load_document_secure(file), file.filename))
    return merge_clause_sets(clause_sets)


@app.post("/check_files")
async def check_files(
    review_title: str = Form("Untitled reference clause crosscheck"),
    reference_files: List[UploadFile] = File(...),
    complaint_statements: List[UploadFile] = File(...),
):
    reference_names = []
    clause_sets = []
    for file in reference_files:
        reference_names.append(file.filename)
        clause_sets.append(extract_reference_clauses(load_document_secure(file), file.filename))

    statements = {}
    for file in complaint_statements:
        statements[file.filename.rsplit(".", 1)[0]] = load_document_secure(file)

    reference_clauses = merge_clause_sets(clause_sets)
    checks = check_complaint_statements(reference_clauses, statements)

    run_id = save_reference_check_run(
        review_title=review_title,
        reference_names="; ".join(reference_names),
        reference_clauses=reference_clauses,
        checks=checks,
    )

    return {
        "run_id": run_id,
        "reference_clauses": reference_clauses,
        "checks": checks,
    }


@app.post("/pipeline", response_model=PipelineResponse)
async def pipeline_endpoint(req: PipelineRequest):
    reference_clauses = extract_reference_clauses(req.reference_text, "Reference text")
    checks = check_complaint_statements(reference_clauses, req.complaint_statements)
    return PipelineResponse(reference_clauses=reference_clauses, checks=checks)


@app.get("/reference_check_runs")
def reference_check_runs(limit: int = 25):
    return list_reference_check_runs(limit)


@app.get("/reference_check_runs/{run_id}")
def reference_check_run(run_id: int):
    run = get_reference_check_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Reference check run not found")
    return run
