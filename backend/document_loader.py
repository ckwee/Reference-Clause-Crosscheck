import os
import tempfile
import logging
from fastapi import UploadFile, HTTPException
import docx2txt
from langchain_community.document_loaders import PyMuPDFLoader

from config import settings

logger = logging.getLogger("document_loader")

def _validate_upload(file: UploadFile):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {ext}")

    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)
    if size_bytes / (1024 * 1024) > settings.max_file_size_mb:
        raise HTTPException(status_code=400, detail="File too large")

def load_document_secure(file: UploadFile) -> str:
    _validate_upload(file)
    ext = os.path.splitext(file.filename or "")[1].lower()

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(file.file.read())
            temp_path = tmp.name

        if ext == ".pdf":
            loader = PyMuPDFLoader(temp_path)
            pages = loader.load()
            text = "\n".join([p.page_content for p in pages])

        elif ext == ".docx":
            text = docx2txt.process(temp_path)

        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

        cleaned = (text or "").strip()
        if not cleaned:
            raise HTTPException(status_code=400, detail="Empty document")

        return cleaned

    except Exception as e:
        logger.exception(f"Error loading document: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document")

    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass
