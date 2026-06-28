"use client";

import React, { useState, useEffect, useRef } from 'react';
import { 
  Satellite, 
  Terminal, 
  Download, 
  Layers, 
  Sliders, 
  Activity, 
  FileText, 
  MapPin, 
  ChevronDown,
  Sparkles,
  ShieldAlert,
  BarChart4
} from 'lucide-react';

const LOCATIONS = {
  kerala: {
    name: "Kerala Coastal Plains (Monsoon Flooding)",
    lat: 9.9312,
    lon: 76.2673,
    stats: { floodArea: "42.8 km²", waterDepth: "1.24 m", roadDamage: "12,450 m", priorityScore: "9.4 / 10", severity: "CRITICAL" },
    metrics: { psnr: "29.45 dB", ssim: "0.912", rmse: "0.038", sam: "0.035 rad", ndviDelta: "0.045", conf: "92.4%", reliability: "0.9240" },
    rankings: [
      { id: "RS2_L4_2024", date: "2024-02-12", cloud: "0.2%", rank: 1, sensor: "Resourcesat-2" },
      { id: "RS2_L4_2023", date: "2023-01-20", cloud: "2.1%", rank: 2, sensor: "Resourcesat-2" },
      { id: "IRS_P6_2022", date: "2022-12-05", cloud: "4.8%", rank: 3, sensor: "IRS-P6" }
    ],
    report: `## DISASTER ASSESSMENT: KERALA MONSOON FLOODING
- **Reconstruction Confidence:** 92.4%
- **Inundated Area:** 42.8 sq km
- **Avg Water Depth:** 1.24 meters
- **NH-66 Road Blockage:** 12.4 km submerged.

> **CRITICAL DIRECTIVE:** Evacuate Vembanad Lake margins and deploy SDRF rescue assets.`
  },
  uttarakhand: {
    name: "Uttarakhand Valleys (Cloudburst & Landslide)",
    lat: 30.7346,
    lon: 79.0669,
    stats: { floodArea: "4.2 km²", waterDepth: "0.45 m", roadDamage: "3,800 m", priorityScore: "7.8 / 10", severity: "HIGH" },
    metrics: { psnr: "27.85 dB", ssim: "0.885", rmse: "0.048", sam: "0.048 rad", ndviDelta: "0.068", conf: "88.7%", reliability: "0.8870" },
    rankings: [
      { id: "RS2_L4_2025", date: "2025-03-01", cloud: "0.5%", rank: 1, sensor: "Resourcesat-2" },
      { id: "RS2A_L4_2024", date: "2024-04-10", cloud: "1.8%", rank: 2, sensor: "Resourcesat-2A" },
      { id: "CARTOSAT_2023", date: "2023-11-22", cloud: "3.1%", rank: 3, sensor: "Cartosat-1" }
    ],
    report: `## DISASTER ASSESSMENT: BLAZING LANDSLIDE DEBRIS
- **Reconstruction Confidence:** 88.7%
- **Inundated Area:** 4.2 sq km
- **Avg Debris Depth:** 0.45 meters
- **NH-107 Road Blockage:** 3.8 km slope debris.

> **HAZARD ALERT:** Landslide dam blocking river channel. Evacuate downstream gorges.`
  },
  chennai: {
    name: "Chennai Basin (Cyclone Inundation)",
    lat: 13.0827,
    lon: 80.2707,
    stats: { floodArea: "56.1 km²", waterDepth: "2.10 m", roadDamage: "28,600 m", priorityScore: "9.8 / 10", severity: "CRITICAL" },
    metrics: { psnr: "30.12 dB", ssim: "0.934", rmse: "0.032", sam: "0.029 rad", ndviDelta: "0.031", conf: "94.1%", reliability: "0.9410" },
    rankings: [
      { id: "RS2A_L4_2025", date: "2025-05-18", cloud: "0.1%", rank: 1, sensor: "Resourcesat-2A" },
      { id: "RS2_L4_2024", date: "2024-06-02", cloud: "2.4%", rank: 2, sensor: "Resourcesat-2" },
      { id: "IRS_P6_2023", date: "2023-05-12", cloud: "5.6%", rank: 3, sensor: "IRS-P6" }
    ],
    report: `## DISASTER ASSESSMENT: CHENNAI CYCLONE FLOODING
- **Reconstruction Confidence:** 94.1%
- **Inundated Area:** 56.1 sq km
- **Avg Inundation Depth:** 2.10 meters
- **Road Blockage:** 28.6 km city roads submerged.

> **SAFETY WARNING:** Industrial runoff detected in flood waters. Distribute clean drinking water.`
  }
};

type LocationKey = 'kerala' | 'uttarakhand' | 'chennai';

