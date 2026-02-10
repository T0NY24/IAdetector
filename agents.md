# 🤖 UIDE Forense AI 15.0 - Documentación para Agentes IA

> **Para:** Agentes IA (Claude, Jules, Gemini, etc.)
> **Versión:** 15.0 (Trinity Judgment: Full React + Flask Migration)
> **Fecha:** Febrero 2026

---

## 📋 Resumen del Sistema

Sistema de análisis forense digital avanzado con arquitectura modular **Clean Architecture**. Completamente migrado de Gradio a una arquitectura moderna **React + Flask** con soporte para:

- ✅ **Imágenes** (multiLID + UFD + Semantic Expert con DeepSeek-R1)
- ✅ **Videos** (XceptionNet - Deepfake facial detection)  
- ✅ **Audio** (HuggingFace AST - Synthetic voice detection)

### Módulos Principales
1. **Image Forensics (V12.0 Trinity Judgment)**:
   - **Peritos (Expert Collectors)**:
     - **multiLID**: Análisis de Dimensión Intrínseca Local (geometría).
     - **UFD**: Universal Fake Detect (clasificador visual en espacio CLIP).
     - **FFT**: Frequency analysis (detección de patrones frecuenciales).
   - **Doctor (Judge)**: **DeepSeek-R1** lee números técnicos + descripción BLIP → score.
   - **Sentencia (Verdict)**: Fusion Engine V10.0 (decisión binaria: threshold 0.60).
2. **Video Forensics**: XceptionNet (análisis frame a frame de rostros).
3. **Audio Forensics**: HuggingFace AST (detección de ElevenLabs, RVC, TTS).

---

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura cliente-servidor completamente desacoplada.

```
[React Frontend :5173]
        ↓ (HTTP REST API)
[Flask Backend :5000]
  │
  ├─── /api/analyze_image  → ForensicsPipeline (Image)
  │     ├─ 1. CLIP Feature Extractor (ViT-L/14)
  │     │    └─ Image embeddings + Text probabilities
  │     ├─ 2. Expert Analysis
  │     │    ├─ multiLID: Local geometry (0-1 score)
  │     │    ├─ UFD: Visual artifacts (0-1 score)
  │     │    └─ Semantic: DeepSeek-R1 reasoning (0-1 score)
  │     └─ 3. Fusion Engine V3.3
  │          └─ Weighted combination + Hard thresholds
  │
  ├─── /api/analyze_video  → VideoForensicsDetector
  │     └─ 1. Frame Extraction (OpenCV)
  │     └─ 2. Face Detection (Haar Cascade)
  │     └─ 3. XceptionNet Classification
  │
  └─── /api/analyze_audio  → AudioForensicsDetector
        └─ 1. Audio Loading (librosa)
        └─ 2. Spectral Analysis
        └─ 3. HuggingFace AST Model
```

### Backend (Flask)
- **Path**: `backend/`
- **Entry Point**: `app.py` (Factory Pattern)
- **API**: RESTful con Blueprints modulares (`routes/`)
  - `analyze.py`: Image analysis → `/api/analyze_image`
  - `analyze_video.py`: Video analysis → `/api/analyze_video`
  - `analyze_audio.py`: Audio analysis → `/api/analyze_audio`
  - `semantic.py`: DeepSeek debugging routes
  - `fusion.py`: Fusion Engine testing routes
- **Core Modules**: `modules/` (image_forensics, video_forensics, audio_forensics)
- **Services**: `forensics_pipeline.py` (orquestrador de imagen), `deepseek_client.py` (LLM)

### Frontend (React + Vite)
- **Path**: `frontend/`
- **Tech Stack**: React 18, Vite, CSS Modules (Dark Theme)
- **Components**:
  - Upload: `UploadImage.jsx`, `UploadVideo.jsx`, `UploadAudio.jsx` (drag-and-drop)
  - Results: `ResultCard.jsx`, `VideoResultCard.jsx`, `AudioResultCard.jsx`
  - UI: `AnalysisProgress.jsx`, `DeepSeekChat.jsx`, `ResultsPanel.jsx`
