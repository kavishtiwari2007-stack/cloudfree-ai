# CloudFreeAI: AI-Powered Multi-Temporal Satellite Reconstruction & Disaster Intelligence

CloudFreeAI is a research-grade remote sensing and disaster intelligence platform designed for the **Bharatiya Antariksh Hackathon (BAH) 2026**. It reconstructs cloud-covered, high-resolution optical satellite imagery (specifically Resourcesat-2/2A LISS-IV) by fusing historical cloud-free optical datasets with current Sentinel-1 Synthetic Aperture Radar (SAR) observations, outputting both reconstructed images and confidence estimates per pixel.

---

## 🛰️ System Architecture & Data Flow

```mermaid
graph TD
    User([User GIS Client]) -->|1. Select AOI / Request| API[FastAPI Gateway]
    API -->|2. Query Metadata| DB[(PostgreSQL + PostGIS)]
    
    %% Ingestion
    API -->|3. Enqueue Ingestion| Celery[Celery Task Queue]
    Celery -->|4. Query Historical Archive| RefRank[Historical Reference Image Ranking Engine]
    RefRank -->|Select Best Cloud-Free Scene| Ingest[Bhoonidhi / Sentinel Hub Ingestion]
    
    subgraph IngestDS [Data Sources Ecosystem]
        Ingest -->|Historical Optical| Bhoonidhi[ISRO Bhoonidhi: LISS-IV, Resourcesat-2/2A, Cartosat, IRS]
        Ingest -->|Current Observations| Radar[Sentinel-1 SAR, RISAT Radar, Weather layers]
    end

    %% Verification & Validation
    IngestDS -->|Raw TIFFs & Orbit files| MetaVal[Metadata Validation: Bands, Projections, Timestamps]

    subgraph Prep [Scientific Preprocessing Module]
        MetaVal -->|1. TOA| Calib[TOA Reflectance Calibration]
        Calib -->|2. Atmospheric| Atmos[Atmospheric Dark Object Subtraction]
        Atmos -->|3. Resampling| Resamp[Spatial Resampling & Speckle Filter]
        Resamp -->|4. Alignment| Reg[LoFTR Sub-Pixel Co-Registration]
        Reg -->|5. Masking| CloudDet[U-Net Cloud & Shadow Masking]
    end
    
    subgraph AI [AI Reconstruction Pipeline]
        CloudDet -->|Historical Optical| OptEnc[Historical Optical Encoder]
        Prep -->|Current SAR VV/VH| SAREnc[Current SAR Encoder]
        
        OptEnc & SAREnc --> TempFuse[Spatial-Temporal Fusion Transformer]
        TempFuse --> CrossAttn[Cross-Attention Feature Fusion]
        CrossAttn --> DiffNet[Conditional Diffusion Reconstruction Model]
        DiffNet --> SpecCons[Spectral Consistency Module]
        SpecCons --> ConfEst[Pixel-level Confidence Estimator]
    end

    subgraph Verification [Scientific Quality Assessment]
        ConfEst -->|Cloud-Free Optical| SpectralVal[NDVI, SAM, PSNR, SSIM, RMSE Verification]
    end

    subgraph Disaster [Disaster Intelligence Engine]
        SpectralVal -->|Validated Optical| FloodSeg[DeepLabV3+ Flood Segmentation]
        SpectralVal -->|Surface Change| ChangeDet[Siamese ViT Change Detection]
        
        FloodSeg & ChangeDet --> DamEval[Road, Bridge, Crop & Settlement Damage Analysis]
        DamEval --> SevClass[Severity & Rescue Priority Classification]
    end
    
    SevClass -->|GeoJSON Layers & Raster| DB
    SevClass -->|Metrics & Data| Gemini[Gemini 1.5 Pro Report Generator]
    Gemini -->|PDF/PowerPoint/GeoTIFF Export| User
```

---

## 📂 Core Project Layout

- `/backend`: FastAPI service managing GIS processes, DB connections, and Gemini report interfaces.
- `/frontend`: Next.js single-page client interface built with Tailwind CSS, Leaflet, and TypeScript.
- `/models`: PyTorch deep learning modules for image alignment, reconstruction, and flood segmentation.
- `/database`: PostGIS database schema definitions and spatial queries.
- `/scripts`: Python training and inference command line utilities.
- `/index.html`: Standalone, zero-setup GIS client for client-side local demonstrations.

---

## 🛠️ Detailed Preprocessing Pipeline
1. **Metadata Validation**: Compares coordinate footprints, matches sensor bands, verifies projection systems (e.g., matching UTM zones), and confirms chronological order.
2. **Top-Of-Atmosphere (TOA) Reflectance**: Calibrates raw pixel Digital Numbers (DN) to physical reflectance values.
3. **Atmospheric Correction**: Adjusts bands for Rayleigh scattering and aerosol attenuation using dark object subtraction.
4. **Spatial Resampling & Filtering**: Resamples multi-scale bands (e.g., LISS-IV 5.8m to Sentinel-1 10m grids) and filters SAR speckle noise using Lee filters.
5. **Geometric Co-Registration**: Keypoint matching using Local Feature Transformers (LoFTR) to ensure sub-pixel mapping alignment.
6. **Cloud & Shadow Detection**: Multi-spectral segmenter generating pixel masks for cloud cover.

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

---

## 🧑‍💻 Standalone Demonstration

If you are running in a restricted environment without docker or GPU runtime, open the root `index.html` file in any web browser. It features a complete telemetry simulated dashboard, real-time leaflet layers, opacity toggles, and side-by-side swipe comparison.
