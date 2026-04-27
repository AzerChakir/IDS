import os

class ResponderService:
    def __init__(self):
        self.blocked_ips = set()
        
    def block_ip(self, ip_address: str):
        """Block an IP address (mock action)."""
        self.blocked_ips.add(ip_address)
        return {"status": "success", "message": f"IP {ip_address} blocked."}
        
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address (mock action)."""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
        return {"status": "success", "message": f"IP {ip_address} unblocked."}
        
    def get_blocked_ips(self):
        return list(self.blocked_ips)

responder = ResponderService()
