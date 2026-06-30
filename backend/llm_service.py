import json
import logging
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, ValidationError
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from config import settings

logger = logging.getLogger("llm_service")

def get_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        num_ctx=settings.llm_num_ctx,
        format="json",
        base_url=settings.ollama_base_url,
    )

def safe_llm_invoke(chain, payload: Dict[str, Any], model_cls: Type[BaseModel]):
    last_error = None
    for attempt in range(settings.llm_max_retries):
        try:
            raw = chain.invoke(payload)

            if isinstance(raw, BaseModel):
                return raw

            if isinstance(raw, str):
                raw = json.loads(raw)

            return model_cls.model_validate(raw)

        except (ValidationError, ValueError, json.JSONDecodeError) as e:
            last_error = e
            logger.warning(f"LLM parse failed (attempt {attempt+1}): {e}")

    logger.error(f"LLM failed after retries: {last_error}")
    return None

def build_json_chain(system_prompt: str, user_template: str, model_cls: Type[BaseModel]):
    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=model_cls)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_template),
    ])
    return prompt | llm | parser, parser
