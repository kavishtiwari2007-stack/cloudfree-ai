from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from celery import Celery
from config import settings

# Initialize FastAPI App
app = FastAPI(
    title="CloudFreeAI API Gateway",
    description="Research-grade API for multi-temporal optical satellite reconstruction and disaster intelligence assessment.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware for frontend interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Celery Worker Client
celery_app = Celery(
    "cloudfree_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Root Endpoint
@app.get("/", tags=["Telemetry"])
async def root():
    return {
        "status": "ONLINE",
        "system": "CloudFreeAI Platform Core",
        "mission": "Bharatiya Antariksh Hackathon 2026",
        "documentation": "/docs"
    }

# Health Check Endpoint
@app.get("/health", tags=["Telemetry"])
async def health_check():
    return {
        "status": "HEALTHY",
        "database": "CONNECTED",
        "redis": "CONNECTED",
        "celery_workers": "ACTIVE"
    }

# Import and register API routers dynamically
from api.auth import router as auth_router
from api.datasets import router as datasets_router
from api.reconstruction import router as reconstruction_router
from api.disaster import router as disaster_router
from api.reports import router as reports_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(datasets_router, prefix="/api/datasets", tags=["Geospatial Datasets"])
app.include_router(reconstruction_router, prefix="/api/reconstruction", tags=["AI Image Reconstruction"])
app.include_router(disaster_router, prefix="/api/disaster", tags=["Disaster Assessment"])
app.include_router(reports_router, prefix="/api/reports", tags=["AI Reports & Export"])
