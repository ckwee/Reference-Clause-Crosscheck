# Reference Clause Crosscheck

Reference Clause Crosscheck is a local AI-assisted application for checking valid complaint statements against exact clauses, requirements, rules, procedures, and obligations extracted from uploaded reference documents.

The tool is designed for evidence-based regulatory, policy, SOP, and governance review workflows where the output needs to show source-backed clause references rather than rankings, scores, or general summaries.

## Overview

In many compliance review workflows, the central question is not "which document ranks highest?" but:

> Which exact clause, section, rule, SOP step, or requirement supports or contradicts this complaint statement?

This project helps with that task by allowing a reviewer to upload a set of reference documents and one or more valid complaint statements. The backend extracts relevant clauses and requirements from the reference documents, then checks each complaint statement against the extracted material.

The application returns a traceable output showing:

- the complaint statement being reviewed
- the source document used for each match
- the inferred source type, such as Act, Regulation, SOP, Policy, Standard, Contract, or Reference
- the clause, section, heading, or requirement reference
- the quoted clause or requirement text
- the match status
- an explanation of why the clause is relevant
- a conclusion for the complaint statement
- any items that still require human verification

## Key Features

- Multi-file reference upload: upload Acts, Regulations, SOPs, policies, standards, contracts, guidance documents, or other reference material together.
- Multi-file complaint upload: upload one or more valid complaint statements in the same run.
- Exact clause extraction: extracts clause references, quoted clause text, source document names, source types, summaries, and keywords.
- Source-backed matching: compares each complaint statement against extracted clauses and requirements.
- Saved review history: stores completed runs in a local SQLite database.
- CSV export: exports results for reporting, review records, or audit trails.
- Local-first architecture: designed to run with a local FastAPI backend, Streamlit frontend, SQLite database, and Ollama model server.
- PDF and DOCX support: accepts common document formats for both references and complaint statements.

## Intended Use Cases

This project can support workflows such as:

- regulatory complaint triage
- validating complaint statements against Acts or Regulations
- crosschecking internal SOP compliance
- mapping alleged non-compliance to exact source requirements
- checking policy or contract obligations against complaint evidence
- preparing clause reference tables for review teams
- building a repeatable audit trail for document-based assessments

## Important Disclaimer

This tool provides decision support only. It does not provide legal advice, regulatory advice, compliance certification, or final determinations.

All extracted clauses, quoted text, match explanations, and conclusions must be reviewed against the original source documents by an appropriately qualified person before being relied upon.

## How It Works

At a high level, the application follows this workflow:

1. The user uploads reference documents.
2. The user uploads one or more valid complaint statements.
3. The backend extracts text from PDFs and DOCX files.
4. Each reference document is processed separately so source names are preserved.
5. The LLM extracts relevant clauses, requirements, SOP steps, or rules from each reference document.
6. The extracted clauses are merged into one reference set.
7. Each complaint statement is checked against the reference set.
8. Results are saved to SQLite and returned to the Streamlit frontend.
9. The user reviews clause matches and can download a CSV report.

## Architecture

```text
User browser
    |
    v
Streamlit frontend
    |  uploads reference documents and complaint statements
    v
FastAPI backend
    |  extracts document text
    |  calls LLM clause extraction and matching pipeline
    v
Ollama model server
    |
    v
JSON structured results
    |
    +--> SQLite saved history
    +--> Streamlit result display
    +--> CSV export
```

## Project Structure

