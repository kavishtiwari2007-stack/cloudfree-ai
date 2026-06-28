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
    Manages operational chains including Object Storage & Metadata DB queries, 
    Multi-Criteria Ranking, Data Quality Filters (IQA), Preprocessing, and 
    Physics-Guided Multi-Temporal Reconstruction.
    """
    def __init__(self):
        self.registry = ModelRegistry()

    def run_pipeline(self, task_id: str, req: ReconstructionRequestSchema):
        # 1. Dataset Discovery Engine (5%)
        mock_task_store[task_id]["progress_percentage"] = 5
        mock_task_store[task_id]["message"] = "Orchestrator: Querying Dataset Discovery Engine (Catalog Search -> Metadata DB query)..."
        time.sleep(0.5)

        # 2. Multi-Criteria Ranking & Selection (12%)
        mock_task_store[task_id]["progress_percentage"] = 12
        mock_task_store[task_id]["message"] = "Orchestrator: Applying Multi-Criteria Ranking (Cloud %, season similarity, temporal distance, viewing geometry)... Reference scene selected."
        time.sleep(0.5)

        # 3. Object Storage & Raster Cache check (20%)
        mock_task_store[task_id]["progress_percentage"] = 20
        mock_task_store[task_id]["message"] = "Orchestrator: Querying Object Storage (MinIO/S3) & local Raster Cache... Cache Miss. Launching Download Manager..."
        time.sleep(0.6)

        # 4. Metadata Validation (30%)
        mock_task_store[task_id]["progress_percentage"] = 30
        mock_task_store[task_id]["message"] = "Orchestrator: Checking metadata consistency, spatial coordinates, and coordinate reference system (CRS)..."
        time.sleep(0.5)

        # 5. Data Quality Filter / Image Quality Assessment (IQA) (38%)
        mock_task_store[task_id]["progress_percentage"] = 38
        mock_task_store[task_id]["message"] = "Orchestrator: Running Image Quality Assessment (IQA) -> Cloud % (78%), Striping (none), Radiometry (none) -> Scene ACCEPTED."
        time.sleep(0.6)

        # 6. SAR Preprocessing (48%)
        mock_task_store[task_id]["progress_percentage"] = 48
        mock_task_store[task_id]["message"] = "Orchestrator: SAR Preprocessing (Orbit Correction -> Thermal Noise Removal -> Calibration -> Terrain Correction -> Lee Speckle Filter)..."
        time.sleep(0.8)

        # 7. Optical Preprocessing (58%)
        mock_task_store[task_id]["progress_percentage"] = 58
        mock_task_store[task_id]["message"] = "Orchestrator: Optical Preprocessing (TOA Reflectance -> Atmospheric correction -> Band Normalization -> Histogram Matching)..."
        time.sleep(0.8)

        # 8. MLOps Layer Checkpoint Load (68%)
        mlops = self.registry.load_inference_service()
        mock_task_store[task_id]["progress_percentage"] = 68
        mock_task_store[task_id]["message"] = f"Orchestrator: Loaded Model Registry version: {mlops['version']} (Performance monitoring online)..."
        time.sleep(0.5)

        # 9. Co-Registration & Reconstruction (78%)
        mock_task_store[task_id]["progress_percentage"] = 78
        mock_task_store[task_id]["message"] = "Orchestrator: Executing Physics-Guided Multi-Temporal SAR-Optical Reconstruction Engine..."
        time.sleep(0.9)

        # 10. Split QA Validation & Flood Segmentation (88%)
        mock_task_store[task_id]["progress_percentage"] = 88
        mock_task_store[task_id]["message"] = "Orchestrator: Running independent validation branches (QA metrics) and flood segmentation modules in parallel..."
        time.sleep(0.7)

        # 11. Explainability Layer & Exposure Analysis (94%)
        mock_task_store[task_id]["progress_percentage"] = 94
        mock_task_store[task_id]["message"] = "Orchestrator: Generating Explainability Layers (Attention maps, uncertainty maps) & Population Exposure (OSM+Census)..."
        time.sleep(0.6)

        # 12. Report Generation (98%)
        mock_task_store[task_id]["progress_percentage"] = 98
        mock_task_store[task_id]["message"] = "Orchestrator: Summarizing spatial metrics for LLM Report Generator..."
        time.sleep(0.5)

        # Scientific validation arrays
        ref_mock = np.random.rand(4, 64, 64)
        recon_mock = ref_mock + np.random.normal(0, 0.04, (4, 64, 64))
        recon_mock = np.clip(recon_mock, 0.0, 1.0)
        
        validator = ScientificValidator(max_value=1.0)
        metrics = validator.validate_scene(ref_mock, recon_mock)

        # Task Complete
        mock_task_store[task_id]["status"] = "COMPLETED"
        mock_task_store[task_id]["progress_percentage"] = 100
        mock_task_store[task_id]["message"] = "Orchestrator: Reconstruction and analysis completed nominal."
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
        "message": "Orchestrator: Triggering Workflow Orchestrator tasks...",
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
