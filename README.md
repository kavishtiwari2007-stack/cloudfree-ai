# CloudFreeAI: AI-Powered Multi-Temporal Satellite Reconstruction & Disaster Intelligence

CloudFreeAI is a research-grade remote sensing and disaster intelligence platform designed for the **Bharatiya Antariksh Hackathon (BAH) 2026**. It reconstructs cloud-covered, high-resolution optical satellite imagery (specifically Resourcesat-2/2A LISS-IV) by fusing historical cloud-free optical datasets with current Sentinel-1 Synthetic Aperture Radar (SAR) observations, outputting both reconstructed images, attention vectors, and pixel-level confidence maps.

---

## 🛰️ System Architecture & Data Flow

```mermaid
graph TD
    User([User GIS Client]) -->|1. Select AOI / Request| API[FastAPI Gateway]
    API -->|2. Initial Request| Orch[Central Workflow Orchestrator]
    
    subgraph Registry [Model Registry]
        MR[Model Registry DB] -->|Resolve weights| Orch
    end

    %% Ingestion
    Orch -->|3. Query Discovery| Disc[Dataset Discovery Engine]
    
    subgraph Discovery [Data Discovery & Ingestion]
        Disc -->|Metadata Search| MetaQuery[Bhoonidhi Catalog Query]
        MetaQuery -->|Filter Cloud %| CloudFilt[Cloud Coverage Filter]
        CloudFilt -->|Acquisition Season / Solar angle| TempRank[Temporal Rank Engine]
        TempRank -->|Reference Selection| RefSel[Reference Scene Selection]
        RefSel -->|Enqueue Download| DL[Download Manager]
    end

    subgraph Preprocessing [Scientific Preprocessing Module]
        DL -->|Raw Orbit Files & Bands| MetaVal[Metadata Validation: Bands, Projections, Timestamps]
        
        %% SAR Preprocessing
        MetaVal -->|SAR VV/VH| S1_1[SAR Orbit Correction]
        S1_1 --> S1_2[SAR Thermal Noise Removal]
        S1_2 --> S1_3[SAR Radiometric Calibration]
        S1_3 --> S1_4[SAR Range-Doppler Terrain Correction]
        S1_4 --> S1_5[SAR Speckle Filtering: Refined Lee]
        S1_5 --> S1_6[SAR Amplitude Normalization]
        
        %% Optical Preprocessing
        MetaVal -->|Historical Optical| Opt_1[TOA Reflectance Calibration]
        Opt_1 --> Opt_2[Atmospheric Correction: Dark Object Subtraction]
        Opt_2 --> Opt_3[Band Normalization]
        Opt_3 --> Opt_4[Histogram Matching]
        Opt_4 --> Opt_5[Seasonal Normalization]
    end
    
    subgraph AI [AI Reconstruction Constraints Engine]
        S1_6 -->|SAR Guidance Constraints| OptEnc[Historical Optical Encoder]
        Opt_5 -->|Historical Baseline| SAREnc[Current SAR Encoder]
        
        OptEnc & SAREnc --> TempFuse[Spatial-Temporal Fusion Transformer]
        TempFuse --> CrossAttn[Cross-Attention Interpolation]
        CrossAttn --> DiffNet[Conditional Diffusion Reconstruction Model]
        DiffNet --> SpecCons[Spectral Consistency & Quality QC]
    end

    subgraph Explain [Explainable AI Layer]
        SpecCons --> AttnM[Attention Weights Synthesis]
        SpecCons --> UncertM[Pixel Uncertainty Estimation]
    end

    subgraph QA [Quality Assurance Validation Split]
        AttnM & UncertM --> ReconstructionQA[Reconstruction Validation: PSNR, SSIM, RMSE]
        AttnM & UncertM --> SpectralQA[Spectral Validation: SAM, NDVI Delta]
        AttnM & UncertM --> UncertaintyQA[Uncertainty Validation: Confidence Score, Pixel Reliability]
    end

    subgraph Disaster [Disaster Intelligence Engine]
        ReconstructionQA & SpectralQA & UncertaintyQA --> FloodSeg[DeepLabV3+ Flood Segmentation]
        ReconstructionQA & SpectralQA & UncertaintyQA --> ChangeDet[Siamese ViT Change Detection]
        
        FloodSeg & ChangeDet --> DamEval[Road, Bridge, Crop Inundation & Village Isolation Analysis]
        DamEval --> WaterDepth[Water Depth Estimation]
        WaterDepth --> RescueIndex[Rescue Priority & Inundation Severity Indexing]
    end
    
    RescueIndex -->|Raster Maps| DB[(PostgreSQL + PostGIS)]
    RescueIndex -->|Metrics & Data| Gemini[Gemini 1.5 Pro Report Generator]
    Gemini -->|Full Output Array: GeoTIFF, GeoJSON, XAI Maps, PDF & PPTX Reports| User
```

---

## 🛰️ Physical Remote Sensing Constraint Note
In this architecture, **Sentinel-1 SAR backscatter observations are utilized as physical constraints** to guide and bound the conditional diffusion model. Because SAR and optical sensors capture fundamentally different physical phenomena (microwave surface roughness/moisture vs solar reflectance), SAR data is NOT directly converted to optical bands. Instead, it constrains the spatial boundaries of features (e.g., water boundaries, landslides) during optical reconstruction.

---

## 🛠️ Detailed Preprocessing Chains

### 1. SAR Preprocessing
- **Orbit Correction**: Updates metadata coordinates using precise Sentinel Orbit State Vectors.
- **Thermal Noise Removal**: Strips noise contamination in sub-swaths.
- **Radiometric Calibration**: Converts pixel digital numbers to physical sigma-nought values.
- **Terrain Correction**: Resolves geometric distortions (layover, shadow) using SRTM 30m DEM arrays.
- **Speckle Filtering**: Dampens radar speckle backscatter noise using a 5x5 Refined Lee filter.
- **Normalization**: Scales backscatter bands to standardized training ranges.

### 2. Optical Preprocessing
- **TOA Calibration**: Standardizes sensor input variables based on solar distance and acquisition date.
- **Atmospheric Correction**: Dark Object Subtraction (DOS) offsets haze.
- **Band Normalization**: Standardizes multi-spectral channels (R, G, B, NIR).
- **Histogram Matching**: Corrects radiometric differences between historical reference scenes and current images.
- **Seasonal Normalization**: Compensates for phenological changes.

---

## 📂 Code Layout

- `/backend`: FastAPI geoprocessing service managing workflow orchestration, model registry, and database queries.
- `/frontend`: Next.js single-page client interface built with Tailwind CSS, Lucide Icons, and React.
- `/models`: PyTorch deep learning modules for image alignment, reconstruction, and flood segmentation.
- `/database`: PostGIS database schema definitions and spatial queries.
- `/scripts`: Python training and verification utilities.
- `/index.html`: Standalone, zero-setup GIS client for client-side local demonstrations.

---

## 🚀 Running the System (Docker Compose)

To spin up the database, Redis queue, background workers, backend API, and frontend server:

```bash
docker-compose up --build
```

The services will expose:
- Frontend Dashboard: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
- PostgreSQL Database: `localhost:5432`
