"""
Semantic Forensics Expert - UIDE Forense AI
V10.0: Data-Driven DeepSeek (Simplified)
DeepSeek recibe los números de MultiLID y UFD directamente y decide.
"""
import logging
import json
import re
from typing import Dict, Optional, Any
from PIL import Image
import torch

from .schemas import ExpertResult
from .feature_extractor import CLIPFeatureExtractor
import config

# Importar DeepSeek
try:
    from services.deepseek_client import DeepSeekClient
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False

logger = logging.getLogger(__name__)


class DeepSeekSemanticEngine:
    """
    Motor de razonamiento V10.0: El Doctor que lee los análisis.
    """
    def __init__(self, api_url=None):
        self.enabled = DEEPSEEK_AVAILABLE
        
        if not self.enabled:
            logger.info("[DEEPSEEK] DeepSeek engine disabled")
            self.client = None
            return
        
        api_url = api_url or getattr(config, 'DEEPSEEK_API_URL', 'http://localhost:11434/api/generate')
        
        try:
            self.client = DeepSeekClient(url=api_url)
            logger.info("[DEEPSEEK] DeepSeek-R1 engine initialized (V10.0 - Data-Driven)")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize DeepSeek: {e}")
            self.enabled = False
            self.client = None

    def evaluate_evidence(self, description: str, multilid: float, ufd: float) -> Dict[str, Any]:
        """
        DeepSeek analiza los números y el contexto visual para decidir.
        V10.0: Solo devuelve un score final (0.0-1.0).
        """
        if not self.enabled or not self.client:
            logger.warning("DeepSeek not available, returning default")
            return {"score": 0.5, "reasoning": "DeepSeek apagado"}

        # PROMPT V10.0: EL ANALISTA DE DATOS
        prompt = f"""
        Actúa como PERITO FORENSE DIGITAL EXPERTO. Tu trabajo es interpretar datos técnicos y contexto visual.
        
        DATOS DEL PACIENTE (IMAGEN):
        1. Descripción Visual: "{description}"
        2. Score Geometría (MultiLID): {multilid:.3f} (Bajo < 0.25 = Muy Plano/Perfecto; Alto > 0.40 = Profundidad Natural)
        3. Score Ruido (UFD): {ufd:.3f} (Bajo < 0.20 = Sin Ruido/Limpio; Alto > 0.35 = Grano de Cámara)

        REGLAS DE INTERPRETACIÓN (V10.0 - PROTOCOLO SOCIAL):
        
        CASO 0: CELEBRIDAD / FAMOSO (Prioridad Máxima)
        - Si la descripción menciona a un famoso (ej. Scarlett Johansson, Elon Musk, Cantantes, Actores):
        - IGNORA los scores bajos de geometría. Los famosos usan maquillaje profesional y edición.
        - VEREDICTO: REAL (Score bajo: 0.10 - 0.20).
        
        CASO 1: ESTÉTICA DE REDES SOCIALES (Influencers/Selfies)
        - Si es una persona joven, selfie, o estilo "Instagram/TikTok":
        - Es normal tener MultiLID bajo (filtros de belleza) y UFD bajo (reducción de ruido del móvil).
        - NO ES IA. ES FILTRO DE BELLEZA.
        - VEREDICTO: REAL (Score medio-bajo: 0.30 - 0.45).

        CASO 2: IA GENERATIVA (Midjourney/Flux/DALL-E)
        - Si la imagen tiene fallos lógicos (dedos extra, texto ilegible, objetos imposibles).
        - O si es un dibujo/anime/pintura claramente digital.
        - VEREDICTO: IA (Score alto: 0.85 - 0.99).

        CASO 3: FOTOGRAFÍA ESTÁNDAR
        - Si UFD > 0.35 (tiene ruido natural) Y MultiLID > 0.30 (tiene profundidad).
        - VEREDICTO: REAL (Score muy bajo: 0.10 - 0.15).

        ZONA DE FILTROS (0.65-0.94 en versiones anteriores):
        - Si los números sugieren edición (MultiLID bajo, UFD bajo) pero NO hay anomalías físicas:
        - VEREDICTO: REAL con filtros (Score: 0.35 - 0.50).
        
        TU MISIÓN:
        Basado en los números técnicos y la descripción visual, dame la probabilidad de que sea IA GENERATIVA.
        
        Responde SOLO JSON estricto:
        {{
            "ai_probability_score": 0.0 a 1.0,
            "reasoning": "Explica tu decisión en 1-2 frases basado en los números y el contexto."
        }}
        """

        try:
            logger.info(f"[DEEPSEEK V10.0] Consulting with multilid={multilid:.3f}, ufd={ufd:.3f}")
            res = self.client.ask(prompt)
            
            # Extracción simple de JSON
            text = res.get("response", "")
            
            # Quitar el bloque </think> si existe
            if "</think>" in text:
                text = text.split("</think>")[-1].strip()
            
            # Buscar JSON
            match = re.search(r'\{[^}]+\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                score = float(data.get("ai_probability_score", 0.5))
                reasoning = data.get("reasoning", "Análisis estándar")
            else:
                logger.warning("No JSON found in response, using default")
                score = 0.5
                reasoning = "No se pudo parsear respuesta"
            
            logger.info(f"[DEEPSEEK V10.0] Final score: {score:.3f} | {reasoning}")
            
            return {
                "score": score,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            return {"score": 0.5, "reasoning": "Error en análisis, defaulting to inconclusive"}


class SemanticForensicsExpert:
    """
    Experto Semántico V10.0: Simplificado.
    Ya no usa banderas, solo pasa números a DeepSeek.
    """
    def __init__(self, feature_extractor: CLIPFeatureExtractor, deepseek_engine=None, use_deepseek=True):
        self.extractor = feature_extractor
        self.use_deepseek = use_deepseek
        
        if self.use_deepseek:
            if deepseek_engine:
                self.deepseek_engine = deepseek_engine
            else:
                self.deepseek_engine = DeepSeekSemanticEngine()
        else:
            self.deepseek_engine = None
        
        logger.info(f"[SEMANTIC] Semantic Expert V10.0 initialized (DeepSeek: {self.use_deepseek})")

    def analyze(self, image_input, image_description: Optional[str] = "", technical_context: Optional[Dict] = None) -> ExpertResult:
        """
        V10.0: Simple analysis - pass numbers to DeepSeek, get score back.
        """
        
        # Extraer números previos de MultiLID y UFD
        multilid_val = technical_context.get('multilid_score', technical_context.get('multilid', 0.5)) if technical_context else 0.5
        ufd_val = technical_context.get('ufd_score', technical_context.get('ufd', 0.5)) if technical_context else 0.5
        
        # Consultar al Doctor DeepSeek con los números
        if self.use_deepseek and self.deepseek_engine and self.deepseek_engine.enabled:
            analysis = self.deepseek_engine.evaluate_evidence(image_description or "imagen sin descripción", multilid_val, ufd_val)
            final_score = analysis["score"]
            reasoning = analysis["reasoning"]
        else:
            # Fallback simple si DeepSeek no está disponible
            final_score = (multilid_val + ufd_val) / 2
            reasoning = "DeepSeek no disponible - score promedio"
        
        return ExpertResult(
            name="DeepSeek Judge V10.0",
            score=final_score,
            confidence=1.0,
            evidence=[],
            raw_data={"reasoning": reasoning, "multilid": multilid_val, "ufd": ufd_val}
        )