- **Services**: `api.js` (analyzeImage, analyzeVideo, analyzeAudio)
- **State Management**: React hooks en `App.jsx` (sin Redux)

---

## 📁 Estructura del Proyecto

```
ProyectoForenseUIDE/
├── backend/                  # Flask API
│   ├── app.py               # App Factory (Registered all blueprints)
│   ├── routes/              # API Endpoints
│   │   ├── analyze.py       # Image analysis
│   │   ├── analyze_video.py # Video analysis [NEW 3.4]
│   │   ├── analyze_audio.py # Audio analysis [NEW 3.4]
│   │   └── semantic.py      # Debug/Test routes
│   ├── services/            # Business Logic
│   │   ├── forensics_pipeline.py  # Image orchestrator
│   │   └── deepseek_client.py     # LLM client
│   └── uploads/             # Temporary file storage
│
├── frontend/                # React App
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadImage.jsx      # Image upload
│   │   │   ├── UploadVideo.jsx      # Video upload [NEW 3.4]
│   │   │   ├── UploadAudio.jsx      # Audio upload [NEW 3.4]
│   │   │   ├── ResultCard.jsx       # Image results
│   │   │   ├── VideoResultCard.jsx  # Video results [NEW 3.4]
│   │   │   ├── AudioResultCard.jsx  # Audio results [NEW 3.4]
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.js       # API client (analyzeImage/Video/Audio)
│   │   └── App.jsx          # Main layout (tabs: image/video/audio)
│   └── ...
│
├── modules/                 # Core AI Modules
│   ├── image_forensics/
│   │   ├── fusion_engine.py       # V3.3 calibrated weights
│   │   ├── semantic_expert.py     # DeepSeek-R1 integration
│   │   ├── feature_extractor.py   # CLIP embeddings
│   │   └── ...
│   ├── video_forensics.py   # XceptionNet detector [REFACTORED]
│   └── audio_forensics.py   # HuggingFace AST detector
│
├── config.py                # Centralized configuration
│   ├── Video: MAX_VIDEO_SIZE_MB, VIDEO_THRESHOLD, etc.
│   └── Audio: AUDIO_SAMPLE_RATE, MODEL_AUDIO_NAME, etc.
│
└── app.py                   # [LEGACY] Old Gradio app (deprecated)
```

---

## ⚙️ Configuración (config.py + .env)

### Video Settings
```python
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv'}
MAX_VIDEO_SIZE_MB = 100
MAX_VIDEO_DURATION_SECONDS = 120
VIDEO_FRAME_STRIDE = 30  # Analyze 1 frame every 30
MIN_FACES_REQUIRED = 5
VIDEO_THRESHOLD = 50.0   # Deepfake probability threshold
```

### Audio Settings
```python
SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
MAX_AUDIO_SIZE_MB = 20
AUDIO_SAMPLE_RATE = 16000
AUDIO_MAX_DURATION = 60
MODEL_AUDIO_NAME = "MIT/ast-finetuned-audioset-10-10-0.4593"
```

### Environment Variables (.env)
```env
# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=...

# DeepSeek / Ollama (for image semantic analysis)
DEEPSEEK_ENABLED=true
DEEPSEEK_API_URL=http://localhost:11434/api/generate
DEEPSEEK_MODEL=deepseek-r1:7b

# CORS
CORS_ORIGINS=http://localhost:5173,https://midominio.com
```

---

## 🖼️ Image Forensics Module (V12.0 Trinity Judgment)

**Files**: `modules/image_forensics/` directory, `backend/services/forensics_pipeline.py`

### Architecture - Trinity Judgment System

El análisis de imágenes usa un **sistema de juicio en 4 etapas**:

**STAGE 1: PERITOS (Expert Collectors)** - Recolectan números técnicos:
1. **multiLID** (`multilid_expert.py`): Geometría - Dimensión Intrínseca Local (0-1)
2. **UFD** (`ufd_expert.py`): Ruido visual - Artefactos en espacio CLIP (0-1)
3. **FFT** (`fft_expert.py`): Frecuencia - Análisis FFT de patrones (0-1)

