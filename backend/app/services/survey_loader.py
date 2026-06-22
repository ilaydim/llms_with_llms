"""FR-8.1/8.2: Anket sorularını survey_config/questions.json'dan okur."""
import json
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings


@lru_cache
def load_survey_questions(survey_type: str) -> list[dict]:
    settings = get_settings()
    config_path = Path(settings.survey_config_dir) / "questions.json"
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if survey_type not in data:
        raise ValueError(f"Bilinmeyen anket tipi: {survey_type}")
    return data[survey_type]
