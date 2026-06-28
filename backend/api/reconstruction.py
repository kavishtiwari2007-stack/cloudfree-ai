from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import uuid

router = APIRouter()

class ReconstructionRequestSchema(BaseModel):
    project_name: str
    cloudy_id: int
    historical_id: int
    sar_id: int
    config: Optional[Dict] = {
        "model_reconstruction": "diffusion",
        "model_cloud": "unet",
        "model_registration": "loftr",
        "spectral_consistency": True,
        "toa_calibration": True
    }

class ReconstructionTaskStatus(BaseModel):
    task_id: str
    status: str
    progress_percentage: int
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict] = None

# Thread-safe database for task execution states
mock_task_store: Dict[str, Dict] = {}


def execute_mock_pipeline_sync(task_id: str, req: ReconstructionRequestSchema):
    """Simulates pipeline sequence inside a background thread"""
    mock_task_store[task_id]["status"] = "RUNNING"
    
    # 1. Preprocessing (10%)
    mock_task_store[task_id]["progress_percentage"] = 15
    mock_task_store[task_id]["message"] = "TOA Calibrating and orthorectifying scene datasets..."
    
    # 2. Registration (35%)
    import time
    time.sleep(1)
    mock_task_store[task_id]["progress_percentage"] = 40
    mock_task_store[task_id]["message"] = "Co-registering scene features using LoFTR..."
    
    # 3. Cloud Detection (60%)
    time.sleep(1)
    mock_task_store[task_id]["progress_percentage"] = 65
    mock_task_store[task_id]["message"] = "Generating cloud and shadow masks (U-Net)..."
    
    # 4. Deep Learning Synthesis (90%)
    time.sleep(1.5)
    mock_task_store[task_id]["progress_percentage"] = 90
    mock_task_store[task_id]["message"] = "Running Temporal Fusion Transformer and Diffusion generator..."
    
    # 5. Completed
    time.sleep(1)
    mock_task_store[task_id]["status"] = "COMPLETED"
    mock_task_store[task_id]["progress_percentage"] = 100
    mock_task_store[task_id]["message"] = "Reconstruction completed successfully."
    mock_task_store[task_id]["completed_at"] = datetime.utcnow()
    
    # Paths for generated raster layers
    mock_task_store[task_id]["results"] = {
        "reconstructed_optical_tif": f"/data/reconstructed/{req.project_name}_clear.tif",
        "confidence_heatmap_tif": f"/data/reconstructed/{req.project_name}_conf.tif",
        "difference_map_tif": f"/data/reconstructed/{req.project_name}_diff.tif",
        "ndvi_map_tif": f"/data/reconstructed/{req.project_name}_ndvi.tif",
        "metrics": {
            "psnr_db": 29.45,
            "ssim": 0.912,
            "spectral_angle_mapper_rad": 0.038
        }
    }


@router.post("/trigger", response_model=ReconstructionTaskStatus)
async def trigger_reconstruction(request: ReconstructionRequestSchema, background_tasks: BackgroundTasks):
    """Enqueues image reconstruction pipeline tasks to run asynchronously in the background"""
    task_id = str(uuid.uuid4())
    
    mock_task_store[task_id] = {
        "task_id": task_id,
        "status": "PENDING",
        "progress_percentage": 0,
        "message": "Task queued. Waiting for worker allocation...",
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "results": None
    }
    
    # Execute simulated Celery worker task asynchronously
    background_tasks.add_task(execute_mock_pipeline_sync, task_id, request)
    
    return mock_task_store[task_id]


@router.get("/status/{task_id}", response_model=ReconstructionTaskStatus)
async def get_task_status(task_id: str):
    """Polls progress percentage, state logging, and final output paths for an enqueued task"""
    if task_id not in mock_task_store:
        raise HTTPException(status_code=404, detail="Requested reconstruction task ID does not exist.")
    return mock_task_store[task_id]
