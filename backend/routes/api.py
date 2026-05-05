import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from backend.services.scorer import scorer
from backend.services.dashboard import dashboard_service
from backend.services.llm_rag import llm_rag_service

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

from backend.services.db import get_db_connection
from datetime import datetime
import json

@router.post("/analyze")
async def analyze_traffic(data: TrafficData):
    try:
        result = scorer.analyze_traffic(data.features)
        
        # Log to database so it shows up on dashboard
        conn = get_db_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        source_ip = data.features.get("Source IP", "192.168.1.100")
        dest_ip = data.features.get("Destination IP", "10.0.0.50")
        protocol = data.features.get("Protocol", "TCP")
        bytes_count = data.features.get("Total Length of Fwd Packets", 500)
        
        is_anomaly = result.get("is_anomaly", False)
        status = "BLOCKED" if is_anomaly else "ALLOWED"
        
        # Insert traffic log
        cursor.execute(
            'INSERT INTO traffic_logs (timestamp, source_ip, dest_ip, protocol, bytes, status) VALUES (?, ?, ?, ?, ?, ?)',
            (timestamp, source_ip, dest_ip, protocol, bytes_count, status)
        )
        
        # If anomaly, create alert
        if is_anomaly:
            severity = "CRITICAL" if result.get("threat_score", 0) > 0.9 else "HIGH"
            cursor.execute(
                'INSERT INTO alerts (timestamp, severity, source_ip, type, description, status) VALUES (?, ?, ?, ?, ?, ?)',
                (timestamp, severity, source_ip, result.get("label", "Threat"), result.get("details", "Anomaly detected via API"), "UNRESOLVED")
            )
            
        conn.commit()
        conn.close()
        
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alert/{alert_id}/analyze")
async def analyze_alert_rag(alert_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type, description FROM alerts WHERE id = ?", (alert_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert_type = row["type"]
    alert_desc = row["description"]
    
    analysis = llm_rag_service.analyze_alert(alert_type, alert_desc)
    return {"status": "success", "analysis": analysis}
