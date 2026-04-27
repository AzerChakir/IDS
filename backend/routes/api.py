from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from backend.services.scorer import scorer
from backend.services.dashboard import dashboard_service

router = APIRouter(prefix="/api")

class TrafficData(BaseModel):
    features: Dict[str, Any]

@router.get("/dashboard/stats")
async def get_stats():
    return dashboard_service.get_stats()

@router.get("/dashboard/alerts")
async def get_alerts():
    return dashboard_service.get_alerts()

@router.get("/dashboard/history")
async def get_history():
    return dashboard_service.get_traffic_history()

@router.post("/analyze")
async def analyze_traffic(data: TrafficData):
    try:
        result = scorer.analyze_traffic(data.features)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
