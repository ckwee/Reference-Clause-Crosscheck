import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

from config import settings
from models import ClauseSetSchema, StatementCheckSchema
from llm_service import build_json_chain, safe_llm_invoke

logger = logging.getLogger("pipeline")

def infer_source_type(source_name: str) -> str:
    name = source_name.lower()
    if "regulation" in name or "reg" in name:
        return "Regulation"
    if "act" in name:
        return "Act"
    if "sop" in name or "procedure" in name:
        return "SOP"
    if "policy" in name:
        return "Policy"
    if "standard" in name:
        return "Standard"
    if "contract" in name or "agreement" in name:
        return "Contract"
    return "Reference"

def extract_reference_clauses(reference_text: str, source_name: str = "Reference document", source_type: str | None = None) -> ClauseSetSchema:
    source_type = source_type or infer_source_type(source_name)
    chain, parser = build_json_chain(
        "Extract exact clauses, requirements, SOP steps, rules, and obligations for complaint compliance checking. Output JSON only. Preserve source document name, source type, clause numbers, section headings, and exact quoted text where available.",
        "Source type: {source_type}\nSource document: {source_name}\n\nSource text:\n{reference_text}\n\nExtract clauses, sections, requirements, SOP steps, rules, or obligations that could be used to test complaint statements. Return every materially relevant item you can identify. For each item, set source_type and source_name exactly as supplied, include the best available clause_reference or section/page heading, quote exact clause_text, summarize the obligation, and add keywords. Do not return N/A for source_name.\n\nFormat:\n{format_instructions}",
        ClauseSetSchema,
    )
    result = safe_llm_invoke(
        chain,
        {
            "source_type": source_type,
            "source_name": source_name,
            "reference_text": reference_text,
            "format_instructions": parser.get_format_instructions(),
        },
        ClauseSetSchema,
    )
    if not result:
        return ClauseSetSchema()
    for clause in result.clauses:
        clause.source_type = clause.source_type if clause.source_type and clause.source_type != "N/A" else source_type
        clause.source_name = clause.source_name if clause.source_name and clause.source_name != "N/A" else source_name
    return result

def merge_clause_sets(clause_sets: List[ClauseSetSchema]) -> ClauseSetSchema:
    clauses = []
    for clause_set in clause_sets:
        clauses.extend(clause_set.clauses)
    return ClauseSetSchema(clauses=clauses)

def _check_one_statement(statement_name: str, statement_text: str, reference_clauses: ClauseSetSchema):
    chain, parser = build_json_chain(
        "Check one valid complaint statement against exact clauses and requirements from the supplied reference documents. Output JSON only. Use only the supplied clauses. Return source-backed matches wherever any clause is relevant.",
        "Complaint statement name: {statement_name}\nComplaint statement text:\n{statement_text}\n\nReference clauses and requirements:\n{reference_clauses}\n\nTask:\n1. Compare the complaint statement to every supplied reference clause or requirement.\n2. Return all clauses that are directly relevant, partly relevant, or potentially conflicting.\n3. For each returned match, preserve source_type, source_name, clause_reference, and clause_text exactly from the supplied clause.\n4. Use match_status values such as Directly relevant, Partly relevant, Not addressed, or Potential conflict.\n5. If no exact clause applies, explain that in conclusion and list what must be verified instead of inventing a clause.\n\nFormat:\n{format_instructions}",
        StatementCheckSchema,
    )
    payload = {
        "statement_name": statement_name,
        "statement_text": statement_text,
        "reference_clauses": [item.model_dump() for item in reference_clauses.clauses],
        "format_instructions": parser.get_format_instructions(),
    }
    result = safe_llm_invoke(chain, payload, StatementCheckSchema)
    if result and not result.complaint_statement:
        result.complaint_statement = statement_text
    return result

def check_complaint_statements(reference_clauses: ClauseSetSchema, complaint_statements: Dict[str, str]) -> List[StatementCheckSchema]:
    results = []
    with ThreadPoolExecutor(max_workers=settings.max_workers) as pool:
        futures = {
            pool.submit(_check_one_statement, name, text, reference_clauses): name
            for name, text in complaint_statements.items()
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    return sorted(results, key=lambda item: item.statement_name.lower())
