# 🤖 UIDE Forense AI 3.0+ - Documentación para Agentes IA

> **Para:** Agentes IA (Claude, Jules, Gemini, etc.)
> **Versión:** 3.3 (Flask + React Migration + Anti-False-Positive Calibration)
> **Fecha:** Febrero 2026

---

## 📋 Resumen del Sistema

Sistema de análisis forense digital avanzado con arquitectura modular **Clean Architecture**. Se ha migrado de una aplicación monolítica Gradio a una arquitectura moderna **Frontend-Backend**.

Implementa un enfoque híbrido combinando análisis geométrico, clasificadores visuales y **razonamiento semántico profundo** mediante **DeepSeek-R1**.

### Módulos Principales
1.  **Image Forensics**:
    *   **multiLID**: Análisis de Dimensión Intrínseca Local (geométrico).
    *   **UFD**: Universal Fake Detect (clasificador visual en espacio CLIP).
    *   **Semantic Expert**: Análisis de plausibilidad con **DeepSeek-R1** (razonamiento) y CLIP (embeddings).
2.  **Video Forensics**: XceptionNet (análisis frame a frame).
3.  **Audio Forensics**: Wav2Vec2 / MelodyMachine.

---

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura cliente-servidor desacoplada.

```
[React Frontend :5173]
        ↓ (HTTPS/WSS via Nginx)
[Flask Backend :5000]
        ↓
[ForensicsPipeline]
  ├─ 1. Feature Extractor (CLIP ViT-L/14)
  │      └─ calculate_probabilities() (Cosine Similarity)
  │
  ├─ 2. Experts Layer
  │    ├─ MultiLID Expert (Geometry)
  │    ├─ UFD Expert (Visual Artifacts)
  │    └─ Semantic Expert (Reasoning)
  │         └─ DeepSeekClient (Simple) -> [Ollama :11434]
  │
  └─ 3. Fusion Engine V3.3 (User Calibrated)
```

### Backend (Flask + Gunicorn)
*   **Path**: `backend/`
*   **Entry Point**: `app.py` (Factory Pattern)
*   **API**: RESTful, con Blueprints modulares (`routes/`).
*   **LLM**: Integración directa con **Ollama** para DeepSeek-R1 usando un cliente ligero (`requests`).

### Frontend (React + Vite)
*   **Path**: `frontend/`
*   **Tech Stack**: React 18, Vite, CSS Modules (Dark Theme).
*   **UI/UX**: Interfaz profesional "ForensicAI" con Sidebar, Navbar y visualización de evidencias.

---

## 🧠 Semantic Expert (DeepSeek-R1)

Detecta imágenes **visualmente perfectas pero semánticamente imposibles**.

1.  **Modo DeepSeek-R1 (Reasoning)**:
    *   Cliente: `services/deepseek_client.py` (Clase `DeepSeekClient`).
    *   **Implementación Simplificada**: 
        *   Usa `requests` estándar para máxima compatibilidad.
        *   Construcción de prompts y parsing JSON ocurre dentro del experto (`modules/image_forensics/semantic_expert.py`).
    *   **Métricas**:
        *   `semantic_improbability_score`: ¿Es la escena plausible?
        *   `context_collision_score`: ¿Hay elementos anacrónicos?
        *   `composition_synthetic_score`: ¿Simetría/perfección artificial?

2.  **Modo CLIP (Fallback)**:
    *   Usa `calculate_probabilities` en `CLIPFeatureExtractor` para comparar embeddings imagen-texto si DeepSeek no está disponible.

---

## ⚗️ Fusion Engine V3.3 (User Calibrated)

Motor de decisión calibrado para reducir falsos positivos en imágenes naturales (Anti-False-Positive).

### 1. Pesos Ajustados
Se da más peso a la evidencia geométrica y menos a la semántica para evitar sesgos de "perfección".

| Experto | Peso V3.3 | Rationale |
| :--- | :--- | :--- |
| **multiLID** | **0.35** | Dimensionalidad es clave para fotos naturales. |
| **UFD** | **0.25** | Clasificador visual (reducido por sensibilidad). |
| **Semantic** | **0.40** | Razonamiento LLM (controlado por umbrales). |

### 2. Bloqueos Hard (Thresholds)
Reglas estrictas que anulan el promedio ponderado.

*   **IA Confirmada**: Si `Semantic > 0.65`. (Antes 0.50, subido para evitar falsos positivos).
*   **Real Confirmada**: Si `Semantic < 0.45` Y `UFD < 0.50`.

### 3. Evidencia Robusta
Cálculo diferencial para determinar la inclinación real vs. fake.

*   **Evidencia IA**: `max(0, Semantic - 0.50) + max(0, UFD - 0.50)`
*   **Evidencia Real**: `max(0, 0.50 - Semantic) + max(0, 0.50 - UFD)`
*   **Boost Real**: Si `multiLID < 0.25`, se suma **+0.20** a la evidencia Real (Bokeh/Desenfoque natural).

---

## 📁 Estructura del Proyecto

Actualizada tras la migración y refactorización:

```
ProyectoForenseUIDE/
├── backend/                  # Flask API
│   ├── app.py               # App Factory
│   ├── routes/              # API Endpoints
│   │   ├── analyze.py       # Lógica principal
│   │   └── semantic.py      # Debug/Test routes
│   ├── services/            # Business Logic
│   │   ├── forensics_pipeline.py  # Orchestrator (Updated Import)
│   │   ├── deepseek_client.py     # Simple Client (Requests)
│   │   └── __init__.py            # Export DeepSeekClient
│   └── wsgi.py              # Gunicorn Entry Point
│
├── frontend/                 # React App
│   ├── src/
│   │   ├── components/      # UI Components
│   │   ├── services/        # API Consumer
│   │   └── App.jsx          # Main Layout
│   └── ...
│
├── modules/                  # Core AI Modules
│   ├── image_forensics/
│   │   ├── fusion_engine.py      # V3.3 Logic here
│   │   ├── semantic_expert.py    # Revised Prompting/Parsing
│   │   ├── feature_extractor.py  # Added calculate_probabilities
│   │   └── ...
│   └── ...
```

---

## 🔧 Configuración (`.env`)

```env
# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=...

# DeepSeek / Ollama
DEEPSEEK_ENABLED=true
DEEPSEEK_API_URL=http://localhost:11434/api/generate
DEEPSEEK_MODEL=deepseek-r1:7b

# CORS
CORS_ORIGINS=http://localhost:5173,https://midominio.com
```

---

## 🎓 Contexto del Proyecto
*   **Organización**: UIDE (Universidad Internacional del Ecuador).
*   **Objetivo**: Detección de contenido sintético con enfoque forense/legal.
*   **Estado Actual**: Calibración V3.3 completada. Falsos positivos minimizados. Sistema listo para demo.
