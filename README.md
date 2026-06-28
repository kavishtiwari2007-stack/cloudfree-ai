# CloudFreeAI: Physics-Guided Multi-Temporal SAR–Optical Reconstruction & Disaster Intelligence Platform

CloudFreeAI is a research-grade remote sensing and disaster intelligence platform developed for the **Bharatiya Antariksh Hackathon (BAH) 2026**. It reconstructs cloud-covered, high-resolution optical satellite imagery (Resourcesat-2/2A LISS-IV) using current Sentinel-1 Synthetic Aperture Radar (SAR) observations and historical cloud-free baselines, preserving physical and scientific accuracy.

---

## 🛰️ Three-Level System Architecture

### 📊 Level 1: High-Level Pipeline
A simplified representation of the end-to-end data flow:

```mermaid
graph LR
    User([User GIS Client]) -->|1. Select AOI| Retrieval[Dataset Discovery & Retrieval]
    Retrieval -->|2. Dual Modality Bands| Prep[Geoprocessing Preprocessing]
    Prep -->|3. Standardized Arrays| Recon[Physics-Guided AI Reconstruction]
    Recon -->|4. Cloud-Free Optical| Flood[Flood Segmentation & Disaster Analysis]
    Flood -->|5. Damage Statistics| Report[LLM Report Summarization]
    Report -->|6. Official Briefs| User
```

---

### 🔍 Level 2: Detailed Architectural Data Flow
The complete scientific geoprocessing, MLOps, and validation architecture:

```mermaid
graph TD
    User([User GIS Client]) -->|1. Select Area of Interest| API[FastAPI Gateway]
    API -->|2. Task Request| Orch[Central Workflow Orchestrator]
    
    subgraph MLOps [MLOps & Model Registry Layer]
        MR[Model Registry DB] -->|Checkpoints| Version[Model Versioning v2.4.1]
        Version -->|Deploy Weights| Service[Inference Service Engine]
        Service -->|Real-time Performance| Monitor[Performance Monitoring & Logging]
        Monitor -->|Telemetric State| Orch
    end

    %% Ingestion & Discovery
    Orch -->|3. Query Metadata| Disc[Dataset Discovery Engine]
    
    subgraph Discovery [Dataset Discovery & Ingestion]
        Disc -->|Metadata Search| MetaQuery[Bhoonidhi Catalog Search]
        MetaQuery -->|Filter Cloud Cover| CloudFilt[Cloud Coverage Filter]
        CloudFilt -->|Acquisition Season / Solar angle| TempRank[Multi-Criteria Ranking Engine]
        TempRank -->|Reference Selection| RefSel[Reference Scene Selection]
        RefSel -->|Verify Cache| ObjectStorage[Object Storage: S3/MinIO]
        ObjectStorage -->|Local Lookup| RasterCache[Local Raster Cache]
        RasterCache -->|Attributes| MetaDB[(Metadata Database: PostGIS)]
        MetaDB -->|Download Misses| DL[Download Manager]
    end

    DL & RasterCache -->|Verify footprint| MetaVal[Metadata Validation: Bands & Projections]

    %% Data Quality Filter / Image Quality Assessment
    MetaVal -->|Radiometric DN check| IQA[Image Quality Assessment: Cloud %, Missing Bands, Striping, Radiometric Errors]
    IQA -->|Filter evaluation| AcceptReject{Accept / Reject Scene}
    
    subgraph Preprocessing [Scientific Preprocessing Module]
        AcceptReject -->|If Accepted - SAR VV/VH| S1_1[SAR Orbit Correction]
        S1_1 --> S1_2[SAR Thermal Noise Removal]
        S1_2 --> S1_3[SAR Radiometric Calibration]
        S1_3 --> S1_4[SAR Range-Doppler Terrain Correction]
        S1_4 --> S1_5[SAR Speckle Filtering: Refined Lee]
        S1_5 --> S1_6[SAR Amplitude Normalization]
        
        AcceptReject -->|If Accepted - Optical| Opt_1[TOA Reflectance Calibration]
        Opt_1 --> Opt_2[Atmospheric Correction: Dark Object Subtraction]
        Opt_2 --> Opt_3[Band Normalization]
        Opt_3 --> Opt_4[Histogram Matching]
        Opt_4 --> Opt_5[Seasonal Normalization]
    end
    
    subgraph AI [Physics-Guided Multi-Temporal SAR-Optical Reconstruction Engine]
        Opt_5 -->|Historical Baseline| OptEnc[Historical Optical Encoder]
        S1_6 -->|Current SAR Guidance Constraints| SAREnc[Current SAR Encoder]
        
        OptEnc & SAREnc --> TempFuse[Spatial-Temporal Fusion Transformer]
        TempFuse --> CrossAttn[Cross-Attention Interpolation]
        CrossAttn --> DiffNet[Conditional Diffusion Reconstruction Model]
        DiffNet --> SpecCons[Spectral Consistency & Quality QC]
    end

    %% Decoupled Splits (Reconstructed Image feeds QA and Flood independently)
    SpecCons -->|Reconstructed Image| SplitNode{Decoupled Splits}
    
    subgraph QA [Quality Assurance Validation Split]
        SplitNode -->|Independent Validation| AttnM[Attention Weights Synthesis]
        SplitNode -->|Independent Validation| UncertM[Pixel Uncertainty Estimation]
        SplitNode -->|Independent Validation| FeatImp[Feature Importance & Pixel Attribution]
        
        AttnM & UncertM & FeatImp --> ReconstructionQA[I. Image Quality: PSNR, SSIM, RMSE]
        AttnM & UncertM & FeatImp --> SpectralQA[II. Spectral Integrity: SAM, NDVI Delta]
        AttnM & UncertM & FeatImp --> GeometricQA[III. Geometric Consistency: IoU Score, Boundary Accuracy]
    end

    subgraph Disaster [Disaster Emergency Decision Support Engine]
        SplitNode -->|Hazard Processing| FloodSeg[DeepLabV3+ Flood Segmentation]
        SplitNode -->|Hazard Processing| ChangeDet[Siamese ViT Change Detection]
        
        FloodSeg & ChangeDet --> DamEval[Road Accessibility & Bridge Connectivity]
        DamEval --> WaterDepth[Estimated Flood Severity Index: Model-Based]
        WaterDepth --> Population[Population Exposure OSM + Census]
        Population --> Hospital[Hospital Accessibility OSM Roads]
        Hospital --> RescueIndex[Priority Response Score]
    end

    subgraph OutputArray [Full Output Data Array]
        ReconstructionQA & SpectralQA & GeometricQA --> ArrayMerge[Output Array Compiler]
        RescueIndex --> ArrayMerge
        ArrayMerge -->|Outputs: GeoTIFF, GeoJSON, XAI Maps, Telemetry Stats| MergedOutput[Completed Array]
    end

    subgraph Reporting [Explanation & Summary Layer]
        MergedOutput --> Gemini[Gemini 1.5 Pro Report Generator]
        Gemini -->|Natural Language Report| PDF[Official Emergency PDF]
        Gemini -->|Brief Slides| PPTX[Brief PowerPoint Briefing]
        Gemini -->|Interactive Chat| Summary[Interactive Executive Chat]
    end

    Summary --> User
```

