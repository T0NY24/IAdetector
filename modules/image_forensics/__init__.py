"""
Image Forensics Module - Detección de imágenes sintéticas.

UIDE Forense AI v3.0+

Módulo de análisis forense de imágenes basado en:
- multiLID: Análisis geométrico del espacio de features
- UniversalFakeDetect: Clasificación visual generalizable
- SemanticForensics: Análisis de plausibilidad semántica (NUEVO)

Uso:
    from modules.image_forensics import ImageForensicsDetector
    
    detector = ImageForensicsDetector()
    result = detector.analyze(image)
    print(result.to_dict())
"""

from .detector import ImageForensicsDetector
from .schemas import ForensicResult, ExpertResult, Verdict, Confidence
from .semantic_expert import SemanticForensicsExpert

__all__ = [
    "ImageForensicsDetector",
    "ForensicResult",
    "ExpertResult",
    "Verdict",
    "Confidence",
    "SemanticForensicsExpert",
]

__version__ = "3.1.0"
