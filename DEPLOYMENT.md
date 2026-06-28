# CloudFreeAI: Production Deployment Guide

This guide details the step-by-step instructions for deploying the **CloudFreeAI** platform in a production cloud environment.

---

## 🏗️ Production Architecture Map

```
                     ┌────────────────────────┐
                     │  Vercel (Frontend)     │
                     └───────────┬────────────┘
                                 │ HTTP / WebSockets
                                 ▼
                     ┌────────────────────────┐
                     │ Render/Koyeb (Backend) │
                     └──────┬───────────┬─────┘
                            │           │
            PostgreSQL Link │           │ Redis protocol
                            ▼           ▼
       ┌──────────────────────┐       ┌──────────────────────┐
       │ Supabase (Database)  │       │ Upstash (Broker)     │
       │  * PostGIS Enabled   │       │  * Cache & Queue     │
       └──────────────────────┘       └──────────────────────┘
```

---

## 📦 Step 1: Database Setup (Supabase)

Supabase provides a managed PostgreSQL database with native PostGIS spatial extension support.

1. **Create a Supabase Project:**
   - Go to [supabase.com](https://supabase.com) and create a new project.
   - Set your database password and choose your regional cluster.
2. **Enable PostGIS Extension:**
   - Go to the **SQL Editor** in the Supabase Dashboard.
   - Execute the following SQL query to initialize the PostGIS schema bindings:
     ```sql
     -- Enable PostGIS extension (adds spatial types like geometry, geography)
     CREATE EXTENSION IF NOT EXISTS postgis;

     -- Verify installation
     SELECT postgis_full_version();
     ```
3. **Execute DB Schema Migrations:**
   - Paste the contents of your `schema.sql` file into the SQL Editor and run it to construct the spatial indices, raster caches, and disaster metrics tables.
4. **Copy connection string:**
   - Go to **Project Settings** -> **Database**.
   - Copy the **URI Connection String** under "Connection Pooling" (use port `6543` for connection pooling with transaction mode).

---

## ⚡ Step 2: Redis Cache & Celery Broker (Upstash)

Because satellite geoprocessing takes time, tasks are enqueued using Celery. Upstash provides a serverless managed Redis broker.

1. **Create an Upstash Redis Database:**
   - Go to [upstash.com](https://upstash.com) and create a Redis database.
2. **Copy Redis URL:**
   - Under the "Details" tab, copy the **Redis Connection URL** (in the format: `rediss://default:password@endpoint.upstash.io:port`).

---

## 🐍 Step 3: Backend Deployment (Render or Koyeb)

The FastAPI backend executes geoprocessing algorithms, runs PyTorch pipelines, and exposes API endpoints.

1. **Create a Web Service on Render:**
   - Go to [render.com](https://render.com) and select **New Web Service**.
   - Connect your GitHub repository.
2. **Configure Service Settings:**
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.5 --port $PORT`
3. **Set Environment Variables:**
   Add the following environment variables in the Render settings:
   - `DATABASE_URL`: *Your Supabase pooled connection string.*
   - `REDIS_URL`: *Your Upstash Redis connection URL.*
   - `GEMINI_API_KEY`: *Your Google AI Studio Gemini API key.*
   - `PYTHONPATH`: `.`

---

## ⚡ Step 4: Frontend Deployment (Vercel)

The Next.js frontend communicates with the FastAPI backend and renders Leaflet map layers.

1. **Create a Project on Vercel:**
   - Go to [vercel.com](https://vercel.com) and select **Add New Project**.
   - Import your GitHub repository.
2. **Configure Build Commands:**
   - **Framework Preset:** `Next.js`
   - **Root Directory:** `frontend/` (set this to point to the frontend folder)
   - **Build Command:** `next build`
   - **Output Directory:** `.next`
3. **Set Frontend Environment Variables:**
   - Add `NEXT_PUBLIC_API_URL`: *The URL of your deployed Render backend (e.g. `https://cloudfreeai-api.onrender.com`).*
4. **Deploy:** Click **Deploy**. Vercel will compile the TypeScript React project and provision your live SSL URL.

---

## 🛠️ Step 5: Local Testing Sandbox (Docker Compose)

If you want to test the entire operational stack locally on your computer with a single command:

1. Make sure you have Docker Desktop installed.
2. Navigate to the project root directory and run:
   ```bash
   docker-compose up --build
   ```
3. Docker will download and boot:
   - PostGIS Database on port `5432`
   - Redis task broker on port `6379`
   - FastAPI Backend API on port `8000`
   - Next.js Web Dashboard on port `3000`
