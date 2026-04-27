from datetime import datetime, timedelta
import random

# Mock database for dashboard
traffic_logs = []
alerts = []

def generate_mock_data():
    """Generates initial mock data for the dashboard"""
    now = datetime.now()
    for i in range(50):
        timestamp = now - timedelta(minutes=i*15)
        log = {
            "id": f"log-{i}",
            "timestamp": timestamp.isoformat(),
            "source_ip": f"192.168.1.{random.randint(2, 254)}",
            "dest_ip": f"10.0.0.{random.randint(1, 100)}",
            "protocol": random.choice(["TCP", "UDP", "ICMP"]),
            "bytes": random.randint(100, 15000),
            "status": random.choice(["ALLOWED", "BLOCKED", "ALLOWED"])
        }
        traffic_logs.append(log)
        
        if random.random() < 0.1:
            alerts.append({
                "id": f"alert-{i}",
                "timestamp": timestamp.isoformat(),
                "severity": random.choice(["HIGH", "CRITICAL"]),
                "source_ip": log["source_ip"],
                "type": random.choice(["DDoS Attempt", "Port Scan", "Malware C2"]),
                "status": "UNRESOLVED"
            })

generate_mock_data()

class DashboardService:
    def get_stats(self):
        total_traffic = sum(log["bytes"] for log in traffic_logs)
        blocked_traffic = len([log for log in traffic_logs if log["status"] == "BLOCKED"])
        active_threats = len([a for a in alerts if a["status"] == "UNRESOLVED"])
        
        return {
            "total_traffic_bytes": total_traffic,
            "blocked_connections": blocked_traffic,
            "active_threats": active_threats,
            "system_health": "Degraded" if active_threats > 2 else "Healthy"
        }
        
    def get_alerts(self):
        return alerts[:10]
        
    def get_traffic_history(self):
        return traffic_logs[:20]

dashboard_service = DashboardService()
