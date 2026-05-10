import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from ai.engine import scorer
from backend.services.dashboard import dashboard_service
from backend.services.llm_rag import llm_rag_service

router = APIRouter(prefix="/api")

class TrafficData(BaseModel):
    features: Dict[str, Any]

class BlacklistIP(BaseModel):
    ip: str

class WhitelistIP(BaseModel):
    ip: str

class IsolateIP(BaseModel):
    ip: str

@router.post("/blacklist")
async def blacklist_ip(data: BlacklistIP):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO blacklisted_ips (ip, timestamp) VALUES (?, ?)",
            (data.ip, datetime.now().isoformat())
        )
        conn.commit()
        return {"status": "success", "message": f"IP {data.ip} blacklisted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.delete("/blacklist/{ip}")
async def unblacklist_ip(ip: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM blacklisted_ips WHERE ip = ?", (ip,))
        conn.commit()
        return {"status": "success", "message": f"IP {ip} unblacklisted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/whitelist")
async def whitelist_ip(data: WhitelistIP):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO whitelisted_ips (ip, timestamp) VALUES (?, ?)",
            (data.ip, datetime.now().isoformat())
        )
        conn.commit()
        return {"status": "success", "message": f"IP {data.ip} whitelisted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.delete("/whitelist/{ip}")
async def unwhitelist_ip(ip: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM whitelisted_ips WHERE ip = ?", (ip,))
        conn.commit()
        return {"status": "success", "message": f"IP {ip} removed from whitelist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/isolate")
async def isolate_destination(data: IsolateIP):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO isolated_destinations (ip, timestamp) VALUES (?, ?)",
            (data.ip, datetime.now().isoformat())
        )
        conn.commit()
        return {"status": "success", "message": f"Destination {data.ip} isolated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.delete("/isolate/{ip}")
async def unisolate_destination(ip: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM isolated_destinations WHERE ip = ?", (ip,))
        conn.commit()
        return {"status": "success", "message": f"Destination {ip} unisolated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

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
        source_ip = data.features.get("Source IP", "192.168.1.100")
        dest_ip = data.features.get("Destination IP", "10.0.0.50")
        
        # Priority 1: Check if Destination is Isolated
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ip FROM isolated_destinations WHERE ip = ?", (dest_ip,))
        is_isolated = cursor.fetchone() is not None
        
        if is_isolated:
            result = {
                "is_anomaly": True,
                "threat_score": 1.0,
                "label": "Isolating Response",
                "details": f"Traffic blocked: Destination {dest_ip} is currently under isolation lockdown."
            }
        else:
            # Priority 2: Check if Source is Whitelisted
            cursor.execute("SELECT ip FROM whitelisted_ips WHERE ip = ?", (source_ip,))
            is_whitelisted = cursor.fetchone() is not None
            
            if is_whitelisted:
                result = {
                    "is_anomaly": False,
                    "threat_score": 0.0,
                    "label": "Whitelisted Source",
                    "details": f"Traffic allowed: Source {source_ip} is on the trusted whitelist."
                }
            else:
                # Priority 3: Check if Source is Blacklisted
                cursor.execute("SELECT ip FROM blacklisted_ips WHERE ip = ?", (source_ip,))
                is_blacklisted = cursor.fetchone() is not None
                
                if is_blacklisted:
                    result = {
                        "is_anomaly": True,
                        "threat_score": 1.0,
                        "label": "Blacklisted IP",
                        "details": f"Connection rejected: IP {source_ip} is on the permanent blacklist."
                    }
                else:
                    # Priority 4: Run AI Scorer
                    result = scorer.analyze_traffic(data.features)
        
        conn.close()
        
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
