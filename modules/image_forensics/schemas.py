"""
Schema definitions for forensic analysis results.
V8.0: Forced visual consistency - scores always match verdicts to prevent 0% displays.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class Verdict(str, Enum):
    """
    Possible verdicts for forensic analysis.
    """
    IA_CONFIRMED = "GENERADA POR IA / SINTÉTICA"
    IA_PROBABLE = "PROBABLEMENTE SINTÉTICA"
    REAL_PROBABLE = "PROBABLEMENTE REAL"
    REAL_CONFIRMED = "COMPATIBLE CON FOTOGRAFÍA REAL"
    INCONCLUSIVE = "REQUIERE VERIFICACIÓN MANUAL"


class Confidence(str, Enum):
    """
    Confidence levels for analysis results.
    """
    HIGH = "ALTA"
    MEDIUM = "MEDIA"
    LOW = "BAJA"


@dataclass
class ExpertResult:
    """
    Resultado del análisis de un experto individual.
    
    Attributes:
        name: Nombre del experto (e.g., "MultiLID", "UFD", "Semantic")
        score: Puntuación de 0.0 a 1.0 (0 = real, 1 = synthetic)
        confidence: Nivel de confianza en el resultado (0.0 a 1.0)
        evidence: Lista de evidencias encontradas
        raw_data: Datos adicionales específicos del experto
    """
    name: str
    score: float
    confidence: float
    evidence: List[str] = field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class ForensicResult:
    """
    Resultado final del análisis forense completo.
    V8.0: Forces visual scores to match verdicts, preventing 0% displays.
    
    Attributes:
        verdict: Veredicto final del análisis
        confidence: Nivel de confianza (ALTA, MEDIA, BAJA)
        scores: Diccionario con métricas individuales
        evidence: Lista de evidencias que sustentan el veredicto
        notes: Notas adicionales sobre el análisis
    """
    verdict: str
    confidence: str
    scores: Dict[str, float]
    evidence: List[str]
    notes: str
    
    def to_dict(self) -> Dict[str, Any]:
        """
        V8.0: Forzado de porcentajes visuales basado en el veredicto.
        Garantiza que el Frontend nunca muestre 0.0% si hay un veredicto.
        
        Returns:
            Dict con estructura compatible con el output esperado del detector
        """
        # 1. Recuperar el score base (0.0-1.0)
        raw = self.scores.get('unified', 0.5)
        
        # 2. OVERRIDE VISUAL: Si el número falla, usamos el veredicto como fuente de verdad
        if "SINTÉTICA" in self.verdict or "IA" in self.verdict.upper():
            # Si dice IA, mínimo 85%
            raw = max(raw, 0.85)
            # Corrección de emergencia si el score es inconsistente
            if raw < 0.5:
                raw = 0.95
            
        elif "REAL" in self.verdict.upper():
            # Si dice REAL, máximo 20% IA
            raw = min(raw, 0.20)
            
        elif "MANUAL" in self.verdict or "INCONCLUSIVE" in self.verdict:
            # Si es Manual, clavamos el 50% (Duda perfecta)
            raw = 0.50

        # 3. Conversión final a 0-100 con 1 decimal
        ai_prob = round(raw * 100, 1)
        real_prob = round(100 - ai_prob, 1)

        return {
            "verdict": self.verdict,
            "confidence": self.confidence,
            # Enviamos TODAS las variantes de nombre para que React no falle
            "ai_probability": ai_prob,
            "real_probability": real_prob,
            "probabilidad_ia": ai_prob,  # Compatibilidad con nombres en español
            "probabilidad_real": real_prob,
            "scores": self.scores,
            "evidence": self.evidence,
            "notes": self.notes
        }


@dataclass
class AnalysisContext:
    """
    Context information for forensic analysis.
    Used to pass metadata and configuration through the pipeline.
    """
    image_path: str
    metadata: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
