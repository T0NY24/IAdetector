# 🤖 UIDE Forense AI 2.0 - Documentación para Agentes IA

> **Para:** Agentes IA (Claude, Jules, etc.)  
> **Versión:** 2.0 - Clean Architecture  
> **Fecha:** Enero 2026  
> **Proyecto:** Sistema Multimodal de Detección de Deepfakes

---

## 📋 Resumen Ejecutivo

**UIDE Forense AI** es un sistema de análisis forense digital que detecta:
- **Imágenes sintéticas** (GANs + Modelos de Difusión)
- **Videos deepfake** (manipulación facial)
- **Audio sintético** (voces de IA, clonación)

### Stack Tecnológico
| Capa | Tecnología |
|------|------------|
| Frontend | Gradio 4.0+ |
| Backend | Python 3.8+ |
| ML Framework | PyTorch 2.0+, HuggingFace Transformers |
| Modelos | ResNet50, ViT, XceptionNet, Wav2Vec2 |

---

## 🏗️ Arquitectura Clean Architecture

```
ProyectoForenseUIDE/
│
├── app.py                    # SOLO interfaz Gradio (controlador)
├── config.py                 # Configuración centralizada (Pathlib)
├── requirements.txt          # Dependencias
│
├── core/                     # 🧠 CEREBRO - Gestión de modelos
│   ├── __init__.py
│   ├── model_manager.py      # Singleton con lazy loading
│   └── processor.py          # Pre-procesamiento de datos
│
├── modules/                  # 🔍 DETECTORES - Lógica de negocio
│   ├── __init__.py
│   ├── image_forensics.py    # Ensamble GAN + Difusión
│   ├── video_forensics.py    # XceptionNet deepfakes
│   └── audio_forensics.py    # Voz sintética (HuggingFace)
│
├── utils/                    # 🛠️ UTILIDADES
│   ├── __init__.py
│   ├── plotting.py           # SVG gauges, gráficos temporales
│   └── file_handlers.py      # Validadores + Reportes HTML
│
└── weights/                  # 📦 MODELOS
    └── blur_jpg_prob0.1.pth  # Modelo GAN (Wang et al.)
```

---

## 📦 Componentes Principales

### 1. `config.py` - Configuración Centralizada

```python
from pathlib import Path

# Rutas compatibles Windows/Unix
BASE_DIR = Path(__file__).parent.resolve()
WEIGHTS_DIR = BASE_DIR / "weights"
MODEL_IMAGE_PATH = WEIGHTS_DIR / "blur_jpg_prob0.1.pth"

# Modelos HuggingFace
MODEL_DIFFUSION_NAME = "umm-maybe/AI-image-detector"
MODEL_AUDIO_NAME = "MelodyMachine/Deepfake-audio-detection"

# Límites
MAX_IMAGE_SIZE_MB = 15
MAX_VIDEO_SIZE_MB = 200
MAX_AUDIO_SIZE_MB = 50

# Umbrales de clasificación
IMAGE_THRESHOLD = 50.0  # >50% = FAKE
VIDEO_THRESHOLD = 50.0
AUDIO_THRESHOLD = 50.0
```

---

### 2. `core/model_manager.py` - Gestión de Modelos

```python
class ModelManager:
    """
    Singleton con lazy loading para modelos.
    - cargar_modelo_imagen_gan() -> ResNet50
    - cargar_modelo_video() -> XceptionNet
    """
```

**Características:**
- **Lazy Loading**: Modelos solo se cargan cuando se necesitan
- **Caché**: Una vez cargado, se reutiliza
- **Error Handling**: Modo demo si falla carga

---

### 3. `modules/image_forensics.py` - Detector de Imágenes

```python
class ImageForensicsDetector:
    """
    ENSAMBLE de dos modelos:
    1. Experto GAN (ResNet50) - Detecta StyleGAN, FaceApp
    2. Experto Difusión (ViT) - Detecta Midjourney, DALL-E, SD
    
    Decisión: MAX(prob_gan, prob_diffusion)
    """
    
    def predict(self, image) -> Dict:
        return {
            "score": 85.5,
            "verdict": "SINTÉTICO",
            "detected_source": "Difusión (Midjourney/DALL-E)",
            "gan_score": 30.2,
            "diffusion_score": 85.5,
        }
```

---

### 4. `modules/video_forensics.py` - Detector de Deepfakes

```python
class VideoForensicsDetector:
    """
    Análisis frame-by-frame de videos.
    - Detección de rostros: Haar Cascade
    - Clasificación: XceptionNet (FaceForensics++)
    - Estrategia: Promedio Top-K (10% más sospechosos)
    """
```

---

### 5. `modules/audio_forensics.py` - Detector de Audio Sintético

```python
class AudioForensicsDetector:
    """
    NUEVO en v2.0: Detección de voces de IA.
    - Modelo: HuggingFace (Wav2Vec2-based)
    - Detecta: ElevenLabs, RVC, TTS, clonación
    - Preprocesamiento: librosa @ 16kHz
    """
```

