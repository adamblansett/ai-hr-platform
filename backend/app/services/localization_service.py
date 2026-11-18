import re
from datetime import date
from typing import Dict, List, Optional
from pydantic import BaseModel

class StatutoryHoliday(BaseModel):
    date: date
    name: str
    country_code: str # US, UK, DE, JP, CA
    is_mandatory_off: bool = True

class LocalizationService:
    """
    Global workforce localization service supporting:
    - Multilingual language detection & cross-lingual RAG prompt augmentation
    - Statutory public holiday calendars across jurisdictions
    """

    LANGUAGE_MAP = {
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "ja": "Japanese",
        "pt": "Portuguese",
        "zh": "Chinese",
        "en": "English",
    }

    HOLIDAYS_BY_COUNTRY: Dict[str, List[Dict[str, Any]]] = {
        "US": [
            {"month": 1, "day": 1, "name": "New Year's Day"},
            {"month": 1, "day": 19, "name": "Martin Luther King Jr. Day"},
            {"month": 5, "day": 25, "name": "Memorial Day"},
            {"month": 6, "day": 19, "name": "Juneteenth National Independence Day"},
            {"month": 7, "day": 4, "name": "Independence Day"},
            {"month": 9, "day": 7, "name": "Labor Day"},
            {"month": 11, "day": 26, "name": "Thanksgiving Day"},
            {"month": 12, "day": 25, "name": "Christmas Day"},
        ],
        "UK": [
            {"month": 1, "day": 1, "name": "New Year's Day"},
            {"month": 4, "day": 3, "name": "Good Friday"},
            {"month": 4, "day": 6, "name": "Easter Monday"},
            {"month": 5, "day": 4, "name": "Early May Bank Holiday"},
            {"month": 5, "day": 25, "name": "Spring Bank Holiday"},
            {"month": 8, "day": 31, "name": "Summer Bank Holiday"},
            {"month": 12, "day": 25, "name": "Christmas Day"},
            {"month": 12, "day": 26, "name": "Boxing Day"},
        ],
        "DE": [
            {"month": 1, "day": 1, "name": "Neujahr"},
            {"month": 5, "day": 1, "name": "Tag der Arbeit"},
            {"month": 10, "day": 3, "name": "Tag der Deutschen Einheit"},
            {"month": 12, "day": 25, "name": "1. Weihnachtstag"},
            {"month": 12, "day": 26, "name": "2. Weihnachtstag"},
        ],
        "JP": [
            {"month": 1, "day": 1, "name": "Ganjitsu (New Year)"},
            {"month": 5, "day": 3, "name": "Constitution Memorial Day"},
            {"month": 5, "day": 4, "name": "Greenery Day"},
            {"month": 5, "day": 5, "name": "Children's Day"},
            {"month": 8, "day": 11, "name": "Mountain Day"},
            {"month": 11, "day": 23, "name": "Labor Thanksgiving Day"},
        ]
    }

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Fast heuristic language detector. Defaults to 'en'.
        """
        # Spanish markers
        if re.search(r"\b(que|como|para|días|vacaciones|permiso|política|cuál|cuándo)\b", text, re.I):
            return "es"
        # French markers
        elif re.search(r"\b(que|pour|jours|congés|politique|comment|quand)\b", text, re.I):
            return "fr"
        # German markers
        elif re.search(r"\b(wie|für|urlaub|tage|richtlinie|wann|bitte)\b", text, re.I):
            return "de"
        # Japanese markers
        elif re.search(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]", text):
            return "ja"
        return "en"

    @staticmethod
    def get_statutory_holidays(country_code: str, year: int) -> List[StatutoryHoliday]:
        code = country_code.upper()
        raw_list = LocalizationService.HOLIDAYS_BY_COUNTRY.get(code, LocalizationService.HOLIDAYS_BY_COUNTRY["US"])
        
        holidays = []
        for h in raw_list:
            holidays.append(
                StatutoryHoliday(
                    date=date(year, h["month"], h["day"]),
                    name=h["name"],
                    country_code=code,
                    is_mandatory_off=True
                )
            )
        return holidays

    @staticmethod
    def augment_rag_prompt_for_language(system_prompt: str, detected_lang: str) -> str:
        if detected_lang == "en":
            return system_prompt

        lang_name = LocalizationService.LANGUAGE_MAP.get(detected_lang, "English")
        augmented = (
            f"{system_prompt}\n\n"
            f"IMPORTANT LOCALIZATION INSTRUCTION:\n"
            f"The employee is asking in {lang_name}. You MUST formulate your entire response in {lang_name}, "
            f"while preserving exact policy source citation tags like [Source X: Title]."
        )
        return augmented

localization_service = LocalizationService()
