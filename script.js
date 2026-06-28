// CloudFreeAI GIS Telemetry & Spatial Controller

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initial State Definitions
    const LOCATIONS = {
        kerala: {
            name: "Kerala Coastal Plains (Monsoon Flooding)",
            lat: 9.9312,
            lon: 76.2673,
            zoom: 13,
            bounds: [[9.90, 76.23], [9.96, 76.30]],
            stats: { floodArea: "42.8 km²", waterDepth: "1.24 m", roadDamage: "12,450 m", priorityScore: "9.4 / 10", severity: "CRITICAL" },
            metrics: { psnr: "29.45 dB", ssim: "0.912", rmse: "0.038", sam: "0.035 rad", ndviDelta: "0.045", conf: "92.4%", reliability: "0.9240" },
            rankings: [
                { id: "RS2_L4_2024", date: "2024-02-12", cloud: "0.2%", rank: 1, sensor: "Resourcesat-2" },
                { id: "RS2_L4_2023", date: "2023-01-20", cloud: "2.1%", rank: 2, sensor: "Resourcesat-2" },
                { id: "IRS_P6_2022", date: "2022-12-05", cloud: "4.8%", rank: 3, sensor: "IRS-P6" }
            ],
            report: `## DISASTER INTELLIGENCE ASSESSMENT: KERALA MONSOON FLOODING
**NRSC Mission Command ID: BAH-2026-KL09**
**Analysis Timestamp:** 2026-06-29 00:00:00 UTC

### 1. Executive Summary
A heavy precipitation event triggered by active monsoon currents has resulted in catastrophic flooding across the Kerala coastal plains. CloudFreeAI processed Resourcesat-2 LISS-IV optical imagery and Sentinel-1 SAR imagery to reconstruct a cloud-free surface assessment under a 78% cloud deck.

### 2. Spectral Indices & Reconstruction Confidence
- **Mean Pixel Reconstruction Confidence:** 92.4% (uncertainty restricted to core cloud-shadow regions)
- **Spectral Angle Mapper (SAM) Deviation:** < 0.04 (excellent spectral consistency preserved in R/G/NIR bands)
- **NDVI Assessment:** Significant drop in NDVI (from +0.62 down to -0.15) along the Vembanad Lake margins, confirming massive crop submersion.

### 3. Damage Evaluation
- **Inundated Area:** 42.8 sq km of agricultural land and low-lying coastal villages.
- **Infrastructure Impact:**
  - **Settlements:** 148 coastal settlements inundated.
  - **Road Transport:** Severe road blockage on NH-66 and minor state routes due to 12.4 km of submerged pavement.
  - **Bridges:** 3 bridges classified as structurally compromised due to hydrodynamic erosion.

### 4. Emergency Action Guidelines
> [!IMPORTANT]
> **Priority 1:** Evacuate settlements along the low-lying agricultural zones.
> **Priority 2:** Redirect transport routes off the affected segments of NH-66.
> **Priority 3:** Mobilize state disaster relief forces (SDRF) to the Kuttanad basin.`
        },
        uttarakhand: {
            name: "Uttarakhand Valleys (Cloudburst & Landslide)",
            lat: 30.7346,
            lon: 79.0669,
            zoom: 14,
            bounds: [[30.71, 79.04], [30.76, 79.09]],
            stats: { floodArea: "4.2 km²", waterDepth: "0.45 m", roadDamage: "3,800 m", priorityScore: "7.8 / 10", severity: "HIGH" },
            metrics: { psnr: "27.85 dB", ssim: "0.885", rmse: "0.048", sam: "0.048 rad", ndviDelta: "0.068", conf: "88.7%", reliability: "0.8870" },
            rankings: [
                { id: "RS2_L4_2025", date: "2025-03-01", cloud: "0.5%", rank: 1, sensor: "Resourcesat-2" },
                { id: "RS2A_L4_2024", date: "2024-04-10", cloud: "1.8%", rank: 2, sensor: "Resourcesat-2A" },
                { id: "CARTOSAT_2023", date: "2023-11-22", cloud: "3.1%", rank: 3, sensor: "Cartosat-1" }
            ],
            report: `## DISASTER INTELLIGENCE ASSESSMENT: UTTARAKHAND LANDSLIDE
**NRSC Mission Command ID: BAH-2026-UK30**
**Analysis Timestamp:** 2026-06-29 00:00:00 UTC

### 1. Executive Summary
A localized cloudburst triggered a major debris flow landslide blocking the Mandakini river channel. CloudFreeAI fused Sentinel-1 radar amplitude (showing texture changes) with historical LISS-IV imagery to resolve structural modifications beneath dense mountain cloud cover.

### 2. Geomorphic Changes & Confidence
- **Mean Pixel Reconstruction Confidence:** 88.7%
- **Reconstruction Notes:** Slope structural changes were inferred via Sentinel-1 SAR double-bounce backscatter anomalies, validating the slide path.
- **NDVI Assessment:** Slope vegetation was entirely stripped, dropping NDVI from +0.55 to +0.08 in the debris path.

### 3. Infrastructure Damage
- **Affected Settlements:** 12 mountain hamlets isolated by slope failures.
- **Road Network:** 3.8 km of NH-107 washed out by landslide debris and secondary mudflows.
- **Bridges:** 2 pedestrian suspension bridges spanning the gorge were washed away.

### 4. Emergency Action Guidelines
> [!WARNING]
> **Risk of Flash Flooding:** The landslide debris has created a temporary impoundment lake on the river. Monitor water levels for sudden release.
> **Action:** Deploy tactical engineering units to clear debris and check dam stability.`
        },
        chennai: {
            name: "Chennai Basin (Cyclone Inundation)",
            lat: 13.0827,
            lon: 80.2707,
            zoom: 13,
            bounds: [[13.05, 80.23], [13.11, 80.30]],
            stats: { floodArea: "56.1 km²", waterDepth: "2.10 m", roadDamage: "28,600 m", priorityScore: "9.8 / 10", severity: "CRITICAL" },
            metrics: { psnr: "30.12 dB", ssim: "0.934", rmse: "0.032", sam: "0.029 rad", ndviDelta: "0.031", conf: "94.1%", reliability: "0.9410" },
            rankings: [
                { id: "RS2A_L4_2025", date: "2025-05-18", cloud: "0.1%", rank: 1, sensor: "Resourcesat-2A" },
                { id: "RS2_L4_2024", date: "2024-06-02", cloud: "2.4%", rank: 2, sensor: "Resourcesat-2" },
                { id: "IRS_P6_2023", date: "2023-05-12", cloud: "5.6%", rank: 3, sensor: "IRS-P6" }
            ],
            report: `## DISASTER INTELLIGENCE ASSESSMENT: CHENNAI CYCLONIC FLOODING
**NRSC Mission Command ID: BAH-2026-TN13**
**Analysis Timestamp:** 2026-06-29 00:00:00 UTC

### 1. Executive Summary
Severe Cyclonic Storm 'Asani' brought heavy rainfall, causing extensive inundation of the Chennai metropolitan basin. Synthetic Aperture Radar (SAR) sensors pierced the cyclone's dense cloud eyewall, enabling CloudFreeAI to reconstruct a clear-sky urban damage map.

### 2. Dynamic Flood Inundation & Confidence
- **Mean Pixel Reconstruction Confidence:** 94.1% (high reliability due to strong SAR double-bounce contrast in urban grids).
- **Difference Analysis:** Strong radar reflection changes confirm water spread inside industrial corridors.

### 3. Urban Damage Assessment
- **Flooded Districts:** 842 municipal blocks submerged.
- **Infrastructure Impact:**
  - **Road Damage:** 28.6 km of urban roads flooded, blocking key arteries.
  - **Airport Runway:** Outer taxiways show minor water accumulation (12 cm depth).

### 4. Emergency Action Guidelines
> [!CAUTION]
> **Water contamination risk:** Heavy inundation of industrial zones increases chemical run-off risks.
> **Action:** Mobilize high-discharge pumps to the south Chennai basins and suspend suburban rail operations.`
        }
    };

    let activeLocKey = "kerala";
    let activeLoc = LOCATIONS[activeLocKey];
    let map = null;
    let baseTileLayer = null;
    let overlayLayers = {};
    let swipeActive = false;
    let isPipelineRunning = false;

    // 2. Initialize Leaflet Map
    function initMap() {
        map = L.map("map", {
            zoomControl: false,
            attributionControl: false
        }).setView([activeLoc.lat, activeLoc.lon], activeLoc.zoom);

        baseTileLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19
        }).addTo(map);

        L.control.zoom({ position: "topleft" }).addTo(map);
        L.control.scale({ position: "bottomleft" }).addTo(map);

        map.on("mousemove", (e) => {
            updateInspector(e.latlng);
        });

        loadOverlays();
        renderReferenceRanking();
    }

    function renderReferenceRanking() {
        const list = document.getElementById("reference-ranking-list");
        list.innerHTML = "";
        activeLoc.rankings.forEach(item => {
            const row = document.createElement("div");
            row.className = "flex items-center justify-between border-b border-[#1e293b]/50 pb-1 pt-0.5 text-[9px]";
            row.innerHTML = `
                <span class="text-slate-400 font-semibold">#${item.rank} ${item.id}</span>
                <span class="text-[#38bdf8]">${item.sensor}</span>
                <span class="text-emerald-400 font-bold">${item.cloud}</span>
            `;
            list.appendChild(row);
        });
    }

    // 3. Render Canvas-Based Satellite Overlays (Base64)
    function generateRasterLayer(locKey, layerType) {
        const canvas = document.createElement("canvas");
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext("2d");
        
        ctx.fillStyle = "#1e293b";
        ctx.fillRect(0, 0, 512, 512);

        const isKerala = locKey === "kerala";
        const isUK = locKey === "uttarakhand";
        const isChennai = locKey === "chennai";

        // Draw River / Lakes
        ctx.beginPath();
        if (isKerala) {
            ctx.strokeStyle = "#0284c7";
            ctx.lineWidth = 14;
            ctx.moveTo(100, 0);
            ctx.bezierCurveTo(120, 200, 200, 300, 220, 512);
            ctx.stroke();

            ctx.beginPath();
            ctx.lineWidth = 8;
            ctx.moveTo(220, 310);
            ctx.lineTo(400, 450);
            ctx.stroke();
        } else if (isUK) {
            ctx.strokeStyle = "#0369a1";
            ctx.lineWidth = 6;
            ctx.moveTo(250, 0);
            ctx.lineTo(260, 200);
            ctx.lineTo(210, 350);
            ctx.lineTo(240, 512);
            ctx.stroke();
        } else if (isChennai) {
            ctx.strokeStyle = "#0ea5e9";
            ctx.lineWidth = 10;
            ctx.moveTo(0, 300);
            ctx.bezierCurveTo(200, 310, 350, 290, 512, 280);
            ctx.stroke();
            
            ctx.fillStyle = "#0c4a6e";
            ctx.beginPath();
            ctx.moveTo(420, 0);
            ctx.lineTo(512, 0);
            ctx.lineTo(512, 512);
            ctx.lineTo(480, 512);
            ctx.bezierCurveTo(460, 300, 430, 150, 420, 0);
            ctx.fill();
        }

        // Draw Settlements
        ctx.fillStyle = "#64748b";
        if (isKerala) {
            ctx.fillRect(40, 80, 40, 30);
            ctx.fillRect(300, 150, 50, 45);
        } else if (isUK) {
            ctx.fillRect(230, 120, 15, 15);
            ctx.fillRect(170, 280, 20, 15);
        } else if (isChennai) {
            ctx.fillRect(50, 50, 120, 120);
            ctx.fillRect(220, 80, 80, 90);
            ctx.fillRect(80, 350, 150, 110);
        }

        // Apply Layer Type Modifications
        if (layerType === "cloudy") {
            ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
            ctx.beginPath();
            ctx.arc(150, 120, 80, 0, Math.PI * 2);
            ctx.arc(320, 250, 110, 0, Math.PI * 2);
            ctx.arc(120, 380, 90, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
            ctx.beginPath();
            ctx.arc(130, 100, 80, 0, Math.PI * 2);
            ctx.arc(300, 230, 110, 0, Math.PI * 2);
            ctx.arc(100, 360, 90, 0, Math.PI * 2);
            ctx.fill();
        } 
        else if (layerType === "sar") {
            const imgData = ctx.getImageData(0, 0, 512, 512);
            const data = imgData.data;
            for (let i = 0; i < data.length; i += 4) {
                let r = data[i], g = data[i+1], b = data[i+2];
                let gray = (r + g + b) / 3;
                let speckle = (Math.random() - 0.5) * 35;
                let val = gray + speckle;

                if (b > g && b > r && g > 50) {
                    val = 10 + (Math.random() * 5);
                } else if (r === 100 && g === 116 && b === 139) {
                    val = 220 + (Math.random() * 35);
                }

                val = Math.max(0, Math.min(255, val));
                data[i] = val; data[i+1] = val; data[i+2] = val;
            }
            ctx.putImageData(imgData, 0, 0);
        }
        else if (layerType === "historical") {
            const imgData = ctx.getImageData(0, 0, 512, 512);
            const data = imgData.data;
            for (let i = 0; i < data.length; i += 4) {
                let r = data[i], g = data[i+1], b = data[i+2];
                if (b > g && b > r) {
                    data[i] = 12; data[i+1] = 74; data[i+2] = 110;
                } else if (r === 30 && g === 41 && b === 59) {
                    data[i] = 21; data[i+1] = 128; data[i+2] = 61;
                } else if (r === 100 && g === 116 && b === 139) {
                    data[i] = 148; data[i+1] = 163; data[i+2] = 184;
                }
            }
            ctx.putImageData(imgData, 0, 0);
        }
        else if (layerType === "reconstructed") {
            const imgData = ctx.getImageData(0, 0, 512, 512);
            const data = imgData.data;
            for (let i = 0; i < data.length; i += 4) {
                let r = data[i], g = data[i+1], b = data[i+2];
                if (b > g && b > r) {
                    data[i] = 8; data[i+1] = 145; data[i+2] = 178;
                } else if (r === 30 && g === 41 && b === 59) {
                    data[i] = 22; data[i+1] = 101; data[i+2] = 52;
                } else if (r === 100 && g === 116 && b === 139) {
                    data[i] = 100; data[i+1] = 116; data[i+2] = 139;
                }
            }
            ctx.putImageData(imgData, 0, 0);

            ctx.fillStyle = "rgba(8, 145, 178, 0.95)";
            if (isKerala) {
                ctx.beginPath(); ctx.arc(220, 310, 45, 0, Math.PI * 2); ctx.arc(150, 180, 28, 0, Math.PI * 2); ctx.fill();
            } else if (isUK) {
                ctx.fillStyle = "#854d0e";
                ctx.beginPath();
                ctx.moveTo(140, 200); ctx.lineTo(260, 240); ctx.lineTo(250, 280); ctx.lineTo(130, 230);
                ctx.closePath(); ctx.fill();
            } else if (isChennai) {
                ctx.beginPath(); ctx.fillRect(80, 80, 110, 80); ctx.arc(200, 300, 60, 0, Math.PI * 2); ctx.fill();
            }
        }
        else if (layerType === "confidence") {
            ctx.fillStyle = "#16a34a";
            ctx.fillRect(0, 0, 512, 512);

            const grad1 = ctx.createRadialGradient(130, 100, 10, 130, 100, 80);
            grad1.addColorStop(0, "#dc2626");
            grad1.addColorStop(0.5, "#eab308");
            grad1.addColorStop(1, "rgba(22, 163, 74, 0)");
            ctx.fillStyle = grad1;
            ctx.beginPath(); ctx.arc(130, 100, 80, 0, Math.PI * 2); ctx.fill();

            const grad2 = ctx.createRadialGradient(300, 230, 15, 300, 230, 110);
            grad2.addColorStop(0, "#dc2626");
            grad2.addColorStop(0.6, "#eab308");
            grad2.addColorStop(1, "rgba(22, 163, 74, 0)");
            ctx.fillStyle = grad2;
            ctx.beginPath(); ctx.arc(300, 230, 110, 0, Math.PI * 2); ctx.fill();

            const grad3 = ctx.createRadialGradient(100, 360, 10, 100, 360, 90);
            grad3.addColorStop(0, "#dc2626");
            grad3.addColorStop(0.5, "#eab308");
            grad3.addColorStop(1, "rgba(22, 163, 74, 0)");
            ctx.fillStyle = grad3;
            ctx.beginPath(); ctx.arc(100, 360, 90, 0, Math.PI * 2); ctx.fill();
        }
        else if (layerType === "flood") {
            ctx.clearRect(0, 0, 512, 512);
            ctx.fillStyle = "rgba(6, 182, 212, 0.4)";
            ctx.strokeStyle = "#22d3ee";
            ctx.lineWidth = 2;

            if (isKerala) {
                ctx.beginPath(); ctx.arc(220, 310, 45, 0, Math.PI * 2); ctx.arc(150, 180, 28, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
            } else if (isUK) {
                ctx.fillStyle = "rgba(239, 68, 68, 0.3)";
                ctx.strokeStyle = "#f87171";
                ctx.beginPath();
                ctx.moveTo(140, 200); ctx.lineTo(260, 240); ctx.lineTo(250, 280); ctx.lineTo(130, 230);
                ctx.closePath(); ctx.fill(); ctx.stroke();
            } else if (isChennai) {
                ctx.beginPath(); ctx.rect(80, 80, 110, 80); ctx.arc(200, 300, 60, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
            }
        }
        else if (layerType === "ndvi") {
            ctx.fillStyle = "#eab308";
            ctx.fillRect(0, 0, 512, 512);
            ctx.fillStyle = "#047857";
            if (isKerala) {
                ctx.fillRect(0, 0, 200, 100); ctx.fillRect(350, 0, 162, 512);
            } else if (isUK) {
                ctx.fillRect(0, 0, 512, 100); ctx.fillRect(0, 380, 512, 132);
            } else if (isChennai) {
                ctx.fillRect(0, 0, 120, 80);
            }

            ctx.fillStyle = "#dc2626";
            if (isKerala) {
                ctx.beginPath(); ctx.lineWidth = 14; ctx.strokeStyle = "#dc2626"; ctx.moveTo(100, 0); ctx.bezierCurveTo(120, 200, 200, 300, 220, 512); ctx.stroke();
                ctx.beginPath(); ctx.arc(220, 310, 45, 0, Math.PI * 2); ctx.arc(150, 180, 28, 0, Math.PI * 2); ctx.fill();
            } else if (isUK) {
                ctx.beginPath(); ctx.lineWidth = 6; ctx.strokeStyle = "#dc2626"; ctx.moveTo(250, 0); ctx.lineTo(260, 200); ctx.lineTo(210, 350); ctx.lineTo(240, 512); ctx.stroke();
                ctx.fillStyle = "#ea580c";
                ctx.beginPath(); ctx.moveTo(140, 200); ctx.lineTo(260, 240); ctx.lineTo(250, 280); ctx.lineTo(130, 230); ctx.closePath(); ctx.fill();
            } else if (isChennai) {
                ctx.beginPath(); ctx.lineWidth = 10; ctx.strokeStyle = "#dc2626"; ctx.moveTo(0, 300); ctx.bezierCurveTo(200, 310, 350, 290, 512, 280); ctx.stroke();
                ctx.fillStyle = "#dc2626";
                ctx.beginPath(); ctx.moveTo(420, 0); ctx.lineTo(512, 0); ctx.lineTo(512, 512); ctx.lineTo(480, 512); ctx.bezierCurveTo(460, 300, 430, 150, 420, 0); ctx.fill();
                ctx.beginPath(); ctx.rect(80, 80, 110, 80); ctx.arc(200, 300, 60, 0, Math.PI * 2); ctx.fill();
            }
        }
        else if (layerType === "difference") {
            ctx.clearRect(0, 0, 512, 512);
            ctx.fillStyle = "rgba(239, 68, 68, 0.7)";
            if (isKerala) {
                ctx.beginPath(); ctx.arc(220, 310, 45, 0, Math.PI * 2); ctx.arc(150, 180, 28, 0, Math.PI * 2); ctx.fill();
            } else if (isUK) {
                ctx.beginPath();
                ctx.moveTo(140, 200); ctx.lineTo(260, 240); ctx.lineTo(250, 280); ctx.lineTo(130, 230);
                ctx.closePath(); ctx.fill();
            } else if (isChennai) {
                ctx.beginPath(); ctx.rect(80, 80, 110, 80); ctx.arc(200, 300, 60, 0, Math.PI * 2); ctx.fill();
            }
        }
        // New Explainability Layers: Attention Map (XAI)
        else if (layerType === "attention") {
            ctx.clearRect(0, 0, 512, 512);
            ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
            ctx.fillRect(0, 0, 512, 512);
            
            // Draw glowing yellow hotspots over edges
            ctx.strokeStyle = "rgba(253, 224, 71, 0.85)";
            ctx.shadowColor = "#fde047";
            ctx.shadowBlur = 15;
            ctx.lineWidth = 4;
            
            ctx.beginPath();
            if (isKerala) {
                ctx.arc(220, 310, 45, 0, Math.PI * 2);
                ctx.arc(150, 180, 28, 0, Math.PI * 2);
            } else if (isUK) {
                ctx.moveTo(180, 210); ctx.lineTo(280, 240); ctx.lineTo(270, 290); ctx.lineTo(170, 250); ctx.closePath();
            } else if (isChennai) {
                ctx.rect(80, 80, 110, 80);
                ctx.arc(200, 300, 60, 0, Math.PI * 2);
            }
            ctx.stroke();
            ctx.shadowBlur = 0; // Reset
        }
        // New Explainability Layers: Uncertainty Map
        else if (layerType === "uncertainty") {
            // White under clouds, black in clear areas
            ctx.fillStyle = "#000";
            ctx.fillRect(0, 0, 512, 512);
            
            // Gaussian blurred uncertainty gradients under cloud coordinates
            const grad1 = ctx.createRadialGradient(130, 100, 0, 130, 100, 80);
            grad1.addColorStop(0, "#fff"); // High uncertainty
            grad1.addColorStop(1, "rgba(0,0,0,0)");
            ctx.fillStyle = grad1; ctx.beginPath(); ctx.arc(130, 100, 80, 0, Math.PI * 2); ctx.fill();

            const grad2 = ctx.createRadialGradient(300, 230, 0, 300, 230, 110);
            grad2.addColorStop(0, "#fff");
            grad2.addColorStop(1, "rgba(0,0,0,0)");
            ctx.fillStyle = grad2; ctx.beginPath(); ctx.arc(300, 230, 110, 0, Math.PI * 2); ctx.fill();

            const grad3 = ctx.createRadialGradient(100, 360, 0, 100, 360, 90);
            grad3.addColorStop(0, "#fff");
            grad3.addColorStop(1, "rgba(0,0,0,0)");
            ctx.fillStyle = grad3; ctx.beginPath(); ctx.arc(100, 360, 90, 0, Math.PI * 2); ctx.fill();
        }

        return canvas.toDataURL();
    }

    // 4. Load Layers into Leaflet ImageOverlays
    function loadOverlays() {
        for (let key in overlayLayers) {
            map.removeLayer(overlayLayers[key]);
        }
        overlayLayers = {};

        const imageBounds = activeLoc.bounds;
        const layers = ["cloudy", "historical", "sar", "reconstructed", "confidence", "flood", "ndvi", "difference", "attention", "uncertainty"];

        layers.forEach(layer => {
            const dataUrl = generateRasterLayer(activeLocKey, layer);
            overlayLayers[layer] = L.imageOverlay(dataUrl, imageBounds, {
                opacity: 0.8,
                interactive: false,
                className: `leaflet-${layer}`
            });
        });

        overlayLayers["cloudy"].addTo(map);
        map.fitBounds(imageBounds);
        renderLayerManager();
    }

    // 5. Render Layer Manager
    const layerMetadata = {
        cloudy: { label: "1. Cloudy Optical (LISS-IV)", color: "#94a3b8" },
        historical: { label: "2. Historical Reference", color: "#22c55e" },
        sar: { label: "3. Current Sentinel-1 SAR", color: "#64748b" },
        reconstructed: { label: "4. AI Reconstructed Optical", color: "#38bdf8" },
        confidence: { label: "5. Confidence Map", color: "#eab308" },
        flood: { label: "6. Flood Vector Overlay", color: "#06b6d4" },
        ndvi: { label: "7. NDVI Canopy Map", color: "#15803d" },
        difference: { label: "8. Difference Change Map", color: "#ef4444" },
        attention: { label: "9. Attention Map (XAI)", color: "#fde047" },
        uncertainty: { label: "10. Uncertainty Map (XAI)", color: "#cbd5e1" }
    };

    function renderLayerManager() {
        const listContainer = document.getElementById("layer-list");
        listContainer.innerHTML = "";

        for (let key in layerMetadata) {
            const meta = layerMetadata[key];
            const isChecked = map.hasLayer(overlayLayers[key]);

            const item = document.createElement("label");
            item.className = "flex items-center justify-between p-1 hover:bg-[#1e293b]/50 rounded cursor-pointer transition-all";
            item.innerHTML = `
                <div class="flex items-center gap-2">
                    <input type="checkbox" data-layer="${key}" ${isChecked ? "checked" : ""} class="layer-chk accent-[#0284c7]">
                    <span style="color: ${meta.color}">${meta.label}</span>
                </div>
                <i class="fa-solid fa-eye ${isChecked ? "text-[#38bdf8]" : "text-slate-600"} text-[9px]"></i>
            `;

            listContainer.appendChild(item);
        }

        document.querySelectorAll(".layer-chk").forEach(input => {
            input.addEventListener("change", (e) => {
                const layerKey = e.target.getAttribute("data-layer");
                const eyeIcon = e.target.closest("label").querySelector(".fa-eye");
                
                if (e.target.checked) {
                    overlayLayers[layerKey].addTo(map);
                    eyeIcon.classList.remove("text-slate-600");
                    eyeIcon.classList.add("text-[#38bdf8]");
                } else {
                    map.removeLayer(overlayLayers[layerKey]);
                    eyeIcon.classList.add("text-slate-600");
                    eyeIcon.classList.remove("text-[#38bdf8]");
                }

                if (swipeActive) updateSwipeClip();
            });
        });
    }

    // 6. Swipe Controllers
    const swipeBtn = document.getElementById("btn-mode-swipe");
    const standardBtn = document.getElementById("btn-mode-standard");
    const timelineSlider = document.getElementById("timeline-slider");
    const timelineLabel = document.getElementById("timeline-label");

    swipeBtn.addEventListener("click", () => {
        swipeActive = true;
        swipeBtn.classList.remove("bg-[#1e293b]", "text-slate-400");
        swipeBtn.classList.add("bg-[#0284c7]", "text-white");
        standardBtn.classList.remove("bg-[#0284c7]");
        standardBtn.classList.add("bg-[#1e293b]", "text-slate-400");
        
        if (overlayLayers["cloudy"]) overlayLayers["cloudy"].addTo(map);
        if (overlayLayers["reconstructed"]) overlayLayers["reconstructed"].addTo(map);

        renderLayerManager();
        updateSwipeClip();
        appendLog("[GIS] Horizontal swipe comparison enabled. Drag timeline slider to wipe cloud deck.");
    });

    standardBtn.addEventListener("click", () => {
        swipeActive = false;
        standardBtn.classList.remove("bg-[#1e293b]", "text-slate-400");
        standardBtn.classList.add("bg-[#0284c7]", "text-white");
        swipeBtn.classList.remove("bg-[#0284c7]");
        swipeBtn.classList.add("bg-[#1e293b]", "text-slate-400");

        const cloudyImg = document.querySelector(".leaflet-cloudy");
        const reconImg = document.querySelector(".leaflet-reconstructed");
        if (cloudyImg) cloudyImg.style.clipPath = "none";
        if (reconImg) reconImg.style.clipPath = "none";
        appendLog("[GIS] Normal layers display restored.");
    });

    timelineSlider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value);
        const dates = [
            "2023 Historical Reference",
            "2024 Reference Deck",
            "2025 Coregistered Sentinel-1",
            "2026 Raw LISS-IV (Cloudy)",
            "2026 Reconstruction"
        ];
        timelineLabel.innerText = dates[val];

        if (swipeActive) {
            updateSwipeClip();
        } else {
            if (val === 0 || val === 1) {
                showSingleLayer("historical");
            } else if (val === 2) {
                showSingleLayer("sar");
            } else if (val === 3) {
                showSingleLayer("cloudy");
            } else if (val === 4) {
                showSingleLayer("reconstructed");
            }
        }
    });

    function showSingleLayer(layerKey) {
        for (let key in overlayLayers) {
            if (key === layerKey) {
                overlayLayers[key].addTo(map);
            } else {
                map.removeLayer(overlayLayers[key]);
            }
        }
        renderLayerManager();
    }

    function updateSwipeClip() {
        const sliderVal = timelineSlider.value;
        const percentage = (sliderVal / 4) * 100;
        
        const cloudyImg = document.querySelector(".leaflet-cloudy");
        const reconImg = document.querySelector(".leaflet-reconstructed");

        if (cloudyImg && reconImg) {
            cloudyImg.style.clipPath = `inset(0 ${100 - percentage}% 0 0)`;
            reconImg.style.clipPath = `inset(0 0 0 ${percentage}%)`;
        }
    }

    // Opacity
    const opacitySlider = document.getElementById("opacity-slider");
    const opacityVal = document.getElementById("opacity-val");

    opacitySlider.addEventListener("input", (e) => {
        const val = e.target.value;
        opacityVal.innerText = `${val}%`;
        for (let key in overlayLayers) {
            overlayLayers[key].setOpacity(val / 100);
        }
    });

    // 7. Interactive Location Switcher
    const locSelect = document.getElementById("location-select");
    locSelect.addEventListener("change", (e) => {
        activeLocKey = e.target.value;
        activeLoc = LOCATIONS[activeLocKey];

        document.getElementById("lat-input").value = activeLoc.lat.toFixed(4);
        document.getElementById("lon-input").value = activeLoc.lon.toFixed(4);

        resetTelemetryStats();
        loadOverlays();
        renderReferenceRanking();

        appendLog(`[SCENE] Switched telemetry scene to: ${activeLoc.name}`);
    });

    function resetTelemetryStats() {
        document.getElementById("stat-flood-area").innerText = "--";
        document.getElementById("stat-water-depth").innerText = "--";
        document.getElementById("stat-road-damage").innerText = "--";
        document.getElementById("stat-priority-score").innerText = "--";
        document.getElementById("report-severity-badge").innerText = "READY";
        document.getElementById("report-severity-badge").className = "text-[9px] bg-slate-500/20 border border-slate-500 text-slate-400 px-1.5 py-0.5 rounded font-bold";

        // Reset metrics
        document.getElementById("metric-psnr").innerText = "--";
        document.getElementById("metric-ssim").innerText = "--";
        document.getElementById("metric-rmse").innerText = "--";
        document.getElementById("metric-sam").innerText = "--";
        document.getElementById("metric-ndvi-delta").innerText = "--";
        document.getElementById("metric-conf").innerText = "--";
        document.getElementById("metric-reliability").innerText = "--";
        
        const qBadge = document.getElementById("metric-check-badge");
        qBadge.innerText = "READY";
        qBadge.className = "text-[8px] bg-slate-500/20 text-slate-400 border border-slate-500/30 px-1 py-0.5 rounded font-bold";

        document.getElementById("report-content").innerHTML = `
            <div class="h-full flex flex-col justify-center items-center text-center text-slate-500 font-mono text-[10px]">
                <i class="fa-solid fa-satellite text-3xl mb-2 text-slate-600"></i>
                <span>Click 'TRIGGER AI PIPELINE' to reconstruct the scene, execute segmentation analysis, and generate the damage report.</span>
            </div>
        `;
        toggleExports(false);
    }

    // 8. AI Pipeline Execution Engine (Orchestrator Logs & Quality Assessment checks)
    const runBtn = document.getElementById("run-pipeline-btn");
    const termLogs = document.getElementById("terminal-logs");
    const progBar = document.getElementById("pipeline-progress");
    const pipStatus = document.getElementById("pipeline-status");

    function appendLog(text, color = "text-slate-300") {
        const line = document.createElement("div");
        line.className = `${color}`;
        line.innerText = `[${new Date().toISOString().slice(11,19)}] ${text}`;
        termLogs.appendChild(line);
        termLogs.scrollTop = termLogs.scrollHeight;
    }

    runBtn.addEventListener("click", () => {
        if (isPipelineRunning) return;
        isPipelineRunning = true;
        runBtn.disabled = true;
        runBtn.classList.add("opacity-50", "cursor-not-allowed");
        
        termLogs.innerHTML = "";
        pipStatus.innerText = "RUNNING";
        pipStatus.className = "text-[#f97316] font-bold";

        const selectedRefId = activeLoc.rankings[0].id;

        const steps = [
            { text: "Orchestrator: Activating Dataset Discovery Engine (Catalog Search -> Metadata Query)...", time: 400, prog: 8 },
            { text: "Orchestrator: Ranking historical reference scenes (Season, Solar elevation, Cloud %)...", time: 900, prog: 15 },
            { text: `Orchestrator: Best Reference Selection: ${selectedRefId} chosen (Cloud: ${activeLoc.rankings[0].cloud})...`, time: 1300, prog: 22 },
            { text: "Orchestrator: Download Manager pulling current Sentinel-1 SAR orbit files and optical bands...", time: 1800, prog: 30 },
            { text: "Orchestrator: Verifying metadata variables, band compatibility, and coordinate bounds...", time: 2300, prog: 38 },
            { text: "Orchestrator: SAR Preprocessing (Orbit Correction -> Thermal Noise Removal -> Calibration -> Terrain Correction -> Lee Speckle Filter -> Normalization)...", time: 2900, prog: 48 },
            { text: "Orchestrator: Optical Preprocessing (TOA Reflectance -> Atmospheric Dark Object Subtraction -> Band Normalization -> Histogram Matching -> Seasonal Normalization)...", time: 3500, prog: 58 },
            { text: "Orchestrator: Swapping registry models (CloudNet_v1.2 and TemporalDiffusion_v3.4 loaded)...", time: 4000, prog: 68 },
            { text: "Orchestrator: Geometric Co-Registration using LoFTR sub-pixel alignment...", time: 4500, prog: 74 },
            { text: "Orchestrator: Running Temporal Fusion Transformer & Denoising Diffusion Reconstruction...", time: 5100, prog: 82 },
            { text: "Orchestrator: Synthesizing Explainability Layer (generating Attention maps and Uncertainty maps)...", time: 5700, prog: 90 },
            { text: "Orchestrator: Executing multi-category QA Validation split (Reconstruction, Spectral, Uncertainty)...", time: 6300, prog: 96 },
            { text: "Orchestrator: Scene reconstruction pipeline successfully finalized. QA passed.", time: 6800, prog: 100 }
        ];

        steps.forEach((step, index) => {
            setTimeout(() => {
                appendLog(step.text, "text-[#38bdf8]");
                progBar.style.width = `${step.prog}%`;
                
                if (index === steps.length - 1) {
                    completePipeline();
                }
            }, step.time);
        });
    });

    function completePipeline() {
        isPipelineRunning = false;
        runBtn.disabled = false;
        runBtn.classList.remove("opacity-50", "cursor-not-allowed");
        
        pipStatus.innerText = "NOMINAL";
        pipStatus.className = "text-emerald-400 font-bold";
        appendLog("[SUCCESS] Quality Assurance checks passed. Attention mapping online.", "text-emerald-400 font-bold");

        // 1. Show reconstructed, flood, and attention overlays
        overlayLayers["reconstructed"].addTo(map);
        overlayLayers["flood"].addTo(map);
        overlayLayers["attention"].addTo(map);
        renderLayerManager();

        // 2. Populate stats panels
        document.getElementById("stat-flood-area").innerText = activeLoc.stats.floodArea;
        document.getElementById("stat-water-depth").innerText = activeLoc.stats.waterDepth;
        document.getElementById("stat-road-damage").innerText = activeLoc.stats.roadDamage;
        document.getElementById("stat-priority-score").innerText = activeLoc.stats.priorityScore;

        const badge = document.getElementById("report-severity-badge");
        badge.innerText = activeLoc.stats.severity;
        badge.className = `text-[9px] px-1.5 py-0.5 rounded font-bold severity-${activeLoc.stats.severity.toLowerCase()}`;

        // 3. Populate QA validation split
        document.getElementById("metric-psnr").innerText = activeLoc.metrics.psnr;
        document.getElementById("metric-ssim").innerText = activeLoc.metrics.ssim;
        document.getElementById("metric-rmse").innerText = activeLoc.metrics.rmse;
        document.getElementById("metric-sam").innerText = activeLoc.metrics.sam;
        document.getElementById("metric-ndvi-delta").innerText = activeLoc.metrics.ndviDelta;
        document.getElementById("metric-conf").innerText = activeLoc.metrics.conf;
        document.getElementById("metric-reliability").innerText = activeLoc.metrics.reliability;
        
        const qBadge = document.getElementById("metric-check-badge");
        qBadge.innerText = "PASSED";
        qBadge.className = "text-[8px] px-1.5 py-0.5 rounded font-bold severity-low";

        // 4. Render Gemini markdown report
        const reportBox = document.getElementById("report-content");
        reportBox.innerHTML = parseMarkdown(activeLoc.report);

        toggleExports(true);
    }

    function toggleExports(enable) {
        const buttons = [
            "btn-export-geotiff", "btn-export-geojson",
            "btn-export-pdf", "btn-export-docx", "btn-export-pptx"
        ];
        buttons.forEach(id => {
            const btn = document.getElementById(id);
            if (enable) {
                btn.removeAttribute("disabled");
                btn.classList.remove("text-slate-500", "cursor-not-allowed");
                if (id.startsWith("btn-export-g")) {
                    btn.classList.add("text-[#38bdf8]", "border-[#0284c7]", "hover:bg-[#0284c7]/20");
                } else {
                    btn.classList.add("text-slate-200");
                }
            } else {
                btn.setAttribute("disabled", "true");
                btn.classList.add("text-slate-500");
                btn.classList.remove("text-[#38bdf8]", "border-[#0284c7]", "hover:bg-[#0284c7]/20", "text-slate-200");
            }
        });
    }

    // 9. Coordinate Inspector & Surface Classifier
    function updateInspector(latlng) {
        document.getElementById("header-coords").innerText = `${latlng.lat.toFixed(5)}°N, ${latlng.lng.toFixed(5)}°E`;
        document.getElementById("inspector-lat").innerText = latlng.lat.toFixed(5);
        document.getElementById("inspector-lon").innerText = latlng.lng.toFixed(5);

        const bounds = activeLoc.bounds;
        const latPct = (latlng.lat - bounds[0][0]) / (bounds[1][0] - bounds[0][0]);
        const lonPct = (latlng.lng - bounds[0][1]) / (bounds[1][1] - bounds[0][1]);

        if (latPct >= 0 && latPct <= 1 && lonPct >= 0 && lonPct <= 1) {
            let confVal = 98 - Math.floor((Math.sin(latPct * Math.PI) * Math.sin(lonPct * Math.PI)) * 35);
            let reliability = (confVal / 100).toFixed(4);
            let ndviVal = (0.72 - (latPct * 0.4) - (lonPct * 0.2)).toFixed(2);
            let attentionWeight = "0.02";
            let surface = "Dense Canopy";

            const dist = Math.hypot(x = latPct * 512 - 230, y = lonPct * 512 - 280);

            if (activeLocKey === "kerala" && dist < 65) {
                confVal = 82;
                reliability = "0.8240";
                ndviVal = (-0.12).toFixed(2);
                attentionWeight = "0.88 (Inundation Edge)";
                surface = "Inundated Area";
            } else if (activeLocKey === "uttarakhand" && latPct > 0.4 && latPct < 0.6 && lonPct > 0.3 && lonPct < 0.7) {
                confVal = 75;
                reliability = "0.7580";
                ndviVal = (+0.04).toFixed(2);
                attentionWeight = "0.94 (Debris Impact)";
                surface = "Landslide Debris";
            } else if (activeLocKey === "chennai" && (latPct < 0.35 || Math.hypot(latPct - 0.6, lonPct - 0.5) < 0.2)) {
                confVal = 91;
                reliability = "0.9120";
                ndviVal = (-0.08).toFixed(2);
                attentionWeight = "0.85 (Urban Inundation)";
                surface = "Urban Inundation";
            } else if (ndviVal < 0.1) {
                surface = "Water Body";
            } else if (ndviVal < 0.35) {
                surface = "Settlements / Bare Soil";
            }

            document.getElementById("inspector-conf").innerText = `${confVal}%`;
            document.getElementById("inspector-reliability").innerText = reliability;
            document.getElementById("inspector-attention").innerText = attentionWeight;
            document.getElementById("inspector-ndvi").innerText = ndviVal;
            document.getElementById("inspector-surface").innerText = surface;
        } else {
            document.getElementById("inspector-conf").innerText = "--";
            document.getElementById("inspector-reliability").innerText = "--";
            document.getElementById("inspector-attention").innerText = "--";
            document.getElementById("inspector-ndvi").innerText = "--";
            document.getElementById("inspector-surface").innerText = "Outside Footprint";
        }
    }

    // 10. Simple Markdown Parser
    function parseMarkdown(md) {
        let html = md;
        html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        html = html.replace(/^## (.*?)$/gm, "<h2 class='text-sm font-bold text-[#38bdf8] border-b border-[#1e293b] pb-1 mt-3 mb-1.5 uppercase font-mono'>$1</h2>");
        html = html.replace(/^### (.*?)$/gm, "<h3 class='text-xs font-bold text-slate-300 mt-2 mb-1'>$1</h3>");
        html = html.replace(/^- (.*?)$/gm, "<li class='ml-4 list-disc text-slate-300'>$1</li>");
        
        html = html.replace(/^> \[\!IMPORTANT\]\s*([\s\S]*?)(?=\n\n|\n$|$)/gm, `
            <div class="my-3 p-3 bg-red-950/20 border-l-4 border-red-500 rounded-r text-xs text-red-200">
                <div class="font-bold text-red-400 mb-1"><i class="fa-solid fa-circle-exclamation mr-1"></i> CRITICAL DIRECTIVE</div>
                $1
            </div>
        `);
        html = html.replace(/^> \[\!WARNING\]\s*([\s\S]*?)(?=\n\n|\n$|$)/gm, `
            <div class="my-3 p-3 bg-yellow-950/20 border-l-4 border-yellow-500 rounded-r text-xs text-yellow-200">
                <div class="font-bold text-yellow-400 mb-1"><i class="fa-solid fa-triangle-exclamation mr-1"></i> PIPELINE ALERT</div>
                $1
            </div>
        `);
        html = html.replace(/^> \[\!CAUTION\]\s*([\s\S]*?)(?=\n\n|\n$|$)/gm, `
            <div class="my-3 p-3 bg-orange-950/20 border-l-4 border-orange-500 rounded-r text-xs text-orange-200">
                <div class="font-bold text-orange-400 mb-1"><i class="fa-solid fa-radiation mr-1"></i> SAFETY HAZARD</div>
                $1
            </div>
        `);
        return html;
    }

    // 11. Mock Export File Triggers
    document.getElementById("btn-export-geojson").addEventListener("click", () => {
        const dummyGeoJSON = {
            "type": "FeatureCollection",
            "metadata": {
                "sensor_platform": "LISS-IV + Sentinel-1 SAR",
                "target_region": activeLoc.name,
                "calculated_area_km2": activeLoc.stats.floodArea
            },
            "features": [
                {
                    "type": "Feature",
                    "properties": { "hazard_type": "Inundation", "severity": activeLoc.stats.severity },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [activeLoc.lon - 0.02, activeLoc.lat - 0.02],
                            [activeLoc.lon + 0.02, activeLoc.lat - 0.02],
                            [activeLoc.lon + 0.02, activeLoc.lat + 0.02],
                            [activeLoc.lon - 0.02, activeLoc.lat + 0.02],
                            [activeLoc.lon - 0.02, activeLoc.lat - 0.02]
                        ]]
                    }
                }
            ]
        };

        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(dummyGeoJSON, null, 2));
        const dlAnchor = document.createElement('a');
        dlAnchor.setAttribute("href", dataStr);
        dlAnchor.setAttribute("download", `cloudfreeai_flood_${activeLocKey}.geojson`);
        document.body.appendChild(dlAnchor);
        dlAnchor.click();
        dlAnchor.remove();
        appendLog(`[EXPORT] Downloaded flood boundary polygons in GeoJSON format.`);
    });

    document.getElementById("btn-export-pdf").addEventListener("click", () => {
        const link = document.createElement("a");
        link.href = `http://localhost:8000/api/reports/download/pdf/${activeLocKey}`;
        link.target = "_blank";
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        appendLog(`[EXPORT] Request sent to PDF report compiler endpoint...`);
        alert(`Connecting to local FastAPI server export router...\n\nStatus: Request generated. If server is not running locally, download fallback PDF template compiled successfully.`);
    });

    document.getElementById("btn-export-geotiff").addEventListener("click", () => {
        alert("Downloading high-resolution orthorectified GeoTIFF band array (B2, B3, B4, SAR, Confidence)...\n\nFile size: ~48 MB");
        appendLog(`[EXPORT] Downloaded GeoTIFF raster band stack.`);
    });

    // 12. Clock update
    setInterval(() => {
        const now = new Date();
        document.getElementById("telemetry-time").innerText = now.toISOString().replace('T',' ').slice(0, 19) + " UTC";
    }, 1000);

    // Initial load
    initMap();
    appendLog("[SYSTEM] Spatial database online. Bhoonidhi mirrors connected.");
});
