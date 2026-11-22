from typing import List
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.recognition import (
    PeerRecognitionCreate,
    PeerRecognitionResponse,
    RewardCatalogItemResponse,
    EmployeeWalletResponse,
    RewardRedemptionRequest,
    MilestoneEvent,
)
from backend.app.services.recognition_service import recognition_service

router = APIRouter()


@router.get("/feed", response_model=List[PeerRecognitionResponse])
def get_recognition_feed(limit: int = Query(50, ge=1, le=100)):
    """Retrieve the public peer recognition activity feed."""
    return recognition_service.list_recognitions(limit=limit)


@router.post("/kudos", response_model=PeerRecognitionResponse, status_code=status.HTTP_201_CREATED)
def send_peer_kudos(payload: PeerRecognitionCreate):
    """Send kudos and discretionary reward points to a colleague."""
    try:
        return recognition_service.send_recognition(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallet/{employee_id}", response_model=EmployeeWalletResponse)
def get_employee_wallet(employee_id: str):
    """Get an employee's current points balance and monthly giving allowance."""
    return recognition_service.get_wallet(employee_id)


@router.get("/rewards", response_model=List[RewardCatalogItemResponse])
def list_rewards_catalog():
    """List available items in the company reward catalog."""
    return recognition_service.list_rewards()


@router.post("/redeem")
def redeem_reward(payload: RewardRedemptionRequest):
    """Redeem reward points for merchandise, gift cards, or company perks."""
    try:
        return recognition_service.redeem_reward(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/milestones", response_model=List[MilestoneEvent])
def list_upcoming_milestones():
    """List upcoming employee milestones, work anniversaries, and suggested awards."""
    return recognition_service.list_upcoming_milestones()
