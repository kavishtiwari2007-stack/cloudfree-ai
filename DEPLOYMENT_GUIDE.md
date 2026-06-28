# CloudFreeAI: Production Deployment Walkthrough

This guide details how to link your initialized local Git repository to your personal accounts on **GitHub**, **Vercel**, **Supabase**, and **Railway** to deploy the complete platform.

---

## Step 1: Uploading Code to GitHub
1. Open your browser and navigate to [GitHub](https://github.com).
2. Log in and click **New Repository** (Top-right `+` icon).
3. Name it `cloudfree-ai` (leave it public or private, but do **NOT** check "Add a README", "Add .gitignore", or "Choose a license" since we already created those).
4. Copy the repository URL (it will look like `https://github.com/YOUR_USERNAME/cloudfree-ai.git`).
5. Open your terminal in `d:\antigravity programss\isro program` and run:
   ```bash
   # Add your GitHub repository as the remote origin
   git remote add origin https://github.com/YOUR_USERNAME/cloudfree-ai.git

   # Push the main branch to GitHub
   git push -u origin main
   ```

---

## Step 2: Provisioning the Database (Supabase)
Supabase provides PostgreSQL database clusters out of the box with native GIS support.
1. Log in to [Supabase](https://supabase.com) and click **New Project**.
2. Select your organization, name the database `cloudfree_gis`, set a secure database password, and create the project.
3. Once the database is ready, go to **Database** (left sidebar menu) -> **Extensions**.
4. Search for `postgis` and toggle it **ON** to enable spatial database capabilities.
5. Go to **SQL Editor** (left sidebar menu) -> click **New Query**.
6. Open the local file **`schema.sql`** in a text editor, copy its entire contents, paste it into the Supabase SQL editor, and click **Run**.
7. Go to **Project Settings** (bottom-left gear icon) -> **Database**.
8. Scroll down to **Connection string** -> select **URI** -> copy the connection string (replace `[YOUR-PASSWORD]` with your database password).
   - *Example URI:* `postgresql://postgres.xxx:PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

---

## Step 3: Deploying the Backend API & Workers (Railway)
Railway runs containerized Docker applications and Celery background workers.
1. Log in to [Railway](https://railway.app) and click **New Project**.
2. Select **Deploy from GitHub repo** and select your `cloudfree-ai` repository.
3. Click **Configure Service**:
   - Set the root directory to `backend`.
4. Click **Variables** (Environment variables tab) and add:
   - `DATABASE_URL` = (Paste the Supabase Connection URI from Step 2)
   - `REDIS_URL` = (You can add a free Redis service inside your Railway project workspace and link its reference URL here)
   - `GEMINI_API_KEY` = (Add your Google Gemini API Key)
5. Railway will automatically find the `Dockerfile` inside the `backend` folder and deploy your FastAPI backend.
6. Copy the public domain URL assigned by Railway (e.g., `https://backend-production.up.railway.app`).

---

## Step 4: Deploying the Frontend Client (Vercel)
Vercel is optimized for building and serving Next.js applications.
1. Log in to [Vercel](https://vercel.com) and click **Add New** -> **Project**.
2. Import your `cloudfree-ai` GitHub repository.
3. In the project setup panel:
   - **Framework Preset:** Select `Next.js`.
   - **Root Directory:** Edit and select `frontend`.
4. Click **Environment Variables** and add:
   - `NEXT_PUBLIC_API_URL` = (Paste your Railway backend public URL from Step 3)
5. Click **Deploy**. Vercel will compile the Next.js assets and host your GIS client dashboard.