> ⚠️ **Primera ejecución**: Descarga modelo (~500MB) automáticamente con mensajes de progreso.

---

### 6. `utils/file_handlers.py` - Validación y Reportes

**Validadores:**
```python
validar_imagen(array) -> (bool, str)  # Dimensiones, formato
validar_video(path) -> (bool, str)    # Tamaño, extensión
validar_audio(path) -> (bool, str)    # Tamaño, formato
```

**Generadores de Reportes HTML:**
```python
generar_reporte_imagen(...)  # Con info de ensamble GAN+Difusión
generar_reporte_video(...)   # Con timeline y frame sospechoso
generar_reporte_audio(...)   # NUEVO: Para audio sintético
generar_reporte_error(...)   # Errores con estilo
```

---

## 🔄 Flujos de Análisis

### Flujo de Imagen (Ensamble)

```
Imagen → Validación → [GAN Detector] → prob_gan
                    ↘ [Diffusion ViT] → prob_diff
                                      ↘ MAX() → Resultado Final
```

### Flujo de Video

```
Video → Validación → Loop Frames → Detectar Rostro → XceptionNet → Predicciones[]
                                                                 ↘ Top-K Average → Resultado
```

### Flujo de Audio (Nuevo)

```
Audio → Validación → librosa 16kHz → Feature Extractor → Wav2Vec2 → Clasificación
```

---

## 🧠 Modelos de IA

| Modelo | Tipo | Detecta | Accuracy |
|--------|------|---------|----------|
| ResNet50 (Wang) | Imagen | GANs, ProGAN, StyleGAN | ~95% |
| ViT (HuggingFace) | Imagen | DALL-E, Midjourney, SD | ~90% |
| XceptionNet | Video | Face2Face, FaceSwap, DeepFake | ~92% |
| Wav2Vec2-based | Audio | ElevenLabs, RVC, TTS | ~88% |

---

## 📊 Interfaz Gradio (app.py)

```python
# TAB 1: Imágenes (GAN + Difusión)
# TAB 2: Video (Deepfakes)  
# TAB 3: Audio (Voz Sintética) - NUEVO
# TAB 4: Acerca de
```

La interfaz ahora es **solo un controlador** que:
1. Recibe archivos del usuario
2. Delega a los detectores en `modules/`
3. Muestra reportes generados por `utils/`

---

## 🔧 Configuración Rápida

### Cambiar Umbrales
```python
# config.py
IMAGE_THRESHOLD = 60.0  # Más estricto
VIDEO_THRESHOLD = 40.0  # Más permisivo
```

### Cambiar Modelos HuggingFace
```python
# config.py
MODEL_DIFFUSION_NAME = "otro-modelo/detector"
MODEL_AUDIO_NAME = "otro-modelo/audio-detect"
```

### Habilitar GPU
```python
# config.py
DEVICE = "cuda"  # En lugar de "cpu"
```

---

## 🚀 Ejecución

```powershell
# Windows
cd c:\Users\anper\Downloads\ProyectoForenseUIDE
pip install -r requirements.txt
python app.py

# Abrir http://localhost:7860
```

### Primera Ejecución
- Los modelos de HuggingFace se descargan automáticamente
- Verás mensajes claros de progreso en la consola
- La primera carga puede tomar 2-5 minutos

---

## 🚨 Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| "Modelo no disponible" | Archivo .pth faltante | Verificar `weights/` |
| Error descarga HuggingFace | Sin conexión | Verificar internet |
| "Pocos rostros detectados" | Video sin caras | Usar video con rostros claros |
| Encoding error (Windows) | UTF-8 | Ejecutar con `$env:PYTHONUTF8=1` |

---

## 📁 Archivos Clave

| Archivo | Propósito | Líneas |
|---------|-----------|-------|
| `app.py` | Solo interfaz Gradio | ~300 |
| `config.py` | Configuración | ~90 |
| `core/model_manager.py` | Gestión modelos | ~170 |
| `modules/image_forensics.py` | Detector imágenes | ~230 |
| `modules/video_forensics.py` | Detector videos | ~210 |
| `modules/audio_forensics.py` | Detector audio | ~175 |
| `utils/file_handlers.py` | Validación + HTML | ~350 |
| `utils/plotting.py` | Gráficos SVG | ~160 |

---

## 📚 Referencias

- [CNNDetection Paper](https://arxiv.org/abs/1912.11035) - Wang et al.
- [FaceForensics++](https://github.com/ondyari/FaceForensics)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)
- [Gradio Documentation](https://gradio.app/docs)

---

## 🎓 Contexto Académico

- **Universidad:** UIDE (Universidad Internacional del Ecuador)
- **Equipo:** Anthony Perez, Bruno Ortega, Manuel Pacheco
- **Objetivo:** Análisis forense digital con IA para tesis
- **Versión:** 2.0 Clean Architecture (Enero 2026)