**STAGE 2: VISION** - Descripción de imagen:
- **BLIP** (Salesforce): Genera descripción textual de la imagen

**STAGE 3: DOCTOR (DeepSeek Judge)** - Razonamiento contextual:
- **Semantic Expert** (`semantic_expert.py`) + **DeepSeek-R1**:
  - Lee números técnicos (MultiLID, UFD, FFT)
  - Lee descripción de imagen (BLIP)
  - Razona sobre plausibilidad semántica
  - Retorna score 0-1

**STAGE 4: SENTENCIA (Binary Verdict)** - Decisión final:
- **Fusion Engine V10.0** (`fusion_engine.py`):
  - Threshold binario: `> 0.60 = IA`, `≤ 0.60 = REAL`
  - Genera veredicto final y evidencias

### API Contract

**Endpoint**: `POST /api/analyze_image`

**Input**: `FormData` with `image` file
- Supported formats: PNG, JPG, JPEG, WEBP, BMP
- Max size: 10MB (configurable en `config.py`)

**Query Parameters** (opcional):
- `use_deepseek=true|false`: Habilitar/deshabilitar análisis semántico con LLM

**Output**:
```json
{
  "status": "success",
  "result": {
    "verdict": "GENERADA POR IA",
    "confidence": "ALTA",
    "overall_synthetic_score": 0.78,
    "experts": {
      "multilid": {
        "score": 0.23,
        "interpretation": "Geometría consistente con IA generativa"
      },
      "ufd": {
        "score": 0.67,
        "interpretation": "Artefactos visuales detectados"
      },
      "semantic": {
        "score": 0.85,
        "improbability": 0.72,
        "collision": 0.45,
        "composition": 0.68,
        "reasoning": "Simetría perfecta antinatural...",
        "enabled": true
      }
    },
    "fusion": {
      "weighted_score": 0.78,
      "weights": {"multilid": 0.35, "ufd": 0.25, "semantic": 0.40},
      "evidence_ia": 0.52,
      "evidence_real": 0.08,
      "decision_path": "HARD_THRESHOLD_SEMANTIC"
    },
    "clip_probabilities": {
      "ai_generated": 0.82,
      "real_photo": 0.18
    }
  },
  "processing_time": 3.2,
  "deepseek_enabled": true
}
```

**Error Response**:
```json
{
  "error": "File type not allowed. Supported: png, jpg, jpeg, webp, bmp",
  "status": "error"
}
```

### Key Features (V12.0)

- ✅ **Trinity Judgment System**: Peritos (3 expertos) + Vision (BLIP) + Doctor (DeepSeek) + Sentencia (Fusion)
- ✅ **Binary Decision**: Threshold 0.60 para veredicto definitivo (IA o REAL)
- ✅ **Data-Driven DeepSeek**: LLM lee números técnicos + contexto visual
- ✅ **FFT Integration**: Análisis frecuencial además de geometría y ruido
- ✅ **BLIP Vision**: Descripción automática de imagen para contexto semántico

---

## 🎥 Video Forensics Module


**File**: `modules/video_forensics.py`

### Key Changes in 3.4
- ❌ Removed: Gradio dependencies (`gr.Progress`, generator pattern with `yield`)
- ✅ Added: Direct dictionary return for REST API compatibility
- ✅ Kept: XceptionNet model, face detection, Top-K frame selection

### API Contract
**Endpoint**: `POST /api/analyze_video`
**Input**: `FormData` with `video` file
**Output**:
```json
{
  "status": "success",
  "result": {
    "is_deepfake": true,
    "probability": 67.8,
    "verdict": "DEEPFAKE",
    "frames_total": 120,
    "frames_analyzed": 45,
    "duration": 4.0,
    "max_probability": 89.2,
    "predictions": [[0, 45.2], [30, 67.8], ...]
  },
  "processing_time": 12.3
}
```

---

## 🔊 Audio Forensics Module

**File**: `modules/audio_forensics.py`

