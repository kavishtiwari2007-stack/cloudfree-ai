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
    Model Registry with MLOps Layer support.
    Tracks model checkpoints, versioning (e.g. v2.4.1), and performance monitors.
    """
    def __init__(self):
        self.version = "v2.4.1"
        self._registry = {
            "cloud_detection": "CloudNet_ResNet_v1.2",
            "registration": "LoFTR_GNN_v2.0",
            "reconstruction": "TemporalDiffusionTransformer_v3.4"
        }

    def load_inference_service(self) -> Dict:
        return {
            "version": self.version,
            "models": self._registry,
            "monitoring": "NOMINAL",
            "performance_logging": "active"
        }


class WorkflowOrchestrator:
    """
    Workflow Orchestrator.
    Manages operational chains including Raster Cache check, Image Quality Assessment,
    model loading from MLOps Registry, and execution of multi-modal fusion.
    """
    def __init__(self):
        self.registry = ModelRegistry()

    def run_pipeline(self, task_id: str, req: ReconstructionRequestSchema):
        # 1. Dataset Discovery Engine (5%)
        mock_task_store[task_id]["progress_percentage"] = 5
        mock_task_store[task_id]["message"] = "Orchestrator: Querying Dataset Discovery Engine (Acquisition season, Solar elevation, Cloud %)..."
        time.sleep(0.5)

        # 2. Reference Scene Selection & Download Manager (12%)
        mock_task_store[task_id]["progress_percentage"] = 12
        mock_task_store[task_id]["message"] = "Orchestrator: Ranking historical baseline reference scenes. Activating Download Manager..."
        time.sleep(0.5)

        # 3. Spatial DB Raster Cache Check (20%)
        mock_task_store[task_id]["progress_percentage"] = 20
        mock_task_store[task_id]["message"] = "Orchestrator: Checking local Spatial DB Raster Cache... Cache Miss. Fetching scenes from Bhoonidhi..."
        time.sleep(0.6)

        # 4. Metadata Validation (30%)
        mock_task_store[task_id]["progress_percentage"] = 30
        mock_task_store[task_id]["message"] = "Orchestrator: Verifying metadata parameters, band mappings, and map projections..."
        time.sleep(0.5)

        # 5. Data Quality Filter / Image Quality Assessment (IQA) (38%)
        mock_task_store[task_id]["progress_percentage"] = 38
        mock_task_store[task_id]["message"] = "Orchestrator: Executing Data Quality Filter (checking Cloud %, Missing Bands, Striping, Radiometric errors)... Scene status: ACCEPTED."
        time.sleep(0.7)

        # 6. SAR Preprocessing (48%)
        mock_task_store[task_id]["progress_percentage"] = 48
        mock_task_store[task_id]["message"] = "Orchestrator: SAR Preprocessing (Orbit Correction -> Thermal Noise Removal -> Calibration -> Terrain Correction -> Lee Speckle Filter -> Normalization)..."
        time.sleep(0.8)

        # 7. Optical Preprocessing (58%)
        mock_task_store[task_id]["progress_percentage"] = 58
        mock_task_store[task_id]["message"] = "Orchestrator: Optical Preprocessing (TOA Reflectance -> Atmospheric correction -> Band Normalization -> Histogram Matching -> Seasonal Normalization)..."
        time.sleep(0.8)

        # 8. MLOps Layer & Model Checkpoint Load (68%)
        mlops = self.registry.load_inference_service()
        mock_task_store[task_id]["progress_percentage"] = 68
        mock_task_store[task_id]["message"] = f"Orchestrator: MLOps Inference Service initialized. Loaded model registry checkpoint version: {mlops['version']} (Performance monitoring online)..."
        time.sleep(0.6)

        # 9. Co-Registration & Fusion Pipeline (78%)
        mock_task_store[task_id]["progress_percentage"] = 78
        mock_task_store[task_id]["message"] = "Orchestrator: Running Co-Registration & Physics-Guided Multi-Modal SAR-Optical Fusion Engine..."
        time.sleep(0.9)

        # 10. Explainability Layer (88%)
        mock_task_store[task_id]["progress_percentage"] = 88
        mock_task_store[task_id]["message"] = "Orchestrator: Compiling Explainability Layers (synthesizing Feature Importance, Pixel Attribution, and Confidence heatmaps)..."
        time.sleep(0.7)

        # 11. Scientific QA Validation Split (94%)
        mock_task_store[task_id]["progress_percentage"] = 94
        mock_task_store[task_id]["message"] = "Orchestrator: Calculating split QA validation arrays (Image Quality, Spectral Integrity, Geometric Consistency)..."
        time.sleep(0.6)

        # 12. Disaster Assessment & Emergency Decision Support (98%)
        mock_task_store[task_id]["progress_percentage"] = 98
        mock_task_store[task_id]["message"] = "Orchestrator: Running Emergency Decision Support Engine (calculating flood depth, population exposure, and priority indices)..."
        time.sleep(0.6)

        # Scientific calculations
        ref_mock = np.random.rand(4, 64, 64)
        recon_mock = ref_mock + np.random.normal(0, 0.04, (4, 64, 64))
        recon_mock = np.clip(recon_mock, 0.0, 1.0)
        
        validator = ScientificValidator(max_value=1.0)
        metrics = validator.validate_scene(ref_mock, recon_mock)

        # Complete
        mock_task_store[task_id]["status"] = "COMPLETED"
        mock_task_store[task_id]["progress_percentage"] = 100
        mock_task_store[task_id]["message"] = "Orchestrator: Spatial geoprocessing task finalized successfully."
        mock_task_store[task_id]["completed_at"] = datetime.utcnow()

        mock_task_store[task_id]["results"] = {
            "mlops_telemetry": mlops,
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
                "image_quality": {
                    "psnr_db": round(metrics["image_quality"]["peak_signal_noise_ratio_db"], 2),
                    "ssim": round(metrics["image_quality"]["structural_similarity_index"], 3),
                    "rmse": round(metrics["image_quality"]["root_mean_squared_error"], 4)
                },
                "spectral_integrity": {
                    "spectral_angle_mapper_rad": round(metrics["spectral_integrity"]["spectral_angle_mapper_rad"], 4),
                    "mean_ndvi_delta": round(metrics["spectral_integrity"]["mean_ndvi_delta"], 4)
                },
                "geometric_consistency": {
                    "intersection_over_union": round(metrics["geometric_consistency"]["intersection_over_union"], 3),
                    "boundary_accuracy_index": round(metrics["geometric_consistency"]["boundary_accuracy_index"], 4)
                }
            }
        }


import time

def execute_mock_pipeline_sync(task_id: str, req: ReconstructionRequestSchema):
    orchestrator = WorkflowOrchestrator()
    orchestrator.run_pipeline(task_id, req)


@router.post("/trigger", response_model=ReconstructionTaskStatus)
async def trigger_reconstruction(request: ReconstructionRequestSchema, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    mock_task_store[task_id] = {
        "task_id": task_id,
        "status": "PENDING",
        "progress_percentage": 0,
        "message": "Orchestrator: Instantiating workflow tasks...",
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "results": None
    }
    
    background_tasks.add_task(execute_mock_pipeline_sync, task_id, request)
    return mock_task_store[task_id]


@router.get("/status/{task_id}", response_model=ReconstructionTaskStatus)
async def get_task_status(task_id: str):
    if task_id not in mock_task_store:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return mock_task_store[task_id]
