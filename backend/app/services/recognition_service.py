import uuid
from datetime import datetime
from typing import Dict, List, Optional
from backend.app.schemas.recognition import (
    PeerRecognitionCreate,
    PeerRecognitionResponse,
    RewardCatalogItemResponse,
    EmployeeWalletResponse,
    RewardRedemptionRequest,
    MilestoneEvent,
)


class RecognitionService:
    def __init__(self):
        self._recognitions: Dict[str, dict] = {}
        self._wallets: Dict[str, dict] = {}
        self._catalog: Dict[str, dict] = {}
        self._seed_default_data()

    def _seed_default_data(self):
        # Seed Wallets
        self._wallets["emp-001"] = {
            "employee_id": "emp-001",
            "points_balance": 350,
            "monthly_allowance_remaining": 150,
            "updated_at": datetime.utcnow(),
        }
        self._wallets["emp-002"] = {
            "employee_id": "emp-002",
            "points_balance": 520,
            "monthly_allowance_remaining": 200,
            "updated_at": datetime.utcnow(),
        }
        self._wallets["emp-003"] = {
            "employee_id": "emp-003",
            "points_balance": 180,
            "monthly_allowance_remaining": 100,
            "updated_at": datetime.utcnow(),
        }

        # Seed Catalog
        items = [
            {
                "id": "reward-01",
                "title": "$25 Amazon Digital Gift Card",
                "category": "GIFT_CARD",
                "points_cost": 250,
                "description": "Instant digital code redeemable for any product on Amazon.com.",
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=300",
            },
            {
                "id": "reward-02",
                "title": "Bose Noise-Cancelling Headphones",
                "category": "MERCHANDISE",
                "points_cost": 1200,
                "description": "Premium wireless noise-cancelling headphones for deep focus work.",
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300",
            },
            {
                "id": "reward-03",
                "title": "Company Swag Fleece & Thermos Kit",
                "category": "SWAG",
                "points_cost": 300,
                "description": "High-grade embroidered Patagonia fleece jacket and insulated Hydro Flask.",
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=300",
            },
            {
                "id": "reward-04",
                "title": "1 Extra Paid Wellness Day Off",
                "category": "PTO",
                "points_cost": 1500,
                "description": "1 additional fully-paid floating wellness day credited to your leave balance.",
                "is_available": True,
                "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=300",
            },
        ]
        for it in items:
            self._catalog[it["id"]] = it

        # Seed Recognitions Feed
        rec_1 = {
            "id": "rec-01",
            "sender_id": "emp-001",
            "recipient_id": "emp-002",
            "points": 50,
            "core_value": "DELIVER_RESULTS",
            "message": "Huge thanks for debugging the multi-tenant database connection pool under heavy load during the v1.5 rollout!",
            "is_public": True,
            "created_at": datetime(2026, 11, 19, 14, 20, 0),
        }
        rec_2 = {
            "id": "rec-02",
            "sender_id": "emp-003",
            "recipient_id": "emp-001",
            "points": 50,
            "core_value": "INNOVATION_EXCELLENCE",
            "message": "Outstanding work designing the zero-identifiability cryptographic hash architecture for our employee pulse surveys.",
            "is_public": True,
            "created_at": datetime(2026, 11, 21, 10, 15, 0),
        }
        self._recognitions[rec_1["id"]] = rec_1
        self._recognitions[rec_2["id"]] = rec_2

    def get_wallet(self, employee_id: str) -> EmployeeWalletResponse:
        if employee_id not in self._wallets:
            self._wallets[employee_id] = {
                "employee_id": employee_id,
                "points_balance": 100,
                "monthly_allowance_remaining": 200,
                "updated_at": datetime.utcnow(),
            }
        return EmployeeWalletResponse(**self._wallets[employee_id])

    def send_recognition(self, payload: PeerRecognitionCreate) -> PeerRecognitionResponse:
        # Check sender's monthly allowance
        sender_wallet = self.get_wallet(payload.sender_id)
        if sender_wallet.monthly_allowance_remaining < payload.points:
            raise ValueError(
                f"Insufficient monthly allowance. Remaining: {sender_wallet.monthly_allowance_remaining} points, requested: {payload.points} points."
            )

        # Deduct from sender's monthly allowance
        self._wallets[payload.sender_id]["monthly_allowance_remaining"] -= payload.points

        # Credit recipient's redeemable points balance
        recipient_wallet = self.get_wallet(payload.recipient_id)
        self._wallets[payload.recipient_id]["points_balance"] += payload.points
        self._wallets[payload.recipient_id]["updated_at"] = datetime.utcnow()

        rec_id = f"rec-{uuid.uuid4().hex[:8]}"
        record = {
            "id": rec_id,
            "sender_id": payload.sender_id,
            "recipient_id": payload.recipient_id,
            "points": payload.points,
            "core_value": payload.core_value,
            "message": payload.message,
            "is_public": payload.is_public,
            "created_at": datetime.utcnow(),
        }
        self._recognitions[rec_id] = record
        return PeerRecognitionResponse(**record)

    def list_recognitions(self, limit: int = 50) -> List[PeerRecognitionResponse]:
        sorted_recs = sorted(
            self._recognitions.values(),
            key=lambda x: str(x["created_at"]),
            reverse=True,
        )
        return [PeerRecognitionResponse(**r) for r in sorted_recs[:limit]]

    def list_rewards(self) -> List[RewardCatalogItemResponse]:
        return [RewardCatalogItemResponse(**it) for it in self._catalog.values() if it["is_available"]]

    def redeem_reward(self, payload: RewardRedemptionRequest) -> dict:
        item = self._catalog.get(payload.reward_item_id)
        if not item or not item["is_available"]:
            raise ValueError("Reward catalog item is not available or does not exist.")

        wallet = self.get_wallet(payload.employee_id)
        if wallet.points_balance < item["points_cost"]:
            raise ValueError(
                f"Insufficient points. Required: {item['points_cost']}, current balance: {wallet.points_balance}."
            )

        # Deduct points
        self._wallets[payload.employee_id]["points_balance"] -= item["points_cost"]
        self._wallets[payload.employee_id]["updated_at"] = datetime.utcnow()

        redemption_code = f"RWD-{uuid.uuid4().hex[:8].upper()}"
        return {
            "success": True,
            "redemption_code": redemption_code,
            "reward_title": item["title"],
            "points_deducted": item["points_cost"],
            "remaining_balance": self._wallets[payload.employee_id]["points_balance"],
            "message": f"Congratulations! You have successfully redeemed '{item['title']}'. Redemption claim code: {redemption_code}.",
        }

    def list_upcoming_milestones(self) -> List[MilestoneEvent]:
        # Synthesizes employee milestones and calculated awards
        return [
            MilestoneEvent(
                employee_id="emp-001",
                employee_name="Alex Chen",
                milestone_type="WORK_ANNIVERSARY",
                milestone_date="2026-12-01",
                anniversary_years=3,
                suggested_award_points=300,
            ),
            MilestoneEvent(
                employee_id="emp-002",
                employee_name="Sarah Miller",
                milestone_type="WORK_ANNIVERSARY",
                milestone_date="2026-12-15",
                anniversary_years=5,
                suggested_award_points=500,
            ),
            MilestoneEvent(
                employee_id="emp-003",
                employee_name="David Patel",
                milestone_type="BIRTHDAY",
                milestone_date="2026-11-28",
                anniversary_years=None,
                suggested_award_points=100,
            ),
        ]


recognition_service = RecognitionService()
