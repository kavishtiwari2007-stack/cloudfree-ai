-- PostgreSQL + PostGIS Schema for CloudFreeAI Remote Sensing Platform

-- Enable PostGIS extension for spatial data operations
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Projects Table (Remote sensing tasks organized by Area of Interest)
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    aoi_geometry GEOMETRY(Polygon, 4326) NOT NULL, -- Spatial AOI in WGS84
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spatial index on AOI for geometric queries (e.g. intersection check)
CREATE INDEX idx_projects_aoi ON projects USING GIST(aoi_geometry);

-- 3. Datasets Cache Table (Satellite imagery metadata)
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    sensor VARCHAR(50) NOT NULL, -- e.g. 'LISS-IV', 'Sentinel-1-SAR', 'Cartosat'
    acquisition_date TIMESTAMP WITH TIME ZONE NOT NULL,
    cloud_cover DOUBLE PRECISION DEFAULT 0.0,
    spatial_coverage GEOMETRY(Polygon, 4326) NOT NULL, -- Boundary of image footprint
    file_path VARCHAR(512) NOT NULL, -- Path to local geotiff / cloud-optimized geotiff (COG)
    metadata JSONB, -- Additional band metadata, polarizations, orbit direction
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_datasets_coverage ON datasets USING GIST(spatial_coverage);
CREATE INDEX idx_datasets_acquisition ON datasets(acquisition_date);

-- 4. Reconstructions Table (AI output runs)
CREATE TABLE IF NOT EXISTS reconstructions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    cloudy_dataset_id INTEGER REFERENCES datasets(id),
    historical_dataset_id INTEGER REFERENCES datasets(id),
    sar_dataset_id INTEGER REFERENCES datasets(id),
    status VARCHAR(50) NOT NULL, -- 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED'
    reconstructed_path VARCHAR(512), -- Reconstructed Optical TIF
    confidence_path VARCHAR(512), -- Confidence Heatmap TIF
    difference_path VARCHAR(512), -- Difference Map TIF
    ndvi_path VARCHAR(512), -- NDVI TIF
    metrics JSONB, -- PSNR, SSIM, Spectral Angle Mapper (SAM) values
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 5. Disaster Analyses Table (Output from Flood Segmentation & Damage modules)
CREATE TABLE IF NOT EXISTS disaster_analyses (
    id SERIAL PRIMARY KEY,
    reconstruction_id INTEGER REFERENCES reconstructions(id) ON DELETE CASCADE,
    flood_extent GEOMETRY(MultiPolygon, 4326), -- Segmented water spread geometry
    water_expansion_area_km2 DOUBLE PRECISION,
    vegetation_loss_area_km2 DOUBLE PRECISION,
    affected_settlements_count INTEGER DEFAULT 0,
    road_damage_length_m DOUBLE PRECISION DEFAULT 0.0,
    bridge_damage_count INTEGER DEFAULT 0,
    severity_level VARCHAR(20) NOT NULL, -- 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_disaster_flood ON disaster_analyses USING GIST(flood_extent);

-- 6. AI Reports Table (Gemini generated natural language summaries)
CREATE TABLE IF NOT EXISTS ai_reports (
    id SERIAL PRIMARY KEY,
    disaster_analysis_id INTEGER REFERENCES disaster_analyses(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    agricultural_impact TEXT,
    infrastructure_damage TEXT,
    emergency_recommendations TEXT,
    report_pdf_path VARCHAR(512),
    report_docx_path VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
