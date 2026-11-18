from datetime import date
from typing import List, Dict
from fastapi import APIRouter, Query
from backend.app.services.localization_service import localization_service, StatutoryHoliday

router = APIRouter()

@router.get("/holidays", response_model=List[StatutoryHoliday], summary="Get statutory public holidays for regional leave calculation")
async def get_statutory_holidays(
    country_code: str = Query("US", min_length=2, max_length=2),
    year: int = Query(default_factory=lambda: date.today().year)
):
    return localization_service.get_statutory_holidays(country_code, year)

@router.post("/detect-language", summary="Detect employee question language")
async def detect_language(payload: Dict[str, str]):
    text = payload.get("text", "")
    code = localization_service.detect_language(text)
    name = localization_service.LANGUAGE_MAP.get(code, "English")
    return {"language_code": code, "language_name": name}