```text
.
|-- backend/
|   |-- main.py              # FastAPI routes and upload handling
|   |-- pipeline.py          # Clause extraction and complaint matching workflow
|   |-- models.py            # Pydantic request/response schemas
|   |-- database.py          # SQLite persistence for saved runs
|   |-- document_loader.py   # Secure PDF/DOCX text extraction
|   |-- llm_service.py       # Ollama + LangChain JSON helper functions
|   |-- config.py            # Runtime settings and environment variables
|   |-- requirements.txt     # Backend Python dependencies
|   `-- Dockerfile
|-- frontend/
|   |-- streamlit_app.py     # Streamlit user interface
|   |-- requirements.txt     # Frontend Python dependencies
|   `-- Dockerfile
|-- docker-compose.yml       # Optional container orchestration
|-- start_backend.bat        # Windows helper script for backend
|-- start_frontend.bat       # Windows helper script for frontend
`-- README.md
```

## Technology Stack

- Python
- FastAPI
- Streamlit
- Pydantic
- SQLite
- LangChain
- Ollama
- PyMuPDF for PDF loading
- docx2txt for Word document loading

## Requirements

- Python 3.11 or later recommended
- Ollama installed and running locally, or available over the network
- An Ollama-compatible model, for example `llama3.1`
- PDF or DOCX source documents
- Windows, macOS, or Linux

Windows batch scripts are included for convenience, but the backend and frontend can also be started manually on any operating system that supports the dependencies.

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

Create and activate a virtual environment if desired:

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd ../frontend
pip install -r requirements.txt
```

## Ollama Setup

Install Ollama from the official Ollama website, then pull a model:

```bash
ollama pull llama3.1
```

Confirm the model is available:

```bash
ollama list
```

By default, the backend expects Ollama at:

```text
http://localhost:11434
```

## Running Locally

### Option 1: Windows helper scripts

From the project root, start the backend:

```bat
start_backend.bat
```

In a second terminal, start the frontend:

```bat
start_frontend.bat
```

### Option 2: Manual commands

Start the backend:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Start the frontend in another terminal:

```bash
cd frontend
streamlit run streamlit_app.py
```

Open the app:

```text
http://localhost:8501
```

Backend API:

```text
http://localhost:8000
```

## Using The Application

1. Open the Streamlit frontend.
2. Enter a review title.
3. Upload one or more reference documents.
4. Upload one or more valid complaint statements.
5. Select `Check clauses`.
6. Review the extracted reference clauses.
7. Review each complaint statement result.
8. Download the CSV output if required.

## Input Documents

### Reference Documents

Reference documents are the source materials used to test complaint statements. Examples include:

- legislation
- regulations
- SOPs
- internal policies
- technical standards
- contracts
- guidelines
- procedural manuals
- correspondence or formal directions

Each reference document is processed separately before clauses are merged. This helps preserve the source document name in the output.

### Valid Complaint Statements

Complaint statements should be documents containing the statements or allegations to be checked. Each uploaded complaint statement file is treated as one statement source and is labelled using the filename.

## Output Fields

Each match can include:

| Field | Description |
| --- | --- |
| Complaint statement | Name of the uploaded complaint statement file |
| Source type | Inferred source type, such as Act, Regulation, SOP, Policy, Standard, Contract, or Reference |
| Source document | Filename or document name for the matched source |
| Clause reference | Clause, section, heading, step, or requirement reference |
| Match status | Relationship between the complaint statement and the source clause |
| Clause text | Quoted source text returned by the model |
| Explanation | Why the source text is relevant |
| Items to verify | Follow-up items requiring human review |

Common match statuses include:

- Directly relevant
- Partly relevant
- Potential conflict
- Not addressed

## Configuration

The backend reads these optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LLM_MODEL` | `llama3.1` | Ollama model name |
| `LLM_TEMPERATURE` | `0.0` | Model temperature |
| `LLM_NUM_CTX` | `16384` | Context window size |
| `LLM_MAX_RETRIES` | `3` | JSON parse retry count |
| `MAX_FILE_SIZE_MB` | `10` | Maximum uploaded file size in MB |
| `MAX_WORKERS` | `4` | Parallel complaint statement checks |
| `DATABASE_PATH` | `data/compliance_reviews.db` | SQLite database path |

Example on Windows:

```bat
set LLM_MODEL=llama3.1
set OLLAMA_BASE_URL=http://localhost:11434
```

Example on macOS/Linux:

```bash
export LLM_MODEL=llama3.1
export OLLAMA_BASE_URL=http://localhost:11434
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Checks whether the backend is running |
| `POST` | `/extract_reference_clauses` | Extracts clauses from uploaded reference documents |
| `POST` | `/check_files` | Runs the full file upload workflow |
| `POST` | `/pipeline` | Runs the text-based pipeline workflow |
| `GET` | `/reference_check_runs` | Lists saved review runs |
| `GET` | `/reference_check_runs/{run_id}` | Retrieves a saved review run |

