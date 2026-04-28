from backend.services.db import get_db_connection

class DashboardService:
    def get_stats(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(bytes) FROM traffic_logs")
        total_traffic = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM traffic_logs WHERE status = 'BLOCKED'")
        blocked_traffic = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE status = 'UNRESOLVED'")
        active_threats = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_traffic_bytes": total_traffic,
            "blocked_connections": blocked_traffic,
            "active_threats": active_threats,
            "system_health": "Degraded" if active_threats > 2 else "Healthy"
        }
        
    def get_alerts(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 10")
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return alerts
        
    def get_traffic_history(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM traffic_logs ORDER BY id DESC LIMIT 20")
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

dashboard_service = DashboardService()
