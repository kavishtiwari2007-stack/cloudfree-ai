from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

router = APIRouter()

class DatasetMetadataSchema(BaseModel):
    id: int
    sensor: str
    acquisition_date: datetime
    cloud_cover: float
    resolution_m: float
    bounds: List[List[float]]
    download_url: str
    polarization: Optional[List[str]] = None

# Mock database of LISS-IV and SAR scenes matching our target locations
mock_dataset_archive = [
    {
        "id": 101,
        "sensor": "Resourcesat-2 LISS-IV",
        "acquisition_date": datetime(2026, 6, 20, 5, 30, 0),
        "cloud_cover": 78.4,
        "resolution_m": 5.8,
        "bounds": [[9.90, 76.23], [9.96, 76.30]],
        "download_url": "/api/datasets/download/RS2_L4_KL09.tif"
    },
    {
        "id": 102,
        "sensor": "Sentinel-1 SAR",
        "acquisition_date": datetime(2026, 6, 28, 12, 10, 0),
        "cloud_cover": 0.0,
        "resolution_m": 10.0,
        "bounds": [[9.90, 76.23], [9.96, 76.30]],
        "download_url": "/api/datasets/download/S1_SAR_KL09.tif",
        "polarization": ["VV", "VH"]
    },
    {
        "id": 201,
        "sensor": "Resourcesat-2 LISS-IV",
        "acquisition_date": datetime(2026, 6, 15, 6, 15, 0),
        "cloud_cover": 92.1,
        "resolution_m": 5.8,
        "bounds": [[30.71, 79.04], [30.76, 79.09]],
        "download_url": "/api/datasets/download/RS2_L4_UK30.tif"
    },
    {
        "id": 202,
        "sensor": "Sentinel-1 SAR",
        "acquisition_date": datetime(2026, 6, 28, 11, 45, 0),
        "cloud_cover": 0.0,
        "resolution_m": 10.0,
        "bounds": [[30.71, 79.04], [30.76, 79.09]],
        "download_url": "/api/datasets/download/S1_SAR_UK30.tif",
        "polarization": ["VV", "VH"]
    },
    {
        "id": 301,
        "sensor": "Resourcesat-2 LISS-IV",
        "acquisition_date": datetime(2026, 6, 25, 5, 45, 0),
        "cloud_cover": 85.0,
        "resolution_m": 5.8,
        "bounds": [[13.05, 80.23], [13.11, 80.30]],
        "download_url": "/api/datasets/download/RS2_L4_TN13.tif"
    },
    {
        "id": 302,
        "sensor": "Sentinel-1 SAR",
        "acquisition_date": datetime(2026, 6, 28, 12, 5, 0),
        "cloud_cover": 0.0,
        "resolution_m": 10.0,
        "bounds": [[13.05, 80.23], [13.11, 80.30]],
        "download_url": "/api/datasets/download/S1_SAR_TN13.tif",
        "polarization": ["VV", "VH"]
    }
]


@router.get("/search", response_model=List[DatasetMetadataSchema])
async def search_datasets(
    lat: float = Query(..., description="Latitude of AOI centroid"),
    lon: float = Query(..., description="Longitude of AOI centroid"),
    radius_km: float = Query(10.0, description="Spatial query radius")
):
    """Queries spatial archive for scenes intersecting the coordinate radius"""
    results = []
    
    # Filter datasets that enclose coordinate points (using simple box checks)
    for ds in mock_dataset_archive:
        b = ds["bounds"]
        if (b[0][0] <= lat <= b[1][0]) and (b[0][1] <= lon <= b[1][1]):
            results.append(ds)
            
    if not results:
        raise HTTPException(
            status_code=404, 
            detail="No matching LISS-IV or SAR satellite footprints found for the specified coordinates."
        )
    return results


@router.post("/download/{scene_id}")
async def trigger_scene_download(scene_id: int):
    """Simulates background ingestion task fetching products from ISRO Bhoonidhi mirrors"""
    scene = next((item for item in mock_dataset_archive if item["id"] == scene_id), None)
    if not scene:
        raise HTTPException(status_code=404, detail="Requested satellite product ID not found in catalog.")
        
    return {
        "status": "COMPLETED",
        "scene_id": scene_id,
        "sensor": scene["sensor"],
        "local_storage_path": f"/data/raw/{scene['sensor'].lower().replace(' ', '_')}_{scene_id}.tif",
        "bytes_ingested": 104857600, # 100MB
        "timestamp": datetime.utcnow()
    }