## Example Workflow

Example reference uploads:

- Building Act.pdf
- Building Regulation.pdf
- Complaints Handling SOP.docx
- Internal Escalation Policy.docx

Example complaint statement uploads:

- Complaint Statement 1.docx
- Complaint Statement 2.docx

Expected result:

- each complaint statement is checked against the extracted requirements
- matched clauses retain their source document names
- the reviewer can inspect exact quoted text
- unresolved or weakly supported statements are flagged for verification
- results can be exported to CSV

## Data Storage

Review history is stored in SQLite using the configured `DATABASE_PATH`.

The default path is:

```text
backend/data/compliance_reviews.db
```

Database files are local runtime artifacts and usually should not be committed to GitHub.

## Privacy And Security

This project is intended to run locally. Uploaded documents are sent from the Streamlit frontend to the local FastAPI backend, then to the configured Ollama server.

If Ollama is running locally, the core processing flow remains on your machine. If you configure a remote Ollama endpoint, uploaded document text may leave your machine.

Before using this tool with sensitive material, confirm that your runtime environment is approved for:

- confidential documents
- personal information
- legal or privileged material
- regulated information
- complaint or investigation records

## Docker

A `docker-compose.yml` file is included for container-based deployment. The backend container expects access to an Ollama endpoint. On Docker Desktop, this is commonly configured with:

```text
http://host.docker.internal:11434
```

Run with:

```bash
docker compose up --build
```

## Troubleshooting

### Backend does not start

Install backend dependencies in the active Python environment:

```bash
pip install -r backend/requirements.txt
```

Then run:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend cannot connect to backend

Confirm the backend is running at:

```text
http://localhost:8000
```

If the backend uses another URL, set `BACKEND_URL` before starting Streamlit.

### Ollama connection errors

Check Ollama:

```bash
ollama list
```

Pull the configured model if needed:

```bash
ollama pull llama3.1
```

### Results show few or no matches

Try the following:

- check whether the PDF has selectable text rather than scanned images
- split very large reference documents into smaller files
- upload the most relevant SOP or policy documents with the legislation
- increase `LLM_NUM_CTX` if the model supports a larger context window
- use a stronger local model if available
- make complaint statement documents clearer and more specific

### Source names show as Reference document

The backend attempts to preserve filenames and infer source types. If a source type is not obvious from the filename, rename the file with a clearer label, for example:

- `Building Act 1975.pdf`
- `Building Regulation 2021.pdf`
- `Complaints Handling SOP.docx`

### Streamlit, PyArrow, or Numpy errors

This project avoids `st.dataframe` in the history view to reduce PyArrow/Numpy dependency issues. If your Python environment still has package conflicts, create a clean virtual environment and reinstall dependencies.

## Development Notes

- The backend asks the LLM to return structured JSON.
- Pydantic validates the returned JSON.
- Failed JSON parses are retried based on `LLM_MAX_RETRIES`.
- Clause extraction runs per reference document so source filenames are preserved.
- Complaint statement checks run in parallel based on `MAX_WORKERS`.

## Limitations

- The model may miss clauses if source text extraction is poor.
- Scanned PDFs without OCR may produce little or no usable text.
- Very large documents may exceed the model context window.
- LLM outputs must be reviewed for accuracy.
- This tool does not determine legal validity or regulatory compliance on its own.

# MIT License

Copyright (c) 2026 CK

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
## Licence

Add your preferred licence before publishing this repository.