### Key Features
- Already compatible with REST API (no Gradio dependencies)
- Uses HuggingFace `transformers` library
- Detects ElevenLabs, RVC, TTS, and other synthetic voices

### API Contract
**Endpoint**: `POST /api/analyze_audio`
**Input**: `FormData` with `audio` file
**Output**:
```json
{
  "status": "success",
  "result": {
    "verdict": "AUDIO SINTÉTICO",
    "score": 78.5,
    "confidence": 92.1,
    "duration_analyzed": 3.5,
    "sample_rate": 16000,
    "top_classes": [
      {"label": "Speech synthesizer", "score": 0.785},
      {"label": "Human voice", "score": 0.215}
    ]
  },
  "processing_time": 4.2
}
```

---

## 🧠 Semantic Expert (DeepSeek-R1) - Doctor Stage in V12.0

**File**: `modules/image_forensics/semantic_expert.py`
**Client**: `backend/services/deepseek_client.py`

En V12.0, el Semantic Expert actúa como **"Doctor" (Juez)**:
- **Input**: Números técnicos (MultiLID, UFD, FFT) + Descripción BLIP
- **Process**: DeepSeek-R1 razona sobre plausibilidad (contexto semántico + números)
- **Output**: Score único 0-1 que alimenta al Fusion Engine

**Workflow**:
1. Recibe context dict: `{"multilid": 0.23, "ufd": 0.67, "fft": 0.45}`
2. Recibe descripción: `"a photo of a person holding a cat"`
3. DeepSeek analiza: ¿Es plausible? ¿Los números coinciden con descripción?
4. Retorna: `score 0-1` (1 = muy sintético, 0 = muy real)

---

## ⚗️ Fusion Engine V10.0 - Sentencia (Binary Logic)

**File**: `modules/image_forensics/fusion_engine.py`

Sistema de decisión binaria simple:

```python
# V10.0 Binary Decision
if semantic_score > 0.60:
    verdict = "GENERADA POR IA"
else:
    verdict = "REAL"
```

**Lógica**:
- **Threshold**: 0.60 (binario, sin zonas grises)
- **Input**: Solo semantic_score (DeepSeek ya consideró MultiLID, UFD, FFT)
- **Output**: Veredicto definitivo + evidencias

**Rationale**: DeepSeek ya fusionó toda la información técnica en su razonamiento, el Fusion Engine solo aplica threshold binario para veredicto final.

---

## 🚀 Deployment

### Development
```bash
# Backend
cd backend
python app.py  # http://localhost:5000

# Frontend
cd frontend
npm run dev    # http://localhost:5173
```

### Production
```bash
# Backend (Gunicorn)
gunicorn -c backend/gunicorn_config.py backend.wsgi:app

# Frontend (Build)
cd frontend && npm run build
# Serve dist/ with Nginx or similar
```

---

## 📊 Migration Status (V15.0)

| Feature | Status | Notes |
| :--- | :--- | :--- |
| Image Analysis (V12.0 Trinity) | ✅ Complete | Peritos + Vision + Doctor + Sentencia |
| Video Deepfake Detection | ✅ Complete | XceptionNet, refactored for REST API |
| Audio Synthetic Detection | ✅ Complete | HuggingFace AST |
| React + Flask Architecture | ✅ Complete | Clean separation, modular routes |
| Gradio Legacy App | ⚠️ Deprecated | `app.py` in root (not used) |
| DeepSeek-R1 Integration | ✅ Active | Doctor stage in Trinity Judgment |
| FFT Expert | ✅ Active | Frequency analysis (Perito #3) |
| BLIP Vision | ✅ Active | Image description (Vision stage) |
| Fusion Engine V10.0 | ✅ Active | Binary logic (Sentencia stage) |

---

## 🎓 Contexto del Proyecto
- **Organización**: UIDE (Universidad Internacional del Ecuador).
- **Objetivo**: Detección de contenido sintético con enfoque forense/legal.
- **Estado Actual**: Versión 15.0 completa. Trinity Judgment System (V12.0) con Fusion Engine V10.0, más video y audio migrados a React + Flask.
