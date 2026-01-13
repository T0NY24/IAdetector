"""
Core module - Sistema de gestión de modelos y procesamiento
UIDE Forense AI
"""

from .model_manager import ModelManager
from .processor import preprocess_image, preprocess_video_frame, preprocess_audio

__all__ = [
    'ModelManager',
    'preprocess_image',
    'preprocess_video_frame', 
    'preprocess_audio',
]