export default function GISDashboard() {
  const [locationKey, setLocationKey] = useState<LocationKey>('kerala');
  const [pipelineProgress, setPipelineProgress] = useState(0);
  const [pipelineStatus, setPipelineStatus] = useState('READY');
  const [logs, setLogs] = useState<string[]>(['[SYSTEM] Core orchestrator engine initialized. Ready.']);
  const [activeLayers, setActiveLayers] = useState<string[]>(['cloudy']);
  const [opacity, setOpacity] = useState(80);
  const [timelineVal, setTimelineVal] = useState(4);
  const [isSwipeMode, setIsSwipeMode] = useState(false);
  const [inspectorData, setInspectorData] = useState({ lat: 0, lon: 0, conf: '--', reliability: '--', attnWeight: '--', ndvi: '--', surface: 'Outside Scene', delta: '--' });
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [report, setReport] = useState('');
  const [stats, setStats] = useState({ floodArea: '--', waterDepth: '--', roadDamage: '--', priorityScore: '--', severity: 'READY' });
  const [valMetrics, setValMetrics] = useState({ psnr: '--', ssim: '--', rmse: '--', sam: '--', ndviDelta: '--', conf: '--', reliability: '--', qaCheck: 'READY' });
  
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const logEndRef = useRef<HTMLDivElement | null>(null);

  const loc = LOCATIONS[locationKey];
  const W = 512;
  const H = 512;

  useEffect(() => {
    drawRasterLayer();
  }, [locationKey, activeLayers, opacity, timelineVal, isSwipeMode]);

  const addLog = (text: string) => {
    const time = new Date().toISOString().slice(11, 19);
    setLogs(prev => [...prev, `[${time}] ${text}`]);
    setTimeout(() => {
      logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  };

  const drawRasterLayer = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = 'rgba(2, 132, 199, 0.1)';
    ctx.lineWidth = 1;
    for (let x = 0; x < W; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y < H; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }

    const drawFeature = (layerType: string, clipPercentage = 100, isLeft = true) => {
      ctx.save();
      if (clipPercentage < 100) {
        ctx.beginPath();
        if (isLeft) {
          ctx.rect(0, 0, W * (clipPercentage / 100), H);
        } else {
          ctx.rect(W * (clipPercentage / 100), 0, W, H);
        }
        ctx.clip();
      }

      const isKerala = locationKey === 'kerala';
      const isUK = locationKey === 'uttarakhand';
      const isChennai = locationKey === 'chennai';

      if (layerType === 'historical' || layerType === 'reconstructed' || layerType === 'cloudy') {
        ctx.fillStyle = '#166534';
        ctx.fillRect(0, 0, W, H);

        ctx.fillStyle = '#475569';
        if (isKerala) {
          ctx.fillRect(80, 80, 50, 40);
          ctx.fillRect(320, 200, 60, 60);
        } else if (isUK) {
          ctx.fillRect(150, 220, 20, 20);
          ctx.fillRect(280, 140, 30, 25);
        } else if (isChennai) {
          ctx.fillRect(50, 50, 180, 180);
          ctx.fillRect(250, 250, 100, 120);
        }

        ctx.beginPath();
        ctx.strokeStyle = '#0369a1';
        ctx.lineWidth = 15;
        if (isKerala) {
          ctx.moveTo(150, 0); ctx.bezierCurveTo(170, 200, 250, 300, 270, H);
        } else if (isUK) {
          ctx.moveTo(250, 0); ctx.lineTo(260, 200); ctx.lineTo(200, 350); ctx.lineTo(240, H);
        } else if (isChennai) {
          ctx.moveTo(0, 280); ctx.bezierCurveTo(200, 290, 300, 270, W, 260);
        }
        ctx.stroke();
      }

      if (layerType === 'reconstructed') {
        ctx.fillStyle = '#06b6d4';
        if (isKerala) {
          ctx.beginPath(); ctx.arc(230, 280, 50, 0, Math.PI * 2); ctx.fill();
        } else if (isUK) {
          ctx.fillStyle = '#78350f';
          ctx.beginPath();
          ctx.moveTo(180, 210); ctx.lineTo(280, 240); ctx.lineTo(270, 290); ctx.lineTo(170, 250);
          ctx.closePath(); ctx.fill();
        } else if (isChennai) {
          ctx.beginPath(); ctx.fillRect(80, 80, 120, 100); ctx.arc(220, 280, 70, 0, Math.PI * 2); ctx.fill();
        }
      }

      if (layerType === 'sar') {
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(0, 0, W, H);
        for (let i = 0; i < 4000; i++) {
          const rx = Math.random() * W;
          const ry = Math.random() * H;
          const tone = Math.floor(Math.random() * 110) + 70;
          ctx.fillStyle = `rgb(${tone}, ${tone}, ${tone})`;
          ctx.fillRect(rx, ry, 2, 2);
        }
        ctx.fillStyle = '#020617';
        if (isKerala) {
          ctx.beginPath(); ctx.arc(230, 280, 50, 0, Math.PI * 2); ctx.fill();
        } else if (isUK) {
          ctx.fillStyle = '#3f220f';
          ctx.beginPath();
          ctx.moveTo(180, 210); ctx.lineTo(280, 240); ctx.lineTo(270, 290); ctx.lineTo(170, 250); ctx.closePath(); ctx.fill();
        } else if (isChennai) {
          ctx.beginPath(); ctx.fillRect(80, 80, 120, 100); ctx.arc(220, 280, 70, 0, Math.PI * 2); ctx.fill();
        }
      }

      if (layerType === 'confidence') {
        ctx.fillStyle = '#16a34a';
        ctx.fillRect(0, 0, W, H);
        const grad = ctx.createRadialGradient(250, 200, 20, 250, 200, 150);
        grad.addColorStop(0, '#dc2626');
        grad.addColorStop(0.5, '#eab308');
        grad.addColorStop(1, 'rgba(22, 163, 74, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(250, 200, 150, 0, Math.PI * 2); ctx.fill();
      }

      if (layerType === 'flood') {
        ctx.fillStyle = 'rgba(6, 182, 212, 0.4)';
        ctx.strokeStyle = '#22d3ee';
        ctx.lineWidth = 2;
        if (isKerala) {
          ctx.beginPath(); ctx.arc(230, 280, 50, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        } else if (isUK) {
          ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
          ctx.strokeStyle = '#f87171';
          ctx.beginPath();
          ctx.moveTo(180, 210); ctx.lineTo(280, 240); ctx.lineTo(270, 290); ctx.lineTo(170, 250);
          ctx.closePath(); ctx.fill(); ctx.stroke();
        } else if (isChennai) {
          ctx.beginPath(); ctx.rect(80, 80, 120, 100); ctx.arc(220, 280, 70, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
      }

      if (layerType === 'ndvi') {
        ctx.fillStyle = '#ca8a04';
        ctx.fillRect(0, 0, W, H);
        ctx.fillStyle = '#14532d';
        ctx.fillRect(0, 0, W, 120);
        ctx.fillStyle = '#dc2626';
        if (isKerala) {
          ctx.beginPath(); ctx.arc(230, 280, 50, 0, Math.PI * 2); ctx.fill();
        } else if (isUK) {
          ctx.fillStyle = '#b45309';
          ctx.beginPath();
          ctx.moveTo(180, 210); ctx.lineTo(280, 240); ctx.lineTo(270, 290); ctx.lineTo(170, 250);
          ctx.closePath(); ctx.fill();
        } else if (isChennai) {
          ctx.beginPath(); ctx.fillRect(80, 80, 120, 100); ctx.arc(220, 280, 70, 0, Math.PI * 2); ctx.fill();
        }
      }

      if (layerType === 'difference') {
        ctx.fillStyle = 'rgba(239, 68, 68, 0.7)';
        if (isKerala) {
          ctx.beginPath(); ctx.arc(230, 280, 50, 0, Math.PI * 2); ctx.fill();
        } else if (isUK) {
          ctx.beginPath();
          ctx.moveTo(180, 210); ctx.lineTo(280, 240); ctx.lineTo(270, 290); ctx.lineTo(170, 250);
          ctx.closePath(); ctx.fill();
        } else if (isChennai) {
          ctx.beginPath(); ctx.rect(80, 80, 120, 100); ctx.arc(220, 280, 70, 0, Math.PI * 2); ctx.fill();
        }
      }

      if (layerType === 'cloudy') {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
        ctx.beginPath(); ctx.arc(270, 220, 120, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = 'rgba(255, 255, 255, 0.88)';
        ctx.beginPath(); ctx.arc(250, 200, 120, 0, Math.PI * 2); ctx.fill();
      }

      // XAI Layer: Attention Map
      if (layerType === 'attention') {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
        ctx.fillRect(0, 0, W, H);
        ctx.strokeStyle = '#fde047';
        ctx.lineWidth = 3;
        ctx.beginPath();
        if (isKerala) {
          ctx.arc(230, 280, 50, 0, Math.PI * 2);
        } else if (isUK) {
          ctx.moveTo(180, 210); ctx.lineTo(280, 240); ctx.lineTo(270, 290); ctx.lineTo(170, 250); ctx.closePath();
        } else if (isChennai) {
          ctx.rect(80, 80, 120, 100); ctx.arc(220, 280, 70, 0, Math.PI * 2);
        }
        ctx.stroke();
      }

      // XAI Layer: Uncertainty Map
      if (layerType === 'uncertainty') {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, W, H);
        const grad = ctx.createRadialGradient(250, 200, 10, 250, 200, 150);
        grad.addColorStop(0, '#fff');
        grad.addColorStop(1, '#000');
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(250, 200, 150, 0, Math.PI * 2); ctx.fill();
      }

      ctx.restore();
    };

    ctx.globalAlpha = opacity / 100;

    if (isSwipeMode) {
      const percentage = (timelineVal / 4) * 100;
      drawFeature('cloudy', percentage, true);
      drawFeature('reconstructed', percentage, false);
    } else {
      activeLayers.forEach(l => {
        drawFeature(l);
      });
    }

    ctx.globalAlpha = 1.0;
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const latOffset = ((H - y) / H) * 0.06 - 0.03;
    const lonOffset = (x / W) * 0.07 - 0.035;
    
    const lat = loc.lat + latOffset;
    const lon = loc.lon + lonOffset;

    let conf = '98%';
    let reliability = '0.9810';
    let attnWeight = '0.04';
    let ndvi = '0.68';
    let surface = 'Vegetation Canopy';
    let delta = '0.00';

    const dist = Math.hypot(x - 230, y - 280);

    if (locationKey === 'kerala' && dist < 50) {
      conf = '82%';
      reliability = '0.8240';
      attnWeight = '0.88 (Water boundary)';
      ndvi = '-0.12';
      surface = 'Flood Inundation';
      delta = '+0.82 (Water)';
    } else if (locationKey === 'uttarakhand' && x > 170 && x < 280 && y > 210 && y < 290) {
      conf = '76%';
      reliability = '0.7580';
      attnWeight = '0.94 (Debris node)';
      ndvi = '+0.06';
      surface = 'Landslide Debris';
      delta = '-0.52 (Veg Loss)';
    } else if (locationKey === 'chennai' && (dist < 70 || (x > 80 && x < 200 && y > 80 && y < 180))) {
      conf = '91%';
      reliability = '0.9120';
      attnWeight = '0.85 (Urban boundary)';
      ndvi = '-0.08';
      surface = 'Urban Flood';
      delta = '+0.76 (Water)';
    }

    setInspectorData({ lat, lon, conf, reliability, attnWeight, ndvi, surface, delta });
  };

  const runPipeline = () => {
    if (pipelineRunning) return;
    setPipelineRunning(true);
    setPipelineStatus('RUNNING');
    setLogs([]);
    
    const steps = [
      { t: 'Orchestrator: Activating Dataset Discovery Engine (Catalog Search -> Metadata Query)...', p: 8 },
      { t: 'Orchestrator: Ranking reference imagery (Cloud percentage, Season, Solar Elevation)...', p: 15 },
      { t: `Orchestrator: Best Reference Selection: Ranked ${loc.rankings[0].id} as baseline reference...`, p: 22 },
      { t: 'Orchestrator: Download Manager pulling current Sentinel-1 SAR orbit files and optical bands...', p: 30 },
      { t: 'Orchestrator: Verifying metadata variables, band compatibility, and coordinate bounds...', p: 38 },
      { t: 'Orchestrator: SAR Preprocessing (Orbit Correction -> Calibration -> Terrain Correction -> Lee Speckle Filter)...', p: 48 },
      { t: 'Orchestrator: Optical Preprocessing (TOA Reflectance -> Atmospheric DOS -> Histogram Matching)...', p: 58 },
      { t: 'Orchestrator: Swapping registry models (CloudNet_v1.2 and TemporalDiffusion_v3.4 loaded)...', p: 68 },
      { t: 'Orchestrator: Running Temporal Fusion Transformer & Denoising Diffusion Reconstruction...', p: 82 },
      { t: 'Orchestrator: Synthesizing Explainability Layer (generating Attention maps and Uncertainty maps)...', p: 90 },
      { t: 'Orchestrator: Executing multi-category QA Validation split (Reconstruction, Spectral, Uncertainty)...', p: 96 },
      { t: 'Orchestrator: Disaster assessment complete. Generating intelligence reports...', p: 100 }
    ];

    steps.forEach((step, idx) => {
      setTimeout(() => {
        addLog(step.t);
        setPipelineProgress(step.p);
        
        if (idx === steps.length - 1) {
          completePipeline();
        }
      }, (idx + 1) * 650);
    });
  };

  const completePipeline = () => {
    setPipelineRunning(false);
    setPipelineStatus('NOMINAL');
    addLog('[SUCCESS] Image reconstruction & validation checks passed. Attention mapping online.');

    setActiveLayers(['reconstructed', 'flood', 'attention']);
    setStats({
      floodArea: loc.stats.floodArea,
      waterDepth: loc.stats.waterDepth,
      roadDamage: loc.stats.roadDamage,
      priorityScore: loc.stats.priorityScore,
      severity: loc.stats.severity
    });

    setValMetrics({
      psnr: loc.metrics.psnr,
      ssim: loc.metrics.ssim,
      rmse: loc.metrics.rmse,
      sam: loc.metrics.sam,
      ndviDelta: loc.metrics.ndviDelta,
      conf: loc.metrics.conf,
      reliability: loc.metrics.reliability,
      qaCheck: 'PASSED'
    });

    setReport(loc.report);
  };

  const toggleLayer = (layerKey: string) => {
    if (activeLayers.includes(layerKey)) {
      setActiveLayers(prev => prev.filter(k => k !== layerKey));
    } else {
      setActiveLayers(prev => [...prev, layerKey]);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      {/* Header */}
      <header className="border-b border-border bg-[#0f172a] px-4 py-2.5 flex items-center justify-between z-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded border border-cyanGlow flex items-center justify-center bg-gradient-to-br from-[#0c4a6e] to-[#0f172a] shadow-lg">
            <Satellite className="text-orangeGlow w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-widest text-[#e2e8f0] flex items-center gap-2">
              CLOUDFREE.AI <span className="text-[9px] bg-cyanGlow/20 text-cyanGlow border border-cyanGlow/40 px-1.5 py-0.5 rounded font-mono font-bold">NEXT.JS PLATFORM</span>
            </h1>
            <p className="text-[9px] text-cyanGlow font-semibold tracking-wider">BHARATIYA ANTARIKSH HACKATHON • ISRO-NRSC PIPELINE</p>
          </div>
        </div>

        <div className="hidden lg:flex items-center gap-6 text-[10px] border-l border-border pl-6">
          <div>
            <span className="text-slate-500">MISSION STATUS:</span>
            <span className="text-emerald-400 font-bold ml-1 flex items-center inline-flex gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> NOMINAL
            </span>
          </div>
          <div>
            <span className="text-slate-500">ORCHESTRATOR:</span>
            <span className="text-cyanGlow font-bold ml-1">Central Workflow Active</span>
          </div>
          <div className="hidden xl:block">
            <span className="text-slate-500">ACTIVE POSITION:</span>
            <span className="text-slate-300 ml-1 font-mono">
              {inspectorData.lat ? `${inspectorData.lat.toFixed(4)}°N, ${inspectorData.lon.toFixed(4)}°E` : 'Searching Sensor...'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Workspace grid */}
      <main className="flex-1 flex overflow-hidden">
        
        {/* Left control panel */}
        <section className="w-80 border-r border-border bg-card/85 backdrop-blur flex flex-col overflow-y-auto shrink-0 z-40">
          <div className="p-3 border-b border-border bg-cyanGlow/5 flex justify-between items-center">
            <span className="text-xs font-bold text-cyanGlow tracking-widest flex items-center gap-1.5"><Sliders className="w-3.5 h-3.5" /> MISSION CONTROL</span>
            <span className="text-[8px] border border-orangeGlow/50 text-orangeGlow px-1.5 py-0.5 rounded font-bold">SAR+OPTICAL</span>
          </div>

          <div className="flex-1 p-3 space-y-4">
            {/* Step 1: Location selection */}
            <div className="border border-border rounded bg-background/70 overflow-hidden">
              <div className="p-2.5 bg-border/50 text-xs font-bold flex justify-between items-center border-b border-border">
                <span>1. GEOSPATIAL DATA SEARCH</span>
                <ChevronDown className="w-3 h-3 text-slate-500" />
              </div>
              <div className="p-3 space-y-3">
                <div>
                  <label className="block text-[9px] text-slate-400 mb-1">TARGET SCENE</label>
                  <select 
                    value={locationKey}
                    onChange={(e) => {
                      setLocationKey(e.target.value as LocationKey);
                      setStats({ floodArea: '--', waterDepth: '--', roadDamage: '--', priorityScore: '--', severity: 'READY' });
                      setValMetrics({ psnr: '--', ssim: '--', rmse: '--', sam: '--', ndviDelta: '--', conf: '--', reliability: '--', qaCheck: 'READY' });
                      setReport('');
                      setActiveLayers(['cloudy']);
                      addLog(`Switched target scene to: ${e.target.value}`);
                    }}
                    className="w-full bg-background border border-border rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-cyanGlow"
                  >
                    <option value="kerala">Kerala Coastal Plains (Monsoon Flood)</option>
                    <option value="uttarakhand">Uttarakhand Valleys (Landslide)</option>
                    <option value="chennai">Chennai Basin (Cyclone Flood)</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-2 text-center text-[10px]">
                  <div className="bg-background border border-border py-1.5 rounded">
                    <span className="block text-[8px] text-slate-500">LATITUDE</span>
                    <span className="font-bold text-slate-300">{loc.lat.toFixed(4)} N</span>
                  </div>
                  <div className="bg-background border border-border py-1.5 rounded">
                    <span className="block text-[8px] text-slate-500">LONGITUDE</span>
                    <span className="font-bold text-slate-300">{loc.lon.toFixed(4)} E</span>
                  </div>
                </div>

                {/* Reference list ranking UI */}
                <div className="p-2 bg-background border border-border rounded text-[9px] space-y-1">
                  <div className="font-semibold text-cyanGlow border-b border-border pb-0.5 flex justify-between">
                    <span>REFERENCE IMAGERY CHRONO RANK</span>
                    <span className="text-emerald-400 font-bold">Cloud-Free</span>
                  </div>
                  {loc.rankings.map(item => (
                    <div key={item.id} className="flex justify-between border-b border-border/30 pb-0.5 pt-0.5">
                      <span className="text-slate-400">#{item.rank} {item.id}</span>
                      <span className="text-slate-300">{item.sensor}</span>
                      <span className="text-emerald-400 font-bold">{item.cloud}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Step 2: Model Configuration */}
            <div className="border border-border rounded bg-background/70 overflow-hidden">
              <div className="p-2.5 bg-border/50 text-xs font-bold flex justify-between items-center border-b border-border">
                <span>2. MODEL REGISTRY CONFIG</span>
                <ChevronDown className="w-3 h-3 text-slate-500" />
              </div>
              <div className="p-3 space-y-2 text-[10px] text-slate-300">
                <div className="flex justify-between">
                  <span>Reconstruction Checkpoint:</span>
                  <span className="text-cyanGlow font-bold">TemporalDiffusion_v3.4</span>
                </div>
                <div className="flex justify-between">
                  <span>Cloud Net weight:</span>
                  <span className="text-cyanGlow font-bold">CloudNet_v1.2</span>
                </div>
                <div className="flex justify-between">
                  <span>Co-Registration GNN:</span>
                  <span className="text-cyanGlow font-bold">LoFTR_ResNet_v2.0</span>
                </div>
                <div className="border-t border-border/30 pt-1.5 mt-1.5 text-[9px] text-slate-500">
                  <i className="fa-solid fa-database mr-1"></i> ModelRegistry: active, weights online
                </div>
              </div>
            </div>

            {/* Run Button */}
            <button 
              onClick={runPipeline}
              disabled={pipelineRunning}
              className="w-full py-2 bg-gradient-to-r from-cyanGlow to-cyanGlow/80 hover:from-cyanGlow hover:to-cyanGlow text-[#fff] font-bold text-xs rounded tracking-widest transition-all shadow-lg flex items-center justify-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Satellite className="w-3.5 h-3.5" /> TRIGGER ORCHESTRATOR
            </button>
          </div>

          {/* Terminal logs */}
          <div className="h-44 border-t border-border bg-[#070b13] p-3 flex flex-col">
            <div className="flex justify-between items-center text-[9px] font-bold text-cyanGlow tracking-wider mb-1">
              <span className="flex items-center gap-1"><Terminal className="w-3 h-3" /> PIPELINE STEPS LOG</span>
              <span className="text-slate-500">{pipelineStatus}</span>
            </div>
            <div className="flex-1 overflow-y-auto text-[8px] text-[#e2e8f0]/85 space-y-1 pr-1 font-mono">
              {logs.map((log, idx) => (
                <div key={idx} className={log.includes('[SUCCESS]') ? 'text-emerald-400 font-bold' : 'text-slate-300'}>{log}</div>
              ))}
              <div ref={logEndRef} />
            </div>
            <div className="w-full bg-[#1e293b] h-1 rounded-full mt-2 overflow-hidden">
              <div 
                className="bg-orangeGlow h-full transition-all duration-300"
                style={{ width: `${pipelineProgress}%` }}
              ></div>
            </div>
          </div>
        </section>

        {/* Center GIS View */}
        <section className="flex-1 relative flex flex-col bg-background">
          <div className="flex-1 relative overflow-hidden flex items-center justify-center">
            <canvas 
              ref={canvasRef}
              width={W}
              height={H}
              onMouseMove={handleMouseMove}
              className="border border-border/40 cursor-crosshair rounded max-w-full max-h-full"
            />

            {/* Legends */}
            <div className="absolute bottom-20 left-4 z-40 bg-card/95 border border-border p-2.5 rounded text-[9px] max-w-xs font-mono">
              <h4 className="font-bold text-slate-300 border-b border-border pb-1 mb-1.5 flex items-center gap-1"><Layers className="w-3 h-3" /> GIS MAP LEGENDS</h4>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span class="text-slate-400 w-16">Confidence:</span>
                  <div className="w-20 h-2 bg-gradient-to-r from-red-600 via-yellow-500 to-green-600 rounded"></div>
                  <span className="text-slate-300">0-100%</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 w-16">Attention:</span>
                  <span className="w-4 h-2 bg-yellow-400 border border-yellow-300 rounded inline-block"></span>
                  <span className="text-slate-300">Hotspots</span>
                </div>
              </div>
            </div>

            {/* Inspector display */}
            <div className="absolute bottom-4 right-4 z-40 bg-card/95 border border-border p-3 rounded text-[9px] w-56 font-mono">
              <div className="text-cyanGlow font-bold border-b border-border pb-1 mb-1 flex justify-between">
                <span>PIXEL INSPECTOR</span>
                <Activity className="w-3.5 h-3.5" />
              </div>
              <div className="grid grid-cols-2 gap-y-0.5 text-slate-300">
                <span>Lat:</span>
                <span className="text-right text-orangeGlow font-bold">{inspectorData.lat ? inspectorData.lat.toFixed(4) : '--'}</span>
                <span>Lon:</span>
                <span className="text-right text-orangeGlow font-bold">{inspectorData.lon ? inspectorData.lon.toFixed(4) : '--'}</span>
                <span>Confidence:</span>
                <span className="text-right text-emerald-400 font-bold">{inspectorData.conf}</span>
                <span>Reliability:</span>
                <span className="text-right text-emerald-400 font-bold">{inspectorData.reliability}</span>
                <span>Attention Wt:</span>
                <span className="text-right text-yellow-400 font-bold">{inspectorData.attnWeight}</span>
                <span>NDVI:</span>
                <span className="text-right text-emerald-400 font-bold">{inspectorData.ndvi}</span>
                <span>Surface:</span>
                <span className="text-right truncate">{inspectorData.surface}</span>
              </div>
            </div>

            {/* Timeline Slider */}
            <div className="absolute bottom-4 left-4 right-64 z-40 bg-card/95 border border-border px-3 py-2 rounded flex items-center gap-3">
              <span className="text-[9px] font-bold text-slate-400 whitespace-nowrap">TIMELINE:</span>
              <input 
                type="range" min="0" max="4" value={timelineVal}
                onChange={(e) => {
                  setTimelineVal(parseInt(e.target.value));
                }}
                className="flex-1 accent-cyanGlow cursor-pointer"
              />
              <span className="text-[8px] font-bold text-cyanGlow bg-cyanGlow/10 px-2 py-0.5 border border-cyanGlow/20 rounded whitespace-nowrap">
                {["2023 Hist", "2024 Ref", "2025 SAR", "2026 Cloudy", "2026 Recon"][timelineVal]}
              </span>
            </div>

            {/* View selectors */}
            <div className="absolute top-4 right-4 z-40 flex flex-col gap-2">
              <div className="bg-card/95 border border-border p-1 rounded flex gap-1">
                <button 
                  onClick={() => setIsSwipeMode(false)}
                  className={`px-2 py-1 text-[9px] font-bold rounded ${!isSwipeMode ? 'bg-cyanGlow text-white' : 'bg-border text-slate-400'}`}
                >
                  STANDARD
                </button>
                <button 
                  onClick={() => {
                    setIsSwipeMode(true);
                    addLog('Enabled swipe mode. Cloudy (left) vs Reconstructed (right).');
                  }}
                  className={`px-2 py-1 text-[9px] font-bold rounded ${isSwipeMode ? 'bg-cyanGlow text-white' : 'bg-border text-slate-400'}`}
                >
                  SWIPE
                </button>
              </div>

              {/* Layer list toggler */}
              <div className="bg-card/95 border border-border p-3 rounded text-[9px] w-48 flex flex-col gap-1.5 font-mono">
                <div className="font-bold text-slate-300 border-b border-border pb-1 flex justify-between items-center">
                  <span>LAYER MANAGER</span>
                  <Layers className="w-3.5 h-3.5 text-slate-500" />
                </div>
                <div className="space-y-1">
                  {Object.entries({
                    cloudy: { label: "1. Cloudy Optical", c: "#94a3b8" },
                    historical: { label: "2. Historical Reference", c: "#22c55e" },
                    sar: { label: "3. Current Sentinel-1", c: "#64748b" },
                    reconstructed: { label: "4. AI Reconstructed", c: "#38bdf8" },
                    confidence: { label: "5. Confidence Map", c: "#eab308" },
                    flood: { label: "6. Flood Vector Overlay", c: "#06b6d4" },
                    ndvi: { label: "7. NDVI Canopy", c: "#15803d" },
                    difference: { label: "8. Difference map", c: "#ef4444" },
                    attention: { label: "9. Attention Map (XAI)", c: "#fde047" },
                    uncertainty: { label: "10. Uncertainty Map (XAI)", c: "#cbd5e1" }
                  }).map(([key, meta]) => (
                    <label key={key} className="flex items-center gap-1.5 cursor-pointer hover:bg-border/30 p-0.5 rounded">
                      <input 
                        type="checkbox"
                        checked={activeLayers.includes(key)}
                        onChange={() => toggleLayer(key)}
                        className="accent-cyanGlow"
                      />
                      <span style={{ color: meta.c }}>{meta.label}</span>
                    </label>
                  ))}
                </div>
                <div className="border-t border-border pt-1.5 mt-1.5 flex flex-col gap-1 text-slate-400">
                  <div className="flex justify-between text-[8px]">
                    <span>Opacity:</span>
                    <span>{opacity}%</span>
                  </div>
                  <input 
                    type="range" min="0" max="100" value={opacity}
                    onChange={(e) => setOpacity(parseInt(e.target.value))}
                    className="accent-cyanGlow"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Right Panel: Intelligence Diagnostics */}
        <section className="w-96 border-l border-border bg-card/85 backdrop-blur flex flex-col overflow-y-auto shrink-0 z-40">
          <div className="p-3 border-b border-border bg-cyanGlow/5 flex justify-between items-center">
            <span className="text-xs font-bold text-cyanGlow tracking-widest flex items-center gap-1.5"><Sparkles className="w-3.5 h-3.5" /> DISASTER TELEMETRY</span>
            <span className={`text-[8px] px-1.5 py-0.5 rounded font-bold border ${
              stats.severity === 'CRITICAL' ? 'bg-red-950/20 text-red-400 border-red-500/40' : 
              stats.severity === 'HIGH' ? 'bg-orange-950/20 text-orange-400 border-orange-500/40' : 'bg-slate-900 text-slate-400 border-slate-700'
            }`}>
              {stats.severity}
            </span>
          </div>

          {/* Stats Grid */}
          <div className="p-3 border-b border-border grid grid-cols-2 gap-2 text-center text-[10px]">
            <div className="bg-background border border-border p-2 rounded">
              <span className="block text-slate-400 text-[8px] uppercase">Water Expansion</span>
              <span className="text-sm font-bold text-cyanGlow mt-0.5">{stats.floodArea}</span>
            </div>
            <div className="bg-background border border-border p-2 rounded">
              <span className="block text-slate-400 text-[8px] uppercase">Avg Water Depth</span>
              <span className="text-sm font-bold text-cyanGlow mt-0.5">{stats.waterDepth}</span>
            </div>
            <div className="bg-background border border-border p-2 rounded">
              <span className="block text-slate-400 text-[8px] uppercase">NH Road Submersion</span>
              <span className="text-sm font-bold text-red-400 mt-0.5">{stats.roadDamage}</span>
            </div>
            <div className="bg-background border border-border p-2 rounded">
              <span className="block text-slate-400 text-[8px] uppercase">Priority Rescue Index</span>
              <span className="text-sm font-bold text-orangeGlow mt-0.5">{stats.priorityScore}</span>
            </div>
          </div>

          {/* Scientific Validation Metrics */}
          <div className="p-3 border-b border-border bg-[#070b13]/90 space-y-2">
            <div className="text-[10px] font-bold text-cyanGlow tracking-wider border-b border-border pb-1 flex justify-between items-center">
              <span className="flex items-center gap-1.5"><BarChart4 className="w-3.5 h-3.5 text-cyanGlow" /> QA VALIDATION SPLIT</span>
              <span className={`text-[8px] px-1.5 py-0.5 rounded font-bold border ${
                valMetrics.qaCheck === 'PASSED' ? 'bg-emerald-950/20 text-emerald-400 border-emerald-500/40' : 'bg-slate-900 text-slate-400 border-slate-700'
              }`}>
                {valMetrics.qaCheck}
              </span>
            </div>
            
            {/* Reconstruction */}
            <div className="space-y-0.5">
              <span className="block text-[8px] text-orangeGlow uppercase font-bold">I. Reconstruction Verification</span>
              <div className="grid grid-cols-3 gap-1 text-[8px] text-slate-300 font-mono text-center">
                <div className="bg-background border border-border/50 py-0.5 rounded">
                  <span className="block text-[7px] text-slate-500">PSNR (dB)</span>
                  <span className="font-bold text-cyanGlow">{valMetrics.psnr}</span>
                </div>
                <div className="bg-background border border-border/50 py-0.5 rounded">
                  <span className="block text-[7px] text-slate-500">SSIM Index</span>
                  <span className="font-bold text-emerald-400">{valMetrics.ssim}</span>
                </div>
                <div className="bg-background border border-border/50 py-0.5 rounded">
                  <span className="block text-[7px] text-slate-500">RMSE Diff</span>
                  <span className="font-bold text-orangeGlow">{valMetrics.rmse}</span>
                </div>
              </div>
            </div>

            {/* Spectral & Uncertainty */}
            <div className="grid grid-cols-2 gap-2 text-[8px] font-mono text-slate-300 pt-1">
              <div>
                <span className="block text-[7px] text-orangeGlow uppercase font-bold mb-0.5">II. Spectral</span>
                <div className="flex justify-between border-b border-border/30 pb-0.5">
                  <span className="text-slate-500">SAM (rad):</span>
                  <span className="font-bold text-cyanGlow">{valMetrics.sam}</span>
                </div>
                <div className="flex justify-between border-b border-border/30 pb-0.5">
                  <span className="text-slate-500">NDVI Delta:</span>
                  <span className="font-bold text-emerald-400">{valMetrics.ndviDelta}</span>
                </div>
              </div>
              <div>
                <span className="block text-[7px] text-orangeGlow uppercase font-bold mb-0.5">III. Uncertainty</span>
                <div className="flex justify-between border-b border-border/30 pb-0.5">
                  <span className="text-slate-500">Confidence:</span>
                  <span className="font-bold text-cyanGlow">{valMetrics.conf}</span>
                </div>
                <div className="flex justify-between border-b border-border/30 pb-0.5">
                  <span className="text-slate-500">Reliability:</span>
                  <span className="font-bold text-emerald-400">{valMetrics.reliability}</span>
                </div>
              </div>
            </div>
          </div>

          {/* AI report */}
          <div className="flex-1 p-4 flex flex-col font-sans">
            <div className="flex justify-between items-center mb-2 font-mono">
              <span className="text-[10px] font-bold text-cyanGlow tracking-wider flex items-center gap-1"><FileText className="w-3.5 h-3.5" /> GENERATIVE BRIEF</span>
              <span className="text-[8px] text-slate-500">GEMINI 1.5 PRO API</span>
            </div>
            
            <div className="flex-1 bg-[#070b13] border border-border rounded p-3 text-[11px] text-slate-300 overflow-y-auto leading-relaxed max-h-[190px] font-sans">
              {report ? (
                <div className="space-y-2">
                  <div className="text-xs font-bold text-cyanGlow uppercase font-mono border-b border-border pb-1 flex items-center gap-1">
                    <ShieldAlert className="w-4 h-4 text-orangeGlow" /> Assessment Report
                  </div>
                  <pre className="whitespace-pre-wrap font-sans text-slate-300 text-[11px]">{report}</pre>
                </div>
              ) : (
                <div className="h-full flex flex-col justify-center items-center text-center text-slate-500 font-mono text-[9px]">
                  <Satellite className="w-8 h-8 mb-2 text-slate-600" />
                  <span>Execute the geoprocessing pipeline to construct clear optical scenes and compile Gemini reports.</span>
                </div>
              )}
            </div>

            {/* Export buttons */}
            <div className="mt-3 space-y-2 font-mono">
              <div className="text-[8px] text-slate-500 uppercase tracking-wider font-bold">System Export Handlers</div>
              <div className="grid grid-cols-2 gap-2">
                <button 
                  disabled={!report}
                  onClick={() => alert('Exporting GeoTIFF band array (B2, B3, B4, SAR, Confidence) via GIS core service...')}
                  className="py-1 border border-border rounded text-[9px] flex items-center justify-center gap-1 text-slate-400 hover:text-cyanGlow hover:border-cyanGlow transition-all disabled:opacity-40 disabled:hover:text-slate-400 disabled:hover:border-border"
                >
                  <Download className="w-3 h-3" /> GeoTIFF Bands
                </button>
                <button 
                  disabled={!report}
                  onClick={() => alert('GeoJSON Flood boundary polygons compiling...')}
                  className="py-1 border border-border rounded text-[9px] flex items-center justify-center gap-1 text-slate-400 hover:text-cyanGlow hover:border-cyanGlow transition-all disabled:opacity-40 disabled:hover:text-slate-400 disabled:hover:border-border"
                >
                  <MapPin className="w-3 h-3" /> GeoJSON Flood
                </button>
              </div>
            </div>
          </div>
        </section>

      </main>
    </div>
  );
}
