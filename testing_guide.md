# PCD IDS — Testing & Manipulation Guide

This guide describes how to interact with the Intrusion Detection System, simulate real-world attacks using Kali Linux, verify the API endpoints, and manipulate the application's underlying database.

---

## 1. Simulating Attacks (Kali Linux)

To see the machine learning model in action, you can generate malicious traffic against the server where the backend is running. The IDS network capture interface (or the `/api/analyze` endpoint) will process this traffic, and it will appear on your Dashboard.

### A. HTTP Flood / DDoS (Slowloris)
Use `slowloris` to simulate a denial-of-service attack against the web server.
```bash
# Install slowloris on Kali if not present
sudo apt-get install slowloris

# Execute attack against the target IP (replace <TARGET_IP> with your server IP)
slowloris <TARGET_IP> -p 80 -s 500
```
*Expected Result on Dashboard:* A spike in connections, triggering a **CRITICAL** "DDoS Attempt" alert.

### B. SSH Brute Force (Hydra)
Use `hydra` to perform a dictionary attack on the SSH port.
```bash
# Execute SSH brute force
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://<TARGET_IP>
```
*Expected Result on Dashboard:* Multiple repeated connection attempts leading to a **HIGH** "Brute Force SSH" alert.

### C. Network Scanning (Nmap)
Perform an aggressive port scan to map the network.
```bash
# Aggressive SYN stealth scan
sudo nmap -sS -A -p- <TARGET_IP>
```
*Expected Result on Dashboard:* A surge of small packets across various ports triggering a **MEDIUM** or **HIGH** "Port Scan" alert.

---

## 2. Using the Authentication API

The application now uses a persistent SQLite database to verify credentials. The Auth API accepts a standard POST request with a JSON payload.

### API Endpoint details
- **URL:** `POST http://localhost:8000/api/auth/login`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

### Testing with cURL
```bash
curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
```

**Successful Response:**
```json
{
  "status": "success",
  "token": "mock-jwt-token-123",
  "role": "admin"
}
```

---

## 3. Accessing & Manipulating the Database

The system has been upgraded to persist data. Instead of holding traffic and alerts in memory, everything is stored in a local SQLite database file. 

### Database Location
The database is located at: `data/ids_database.db` (relative to the project root). If running via Docker, this directory can be volume mapped to your host machine for live editing.

### Connecting to the Database
Because it uses standard SQLite3, it is highly accessible. You can manipulate the database using any SQLite client:
1. **DB Browser for SQLite:** Open `data/ids_database.db` using the GUI application to view tables, modify alerts, or add new users.
2. **Command Line (SQLite3 CLI):**
```bash
# Open the database
sqlite3 data/ids_database.db

# View all tables
sqlite> .tables
# output: alerts  traffic_logs  users

# Add a new administrator user
sqlite> INSERT INTO users (username, password, role) VALUES ('security_analyst', 'securepass1!', 'analyst');

# Mark an alert as resolved manually
sqlite> UPDATE alerts SET status = 'RESOLVED' WHERE id = 1;

# Exit
sqlite> .quit
```

When you update the database directly, the changes will immediately reflect on the React Frontend dashboard the next time it auto-refreshes (every 5 seconds).