---

### ⏱️ Level 3: Sequence Diagram
Sequence of runtime interactions across core system components:

```mermaid
sequenceDiagram
    autonumber
    actor User as User GIS Client
    participant API as FastAPI Gateway
    participant Orch as Central Workflow Orchestrator
    participant Cache as Object Storage & DB Cache
    participant Prep as Geoprocessing Modules
    participant AI as Multi-Temporal Fusion Engine
    participant QA as QA Validation Split
    participant LLM as Gemini Report Generator

    User->>API: POST /api/reconstruct/trigger (AOI coordinates)
    API->>Orch: Enqueue task in background
    API-->>User: 202 Accepted (Task ID)
    
    activate Orch
    Orch->>Cache: Check cache footprints
    alt Cache Hit
        Cache-->>Orch: Return cached rasters
    else Cache Miss
        Cache-->>Orch: Catalog query download
        Orch->>Prep: Execute SAR & Optical Preprocessing
        Prep-->>Orch: Return calibrated rasters
    end

    Orch->>AI: Trigger physics-guided multi-temporal fusion
    AI-->>Orch: Return cloud-free reconstructed optical scene
    
    par Quality Verification
        Orch->>QA: Execute QA Validation Split (PSNR, SSIM, SAM, IoU)
        QA-->>Orch: Return verification metrics
    and Disaster Analytics
        Orch->>Prep: Run Flood segmenters & OSM exposure mapping
        Prep-->>Orch: Return severity and accessibility statistics
    end

    Orch->>LLM: Summarize outputs for briefing
    LLM-->>Orch: Return PDF report & natural language brief
    Orch-->>API: Task state = COMPLETED
    deactivate Orch
    
    User->>API: GET /api/reconstruct/status (Task ID)
    API-->>User: 200 OK (Rasters, split metrics, and Gemini briefs)
```

---

## 🛰️ Physical Remote Sensing Constraint Note
In this architecture, **Sentinel-1 SAR backscatter observations are utilized as physical constraints** to guide and bound the conditional diffusion model. Because SAR and optical sensors capture fundamentally different physical phenomena (microwave surface roughness/moisture vs solar reflectance), SAR data is NOT directly converted to optical bands. Instead, it constrains the spatial boundaries of features (e.g., water boundaries, landslides) during optical reconstruction.

---

## 🌟 Future Extension Modules (Roadmap)
```
Weather Forecast API --> Rainfall Prediction --> Future Flood Risk Estimation
```
*Note: Weather forecasting is labeled as a future extension module to maintain separation from the current satellite surface reconstruction engine.*

---

## 🧑‍💻 End User Dashboard Flow
```
User --> Dashboard --> AOI Selection --> AI Processing --> Results --> Layer Controls --> Compare Before/After --> Download GeoTIFF/GeoJSON --> Generate AI Report --> Interactive AI Chat
```
---

## 📂 Code Layout

- `/backend`: FastAPI geoprocessing service managing workflow orchestration, model registry, and database queries.
- `/frontend`: Next.js single-page client interface built with Tailwind CSS, Lucide Icons, and React.
- `/models`: PyTorch deep learning modules for image alignment, reconstruction, and flood segmentation.
- `/database`: PostGIS database schema definitions and spatial queries.
- `/scripts`: Python training and verification utilities.
- `/index.html`: Standalone, zero-setup GIS client for client-side local demonstrations.
