"""
Configuración centralizada del proyecto UIDE Forense AI
Clean Architecture - Actualizado con soporte multimodal
"""

import os
from pathlib import Path

# ==========================================
# 📁 Rutas de Archivos (Compatible Windows/Unix)
# ==========================================
BASE_DIR = Path(__file__).parent.resolve()
WEIGHTS_DIR = BASE_DIR / "weights"
SAMPLES_DIR = BASE_DIR / "samples"

# Rutas de modelos locales
MODEL_IMAGE_PATH = WEIGHTS_DIR / "blur_jpg_prob0.1.pth"

# Nombres de modelos (timm/HuggingFace)
MODEL_VIDEO_NAME = "xception"
MODEL_DIFFUSION_NAME = "umm-maybe/AI-image-detector"
MODEL_AUDIO_NAME = "MelodyMachine/Deepfake-audio-detection"

# ==========================================
# 📊 Límites y Validación
# ==========================================
MAX_IMAGE_SIZE_MB = 15
MAX_VIDEO_SIZE_MB = 200
MAX_AUDIO_SIZE_MB = 50
MAX_VIDEO_DURATION_SECONDS = 300  # 5 minutos
MAX_AUDIO_DURATION_SECONDS = 600  # 10 minutos

# Formatos soportados
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']

# ==========================================
# 🎯 Parámetros de Análisis - Imágenes
# ==========================================
IMAGE_THRESHOLD = 50.0  # Umbral de clasificación (%)
IMAGE_SIZE = 224

# Transformaciones estándar (CNNDetection)
TRANSFORMS_RESIZE = 256
TRANSFORMS_CROP = 224
TRANSFORMS_MEAN = [0.485, 0.456, 0.406]
TRANSFORMS_STD = [0.229, 0.224, 0.225]

# ==========================================
# 🎯 Parámetros de Análisis - Video
# ==========================================
VIDEO_FRAME_STRIDE = 30  # Analizar 1 frame cada N frames
VIDEO_SIZE = 299
VIDEO_THRESHOLD = 50.0
MIN_FACES_REQUIRED = 3  # Mínimo de rostros para análisis válido

# ==========================================
# 🎯 Parámetros de Análisis - Audio
# ==========================================
AUDIO_SAMPLE_RATE = 16000  # Sample rate para modelos de voz
AUDIO_THRESHOLD = 50.0  # Umbral de clasificación (%)
AUDIO_MAX_DURATION = 30  # Máximo segundos a analizar por chunk

# ==========================================
# 🎨 Configuración UI
# ==========================================
DEFAULT_THEME = "soft"
PRIMARY_COLOR = "blue"
SECONDARY_COLOR = "slate"

# Colores para reportes
COLOR_FAKE = "#ef4444"      # Rojo
COLOR_REAL = "#22c55e"      # Verde
COLOR_WARNING = "#f59e0b"   # Ámbar
COLOR_INFO = "#3b82f6"      # Azul

# ==========================================
# 🔧 Configuración Técnica
# ==========================================
DEVICE = "cpu"  # Cambiar a 'cuda' si hay GPU disponible
NUM_WORKERS = 4
ENABLE_CACHE = True

# HuggingFace Cache (opcional - usa default si no se especifica)
# HF_CACHE_DIR = WEIGHTS_DIR / "hf_cache"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
