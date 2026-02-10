"""
Configuración Actualizada - Flask Backend
UIDE Forense AI 3.0+ con DeepSeek-R1
"""

import os
from pathlib import Path

# ==========================================
# 📁 Rutas Base
# ==========================================
BASE_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = BASE_DIR / "backend"
WEIGHTS_DIR = BASE_DIR / "weights"
UPLOAD_FOLDER = BACKEND_DIR / "uploads"
LOGS_DIR = BACKEND_DIR / "logs"

# ==========================================
# 🌐 Flask Configuration
# ==========================================
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
TESTING = False

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# Upload limits
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB (para soportar videos)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}  # Solo imágenes (legacy)
ALLOWED_EXTENSIONS_IMAGE = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}
ALLOWED_EXTENSIONS_VIDEO = {'mp4', 'avi', 'mov', 'mkv'}
ALLOWED_EXTENSIONS_AUDIO = {'mp3', 'wav', 'm4a', 'ogg', 'flac'}


# ==========================================
# 🖼️ Image Forensics Configuration
# ==========================================

# CLIP
CLIP_MODEL_NAME = "ViT-L/14"

# multiLID
LID_K_NEIGHBORS = 20
LID_LAYERS = [6, 8, 10, 11]

# UFD
UFD_WEIGHTS_PATH = WEIGHTS_DIR / "ufd_classifier.pth"
UFD_TEMPERATURE = 1.5

# Semantic Expert
SEMANTIC_ENABLED = True
SEMANTIC_THRESHOLDS = {
    "improbability_high": 0.65,
    "improbability_medium": 0.45,
    "collision_significant": 0.55,
    "composition_synthetic": 0.60,
    "overall_synthetic": 0.55,
}

# ==========================================
# 🎥 Video Forensics Configuration
# ==========================================
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv'}
MAX_VIDEO_SIZE_MB = 100  # 100MB máximo para videos
MAX_VIDEO_DURATION_SECONDS = 120  # 2 minutos máximo
VIDEO_SIZE = 299  # Tamaño de frame para XceptionNet (299x299)
MODEL_VIDEO_NAME = 'xception'  # Modelo timm para detección de deepfakes
VIDEO_FRAME_STRIDE = 30  # Analizar 1 frame cada 30
MIN_FACES_REQUIRED = 5  # Mínimo de rostros para análisis confiable
VIDEO_THRESHOLD = 50.0  # Umbral de detección de deepfake (0-100)

# ==========================================
# 🔊 Audio Forensics Configuration
# ==========================================
SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
MAX_AUDIO_SIZE_MB = 20  # 20MB máximo
AUDIO_SAMPLE_RATE = 16000  # Hz
AUDIO_MAX_DURATION = 60  # 60 segundos máximo
# Detección heurística basada en análisis espectral (sin modelo pesado)

# ==========================================
# 🤖 DeepSeek-R1 LLM Configuration
# ==========================================
DEEPSEEK_ENABLED = os.getenv("DEEPSEEK_ENABLED", "false").lower() == "true"
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "http://localhost:11434/api/generate")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-r1:7b")
DEEPSEEK_TIMEOUT = int(os.getenv("DEEPSEEK_TIMEOUT", "60"))
DEEPSEEK_MAX_RETRIES = int(os.getenv("DEEPSEEK_MAX_RETRIES", "3"))
DEEPSEEK_TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.3"))

# ==========================================
# ⚗️ Fusion Engine
# ==========================================
FUSION_THRESHOLDS = {
    "gate_multilid": 0.25,
    "gate_ufd": 0.45,
    "gate_semantic": 0.55,
    "ia_multilid_strong": 0.45,
    "ia_ufd_definitive": 0.70,
    "ia_ufd_strong": 0.55,
    "ia_ufd_with_semantic": 0.45,
    "ia_semantic_support": 0.60,
}

# ==========================================
# 🔧 Technical Settings
# ==========================================
DEVICE = os.getenv("DEVICE", "cpu")  # 'cuda' si hay GPU
NUM_WORKERS = int(os.getenv("NUM_WORKERS", "4"))
ENABLE_CACHE = True

# Transforms
TRANSFORMS_RESIZE = (224, 224)
TRANSFORMS_CROP = 224
TRANSFORMS_MEAN = [0.485, 0.456, 0.406]
TRANSFORMS_STD = [0.229, 0.224, 0.225]

# ==========================================
# 📊 Logging
# ==========================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==========================================
# 🚀 Production Settings
# ==========================================
# Gunicorn
GUNICORN_WORKERS = int(os.getenv("GUNICORN_WORKERS", "4"))
GUNICORN_BIND = os.getenv("GUNICORN_BIND", "127.0.0.1:5000")
GUNICORN_TIMEOUT = int(os.getenv("GUNICORN_TIMEOUT", "120"))

# ==========================================
# 🔒 Security
# ==========================================
# En producción, configurar desde variables de entorno
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
