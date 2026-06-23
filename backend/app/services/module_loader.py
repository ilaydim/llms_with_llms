"""
FR-1.1: Sistem her modülü tutarlı bir yapılandırma formatında (JSON) okur;
yeni modül eklemek kod değişikliği değil, yeni bir config dosyası eklemek demektir.
FR-1.3: Tutor Agent sistem promptunu bu yapılandırmadan dinamik üretir.
"""
import json
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings


@lru_cache
def load_module_config(module_code: str) -> dict:
    """Verilen modül kodu için config JSON'unu yükler (örn. 'rag' -> modules_config/rag.json)."""
    settings = get_settings()
    config_path = Path(settings.modules_config_dir) / f"{module_code}.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Modül yapılandırma dosyası bulunamadı: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_tutor_system_prompt(module_config: dict, layer: str) -> str:
    """
    FR-1.3: Aktif modülün config'inden, o anki katmana (theory/application/critical)
    özel bir sistem promptu üretir. Konuşmanın modül kapsamı dışına taşmasını
    azaltmak (Bölüm 5.5 — scope drift) burada ele alınır.
    """
    persona = module_config.get("tutor_persona", "")
    layer_context = ""

    if layer == "theory":
        objectives = module_config["theory"].get("learning_objectives", [])
        layer_context = (
            "You are currently in the Theory layer. Help the student achieve the following learning objectives:\n- "
            + "\n- ".join(objectives)
        )
    elif layer == "application":
        layer_context = (
            "You are currently in the Application layer. Task: "
            + module_config["application"]["task_description"]
            + " Use the search_documents tool when needed to actually trigger retrieval (FR-4.1)."
        )
    elif layer == "critical":
        layer_context = (
            "You are currently in the Critical Thinking layer. Discussion starter: "
            + module_config["critical"]["discussion_starter"]
        )

    return f"{persona}\n\n{layer_context}"
