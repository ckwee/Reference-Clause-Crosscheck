# Reference Clause Crosscheck

AI-assisted clause reference tool for checking valid complaint statements against exact clauses and requirements from uploaded reference documents.

Upload any mix of reference material in one field, including Acts, Regulations, SOPs, policies, standards, contracts, guidance documents, or other supporting documents. Then upload one or more valid complaint statements.

The app extracts exact clauses and requirements from the reference documents, preserving the source document and source type where possible. It then checks each complaint statement against the relevant source material and returns clause references, quoted text, match status, explanation, conclusions, and items that still need human verification.

## Run locally

Start the backend:

```bat
start_backend.bat
```

Start the frontend:

```bat
start_frontend.bat
```

The frontend runs on `http://localhost:8501` and the backend runs on `http://localhost:8000`.

The backend expects Ollama to be available at `http://localhost:11434` by default. Set `LLM_MODEL`, `OLLAMA_BASE_URL`, or `DATABASE_PATH` as environment variables if needed.
