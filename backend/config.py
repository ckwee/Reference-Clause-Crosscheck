import os
from pydantic import BaseModel

class Settings(BaseModel):
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_model: str = os.getenv("LLM_MODEL", "llama3.1")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    llm_num_ctx: int = int(os.getenv("LLM_NUM_CTX", "16384"))
    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "3"))

    max_file_size_mb: float = float(os.getenv("MAX_FILE_SIZE_MB", "10"))
    allowed_extensions: set = {".pdf", ".docx"}

    max_workers: int = int(os.getenv("MAX_WORKERS", "4"))
    database_path: str = os.getenv("DATABASE_PATH", "data/compliance_reviews.db")

settings = Settings()