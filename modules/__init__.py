"""
Modules - Módulos de análisis forense independientes
UIDE Forense AI
"""

from .image_forensics import ImageForensicsDetector
from .video_forensics import VideoForensicsDetector
from .audio_forensics import AudioForensicsDetector

__all__ = [
    'ImageForensicsDetector',
    'VideoForensicsDetector',
    'AudioForensicsDetector',
]
