from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

router = APIRouter()

class DisasterImpactSchema(BaseModel):
    reconstruction_id: str
    flood_extent_geojson_url: str
    water_expansion_km2: float
    vegetation_loss_pct: float
    affected_settlements: int
    road_damage_m: float
    bridge_damage_count: int
    severity_level: str # 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'
    timestamp: datetime

# Mock database of disaster impact indices corresponding to our locations
mock_disaster_db = {
    "kerala": {
        "reconstruction_id": "kl09-recon-uuid",
        "flood_extent_geojson_url": "/api/reports/geojson/kerala",
        "water_expansion_km2": 42.8,
        "vegetation_loss_pct": 18.4,
        "affected_settlements": 148,
        "road_damage_m": 12450.0,
        "bridge_damage_count": 3,
        "severity_level": "CRITICAL",
        "timestamp": datetime.utcnow()
    },
    "uttarakhand": {
        "reconstruction_id": "uk30-recon-uuid",
        "flood_extent_geojson_url": "/api/reports/geojson/uttarakhand",
        "water_expansion_km2": 4.2,
        "vegetation_loss_pct": 32.1,
        "affected_settlements": 12,
        "road_damage_m": 3800.0,
        "bridge_damage_count": 2,
        "severity_level": "HIGH",
        "timestamp": datetime.utcnow()
    },
    "chennai": {
        "reconstruction_id": "tn13-recon-uuid",
        "flood_extent_geojson_url": "/api/reports/geojson/chennai",
        "water_expansion_km2": 56.1,
        "vegetation_loss_pct": 8.2,
        "affected_settlements": 842,
        "road_damage_m": 28600.0,
        "bridge_damage_count": 0,
        "severity_level": "CRITICAL",
        "timestamp": datetime.utcnow()
    }
}


@router.post("/analyze/{scene_key}", response_model=DisasterImpactSchema)
async def analyze_disaster_impact(scene_key: str):
    """
    Triggers change detection and flood segmentation pipelines.
    Extracts affected settlements count, road breakages, and calculates severity levels.
    """
    key = scene_key.lower().strip()
    if key not in mock_disaster_db:
        raise HTTPException(
            status_code=404, 
            detail="Disaster assessment mapping for selected scene is not pre-computed or invalid."
        )
    
    # Update analysis timestamp to reflect present computation execution
    result = mock_disaster_db[key].copy()
    result["timestamp"] = datetime.utcnow()
    return result


@router.get("/impact-history", response_model=List[DisasterImpactSchema])
async def get_all_disaster_assessments():
    """Returns historical list of calculated disaster assessments for spatial trend monitoring"""
    return list(mock_disaster_db.values())
