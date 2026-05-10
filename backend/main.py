import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env from backend directory (must be before imports)
load_dotenv(Path(__file__).parent / ".env")

from backend.routes.api import router as api_router
from backend.routes.auth import router as auth_router

app = FastAPI(
    title="PCD IDS Dashboard API",
    description="Intrusion Detection System API with Machine Learning",
    version="0.2.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API Router
app.include_router(api_router)
app.include_router(auth_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
