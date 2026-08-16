import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.models.scan import Scan
from app.routes.audit import router as audit_router
from app.routes.scans import router as scans_router


load_dotenv()


app = FastAPI(
    title="ContractShield API",
    description="AI-powered smart contract security auditor",
    version="1.0.0",
)


# Create database tables
Base.metadata.create_all(bind=engine)


# CORS
frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000",
)

allowed_origins = [
    "http://localhost:3000",
]

if frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scans_router)
app.include_router(audit_router)


@app.get("/")
def root():
    return {
        "message": "ContractShield API is running"
    }