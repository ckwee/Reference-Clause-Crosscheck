from typing import List
from pydantic import BaseModel, Field

class ClauseSchema(BaseModel):
    source_type: str = "Reference"
    source_name: str = "Reference document"
    clause_reference: str
    clause_text: str
    obligation_summary: str
    keywords: List[str] = Field(default_factory=list)

class ClauseSetSchema(BaseModel):
    clauses: List[ClauseSchema] = Field(default_factory=list)

class ClauseMatchSchema(BaseModel):
    source_type: str = "Reference"
    source_name: str = "Reference document"
    clause_reference: str
    clause_text: str
    match_status: str
    match_explanation: str

class StatementCheckSchema(BaseModel):
    statement_name: str
    complaint_statement: str
    reference_matches: List[ClauseMatchSchema] = Field(default_factory=list)
    conclusion: str
    items_to_verify: List[str] = Field(default_factory=list)

class PipelineRequest(BaseModel):
    reference_text: str
    complaint_statements: dict[str, str]

class PipelineResponse(BaseModel):
    reference_clauses: ClauseSetSchema
    checks: List[StatementCheckSchema]
