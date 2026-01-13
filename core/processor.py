"""
Processor - Funciones de pre-procesamiento de datos
UIDE Forense AI

Este módulo contiene funciones para preparar imágenes, video frames
y audio para el análisis con los modelos de detección.
"""

import logging
from typing import Tuple, Optional
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


def preprocess_image(image_array: np.ndarray) -> Image.Image:
    """
    Pre-procesa una imagen desde array numpy a PIL Image.
    
    Args:
        image_array: Array numpy de la imagen (RGB o BGR)
        
    Returns:
        PIL Image en modo RGB
    """
    try:
        img_pil = Image.fromarray(image_array).convert("RGB")
        return img_pil
    except Exception as e:
        logger.error(f"Error en preprocess_image: {e}")
        raise


def preprocess_video_frame(
    frame: np.ndarray,
    face_region: Tuple[int, int, int, int],
    margin_ratio: float = 0.2
) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
    """
    Pre-procesa un frame de video extrayendo la región del rostro con margen.
    
    Args:
        frame: Frame de video como array numpy (BGR de OpenCV)
        face_region: Tupla (x, y, w, h) del rostro detectado
        margin_ratio: Ratio de margen alrededor del rostro (default 0.2 = 20%)
        
    Returns:
        Tupla de (PIL Image del rostro en RGB, coordenadas expandidas)
    """
    import cv2
    
    x, y, w, h = face_region
    
    # Calcular margen de seguridad
    margin = int(w * margin_ratio)
    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(frame.shape[1], x + w + margin)
    y2 = min(frame.shape[0], y + h + margin)
    
    # Extraer ROI
    face_roi = frame[y1:y2, x1:x2]
    
    # Convertir BGR a RGB y luego a PIL
    face_rgb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
    face_pil = Image.fromarray(face_rgb)
    
    return face_pil, (x1, y1, x2, y2)


def preprocess_audio(audio_path: str, target_sr: int = 16000) -> Tuple[np.ndarray, int]:
    """
    Pre-procesa un archivo de audio para análisis.
    Carga y re-muestrea al sample rate objetivo.
    
    Args:
        audio_path: Ruta al archivo de audio
        target_sr: Sample rate objetivo (default 16000 Hz para modelos de voz)
        
    Returns:
        Tupla de (array de audio, sample rate)
    """
    try:
        import librosa
        
        logger.info(f"🔊 Cargando audio: {audio_path}")
        
        # Cargar audio y re-muestrear
        audio_array, sr = librosa.load(audio_path, sr=target_sr)
        
        logger.info(f"✅ Audio cargado: {len(audio_array)/sr:.2f}s @ {sr}Hz")
        
        return audio_array, sr
        
    except ImportError:
        logger.error("❌ librosa no está instalado. Ejecuta: pip install librosa")
        raise
    except Exception as e:
        logger.error(f"❌ Error cargando audio: {e}")
        raise


def extract_mel_spectrogram(
    audio_array: np.ndarray,
    sr: int = 16000,
    n_mels: int = 128,
    n_fft: int = 2048,
    hop_length: int = 512
) -> np.ndarray:
    """
    Extrae un espectrograma Mel de una señal de audio.
    Útil para visualización y algunos modelos de clasificación.
    
    Args:
        audio_array: Array de audio
        sr: Sample rate
        n_mels: Número de bandas Mel
        n_fft: Tamaño de FFT
        hop_length: Salto entre frames
        
    Returns:
        Espectrograma Mel en dB
    """
    try:
        import librosa
        
        mel_spec = librosa.feature.melspectrogram(
            y=audio_array,
            sr=sr,
            n_mels=n_mels,
            n_fft=n_fft,
            hop_length=hop_length
        )
        
        # Convertir a dB
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        return mel_spec_db
        
    except ImportError:
        logger.error("❌ librosa no está instalado")
        raise
