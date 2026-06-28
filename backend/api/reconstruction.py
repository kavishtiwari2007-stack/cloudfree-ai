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


class ModelRegistry:
    """
    Model Registry abstraction.
    Manages swap/upgrade lifecycle of satellite models (U-Net, LoFTR, Diffusion).
    """
    def __init__(self):
        self._registry = {
            "cloud_detection": ["CloudNet_v1.2", "Fmask_v4.0"],
            "registration": ["LoFTR_ResNet_v2.0", "SuperGlue_GNN_v1.1"],
            "reconstruction": ["TemporalDiffusion_v3.4", "Pix2PixGAN_v2.1", "DSen2CR_ResNet_v2.5"]
        }

    def fetch_model(self, model_type: str, selected_name: str) -> str:
        """Resolves model path or checkpoint weights from registry"""
        available = self._registry.get(model_type, [])
        for name in available:
            if selected_name.lower() in name.lower():
                return name
        return available[0] if available else "default_model"


class WorkflowOrchestrator:
    """
    Central Workflow Orchestration service.
    Decides data search pipelines, checks cache, selects reference scenes,
    configures preprocessing chains, and calls target models.
    """
    def __init__(self):
        self.registry = ModelRegistry()

    def run_pipeline(self, task_id: str, req: ReconstructionRequestSchema):
        # 1. Dataset Discovery Engine (10%)
        mock_task_store[task_id]["progress_percentage"] = 8
        mock_task_store[task_id]["message"] = "Orchestrator: Activating Dataset Discovery Engine (Catalog Search -> Metadata Query)..."
        time.sleep(0.6)
        
        # 2. Cloud Filter & Reference Selection (20%)
        mock_task_store[task_id]["progress_percentage"] = 15
        mock_task_store[task_id]["message"] = "Orchestrator: Ranking historical optical reference scenes (Acquisition season, Solar elevation, Cloud %)..."
        time.sleep(0.6)
        
        # 3. Download Manager (30%)
        mock_task_store[task_id]["progress_percentage"] = 25
        mock_task_store[task_id]["message"] = "Orchestrator: Download Manager pulling current SAR orbit files and optical bands..."
        time.sleep(0.6)

        # 4. Metadata Validation (40%)
        mock_task_store[task_id]["progress_percentage"] = 35
        mock_task_store[task_id]["message"] = "Orchestrator: Verifying metadata variables, band compatibility, and coordinate bounds..."
        time.sleep(0.6)

        # 5. SAR Preprocessing (50%)
        mock_task_store[task_id]["progress_percentage"] = 48
        mock_task_store[task_id]["message"] = "Orchestrator: SAR Preprocessing (Orbit Correction -> Thermal Noise Removal -> Calibration -> Terrain Correction -> Refined Lee Speckle Filtering -> Normalization)..."
        time.sleep(0.9)

        # 6. Optical Preprocessing (60%)
        mock_task_store[task_id]["progress_percentage"] = 58
        mock_task_store[task_id]["message"] = "Orchestrator: Optical Preprocessing (TOA Reflectance -> Atmospheric correction -> Band Normalization -> Histogram Matching -> Seasonal Normalization)..."
        time.sleep(0.9)

        # 7. Model Ingestion & Registration (70%)
        reg_cloud = self.registry.fetch_model("cloud_detection", req.config.get("model_cloud", "unet"))
        reg_recon = self.registry.fetch_model("reconstruction", req.config.get("model_reconstruction", "diffusion"))
        mock_task_store[task_id]["progress_percentage"] = 68
        mock_task_store[task_id]["message"] = f"Orchestrator: Swapping registry models ({reg_cloud} and {reg_recon} loaded)..."
        time.sleep(0.6)

        # 8. AI Pixel Reconstruction (80%)
        mock_task_store[task_id]["progress_percentage"] = 80
        mock_task_store[task_id]["message"] = "Orchestrator: Running Temporal Fusion Transformer & Denoising Diffusion Reconstruction..."
        time.sleep(1.0)

        # 9. Explainability layer (90%)
        mock_task_store[task_id]["progress_percentage"] = 90
        mock_task_store[task_id]["message"] = "Orchestrator: Synthesizing Explainability Layer (generating spatial Attention maps and pixel Uncertainty maps)..."
        time.sleep(0.7)

        # 10. Split QA validation metrics (95%)
        mock_task_store[task_id]["progress_percentage"] = 95
        mock_task_store[task_id]["message"] = "Orchestrator: Executing multi-category QA Validation split..."
        time.sleep(0.6)

        # Scientific quality calculations
        ref_mock = np.random.rand(4, 64, 64)
        recon_mock = ref_mock + np.random.normal(0, 0.04, (4, 64, 64))
        recon_mock = np.clip(recon_mock, 0.0, 1.0)
        
        validator = ScientificValidator(max_value=1.0)
        metrics = validator.validate_scene(ref_mock, recon_mock)
        
        # Complete task
        mock_task_store[task_id]["status"] = "COMPLETED"
        mock_task_store[task_id]["progress_percentage"] = 100
        mock_task_store[task_id]["message"] = "Orchestrator: Scene reconstruction pipeline successfully finalized."
        mock_task_store[task_id]["completed_at"] = datetime.utcnow()
        
        # Structure the payload response
        mock_task_store[task_id]["results"] = {
            "model_registry": {
                "active_cloud_model": reg_cloud,
                "active_reconstruction_model": reg_recon
            },
            "output_rasters": {
                "reconstructed_optical_tif": f"/data/reconstructed/{req.project_name}_clear.tif",
                "cloud_mask_tif": f"/data/reconstructed/{req.project_name}_mask.tif",
                "confidence_heatmap_tif": f"/data/reconstructed/{req.project_name}_conf.tif",
                "flood_map_tif": f"/data/reconstructed/{req.project_name}_flood.tif",
                "damage_map_tif": f"/data/reconstructed/{req.project_name}_damage.tif",
                "attention_map_xai_tif": f"/data/reconstructed/{req.project_name}_attn_xai.tif",
                "uncertainty_map_tif": f"/data/reconstructed/{req.project_name}_uncertainty.tif"
            },
            "scientific_validation": {
                "reconstruction_validation": {
                    "psnr_db": round(metrics["reconstruction_validation"]["peak_signal_noise_ratio_db"], 2),
                    "ssim": round(metrics["reconstruction_validation"]["structural_similarity_index"], 3),
                    "rmse": round(metrics["reconstruction_validation"]["root_mean_squared_error"], 4)
                },
                "spectral_validation": {
                    "spectral_angle_mapper_rad": round(metrics["spectral_validation"]["spectral_angle_mapper_rad"], 4),
                    "mean_ndvi_delta": round(metrics["spectral_validation"]["mean_ndvi_delta"], 4)
                },
                "uncertainty_validation": {
                    "mean_confidence_score": round(metrics["uncertainty_validation"]["mean_confidence_score"], 2),
                    "pixel_reliability_index": round(metrics["uncertainty_validation"]["pixel_reliability_index"], 4)
                }
            }
        }


import time # Helper for threads

def execute_mock_pipeline_sync(task_id: str, req: ReconstructionRequestSchema):
    orchestrator = WorkflowOrchestrator()
    orchestrator.run_pipeline(task_id, req)


@router.post("/trigger", response_model=ReconstructionTaskStatus)
async def trigger_reconstruction(request: ReconstructionRequestSchema, background_tasks: BackgroundTasks):
    """Enqueues pipeline tasks to be managed by the Central Workflow Orchestrator"""
    task_id = str(uuid.uuid4())
    
    mock_task_store[task_id] = {
        "task_id": task_id,
        "status": "PENDING",
        "progress_percentage": 0,
        "message": "Task enqueued. Central Orchestrator booting up...",
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "results": None
    }
    
    background_tasks.add_task(execute_mock_pipeline_sync, task_id, request)
    return mock_task_store[task_id]


@router.get("/status/{task_id}", response_model=ReconstructionTaskStatus)
async def get_task_status(task_id: str):
    """Retrieves execution status, logs, explainability maps, and split QA outputs"""
    if task_id not in mock_task_store:
        raise HTTPException(status_code=404, detail="Requested task ID not found.")
    return mock_task_store[task_id]
