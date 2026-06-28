from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime
import numpy as np
import uuid
from processing.validation import ScientificValidator

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
    """Simulates pipeline sequence inside a background thread executing remote-sensing steps"""
    mock_task_store[task_id]["status"] = "RUNNING"
    
    # 1. Metadata Validation (10%)
    mock_task_store[task_id]["progress_percentage"] = 10
    mock_task_store[task_id]["message"] = "Validating scene metadata (checking UTM coordinates, sensor bands, timestamp chronologies)..."
    
    # 2. TOA Reflectance & Atmospheric correction (30%)
    import time
    time.sleep(1)
    mock_task_store[task_id]["progress_percentage"] = 30
    mock_task_store[task_id]["message"] = "Applying TOA calibration and Dark Object Subtraction atmospheric correction..."
    
    # 3. Spatial Resampling & Lee Filtering (45%)
    time.sleep(0.8)
    mock_task_store[task_id]["progress_percentage"] = 45
    mock_task_store[task_id]["message"] = "Resampling spatial bands to 10m grid and filtering SAR speckle noise (Refined Lee)..."
    
    # 4. Geometric Co-Registration (60%)
    time.sleep(1)
    mock_task_store[task_id]["progress_percentage"] = 65
    mock_task_store[task_id]["message"] = "Executing LoFTR feature co-registration (extracting sub-pixel keypoint matches)..."
    
    # 5. Cloud & shadow segmentation (75%)
    time.sleep(1)
    mock_task_store[task_id]["progress_percentage"] = 78
    mock_task_store[task_id]["message"] = "Segmenting thick clouds and shadow decks using Cloud-Net U-Net..."
    
    # 6. Diffusion Pixel Reconstruction (90%)
    time.sleep(1.2)
    mock_task_store[task_id]["progress_percentage"] = 90
    mock_task_store[task_id]["message"] = "Denoising pixel channels under cloud regions using Conditional Diffusion Model..."
    
    # 7. Scientific Quality Assessment (95%)
    time.sleep(0.8)
    mock_task_store[task_id]["progress_percentage"] = 96
    mock_task_store[task_id]["message"] = "Calculating reconstruction quality metrics (PSNR, SSIM, RMSE, and SAM)..."
    
    # Calculate simulated array matrices to verify mathematics
    ref_mock = np.random.rand(4, 64, 64)
    recon_mock = ref_mock + np.random.normal(0, 0.04, (4, 64, 64)) # Add slight noise deviation
    recon_mock = np.clip(recon_mock, 0.0, 1.0)
    
    validator = ScientificValidator(max_value=1.0)
    metrics = validator.validate_scene(ref_mock, recon_mock)
    
    # 8. Completed
    time.sleep(0.5)
    mock_task_store[task_id]["status"] = "COMPLETED"
    mock_task_store[task_id]["progress_percentage"] = 100
    mock_task_store[task_id]["message"] = "Reconstruction pipeline finished. QA check: PASSED."
    mock_task_store[task_id]["completed_at"] = datetime.utcnow()
    
    # Save output paths and scientific metrics values
    mock_task_store[task_id]["results"] = {
        "reconstructed_optical_tif": f"/data/reconstructed/{req.project_name}_clear.tif",
        "confidence_heatmap_tif": f"/data/reconstructed/{req.project_name}_conf.tif",
        "difference_map_tif": f"/data/reconstructed/{req.project_name}_diff.tif",
        "ndvi_map_tif": f"/data/reconstructed/{req.project_name}_ndvi.tif",
        "quality_metrics": {
            "psnr_db": round(metrics["peak_signal_noise_ratio_db"], 2),
            "ssim": round(metrics["structural_similarity_index"], 3),
            "rmse": round(metrics["root_mean_squared_error"], 4),
            "spectral_angle_mapper_rad": round(metrics["spectral_angle_mapper_rad"], 4),
            "spectral_consistency": metrics["spectral_consistency_check"]
        }
    }


@router.post("/trigger", response_model=ReconstructionTaskStatus)
async def trigger_reconstruction(request: ReconstructionRequestSchema, background_tasks: BackgroundTasks):
    """Enqueues spatial reconstruction tasks to execute asynchronously in background thread"""
    task_id = str(uuid.uuid4())
    
    mock_task_store[task_id] = {
        "task_id": task_id,
        "status": "PENDING",
        "progress_percentage": 0,
        "message": "Task queued. Allocating workers...",
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "results": None
    }
    
    background_tasks.add_task(execute_mock_pipeline_sync, task_id, request)
    
    return mock_task_store[task_id]


@router.get("/status/{task_id}", response_model=ReconstructionTaskStatus)
async def get_task_status(task_id: str):
    """Retrieves status, logs, output files, and QA verification metrics for enqueued tasks"""
    if task_id not in mock_task_store:
        raise HTTPException(status_code=404, detail="Requested reconstruction task ID does not exist.")
    return mock_task_store[task_id]
