"""
Fusion Engine V10.0 (Direct Execution)
UIDE Forense AI - Simplified

V10.0: Confía plenamente en el juicio de DeepSeek.
Lógica binaria simple: > 0.60 = IA, ≤ 0.60 = REAL
"""

import logging
from typing import Optional

from .schemas import ExpertResult, ForensicResult

logger = logging.getLogger(__name__)

# --- CONSTANTES DE VEREDICTO (Solo 2) ---
VERDICT_IA = "GENERADA POR IA / SINTÉTICA"
VERDICT_REAL = "COMPATIBLE CON FOTOGRAFÍA REAL"


class FusionEngine:
    """
    Fusion Engine V10.0 (Direct Execution)
    No piensa, solo ejecuta la decisión de DeepSeek.
    """
    
    def __init__(self):
        logger.info("⚗️ FusionEngine V10.0 (Direct Execution) inicializado")

    def fuse(
        self,
        multilid_result: ExpertResult,
        ufd_result: ExpertResult,
        semantic_result: Optional[ExpertResult] = None
    ) -> ForensicResult:
        """
        V10.0: Lógica binaria simple basada en el score de DeepSeek.
        
        DeepSeek ya consideró:
        - Los scores de MultiLID y UFD
        - El contexto visual (descripción)
        - Las reglas de celebridades/redes sociales
        
        Solo nos queda decidir: IA o REAL
        """
        
        if not semantic_result:
            # Fallback si no hay semantic
            final_score = 0.5
            reasoning = "No semantic analysis available"
        else:
            # El score principal viene de DeepSeek (que ya leyó todo)
            final_score = semantic_result.score
            reasoning = semantic_result.raw_data.get("reasoning", "Análisis completado")

        # --- LÓGICA BINARIA SIMPLE ---
        # Umbral: 0.60
        # Damos margen a fotos editadas/filtros (0.30-0.55)
        
        if final_score > 0.60:
            verdict = VERDICT_IA
            confidence = "ALTA"
            notes = f"🚫 IA DETECTADA: {reasoning}"
        else:
            verdict = VERDICT_REAL
            confidence = "ALTA"
            notes = f"✅ FOTO REAL: {reasoning}"

        # Preparar porcentajes limpios para el Frontend
        ai_prob = round(final_score * 100, 1)
        real_prob = round(100 - ai_prob, 1)

        logger.info(f"[FUSION V10.0] Score={final_score:.3f} → Verdict={verdict}")

        return ForensicResult(
            verdict=verdict,
            confidence=confidence,
            scores={
                "unified": final_score,
                "ai_probability": ai_prob,     # Para el Front
                "real_probability": real_prob,  # Para el Front
                "deepseek": final_score,
                "multilid": multilid_result.score,
                "ufd": ufd_result.score,
                "semantic": final_score
            },
            evidence=[],  # Ya no usamos listas de banderas
            notes=notes
        )
