import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.db import get_db_connection

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginData):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hash the incoming password to compare with the stored hash
    hashed_password = hashlib.sha256(data.password.encode()).hexdigest()
    
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (data.username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"status": "success", "token": "mock-jwt-token-123", "role": user["role"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")
