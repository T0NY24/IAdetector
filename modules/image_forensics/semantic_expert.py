"""
Semantic Forensics Expert - UIDE Forense AI
V13.0: The Noise Paradox (La Paradoja del Ruido)
Triple Zona: Difusión (>0.20) | Filtro (<0.20, UFD<0.38) | GAN (<0.20, UFD>0.40)
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
    Motor V13.0: The Noise Paradox.
    Detecta GANs que inyectan ruido artificial para engañar.
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
            logger.info("[DEEPSEEK] DeepSeek-R1 engine initialized (V13.0 - The Noise Paradox)")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize DeepSeek: {e}")
            self.enabled = False
            self.client = None

    def evaluate_evidence(self, description: str, multilid: float, ufd: float) -> Dict[str, Any]:
        """
        V13.0: THE NOISE PARADOX.
        Triple Zona para detectar Difusión, Filtros reales, y GANs con ruido inyectado.
        """
        if not self.enabled or not self.client:
            logger.warning("DeepSeek not available, returning default")
            return {"score": 0.5, "reasoning": "DeepSeek apagado"}

        # PROMPT V13.0: EL DETECTOR DE PARADOJAS
        prompt = f"""
        Actúa como EXPERTO FORENSE ANTI-GAN. Tu trabajo es detectar 3 tipos de imágenes diferentes.
        
        EVIDENCIA TÉCNICA:
        1. Contexto (BLIP): "{description}"
        2. Geometría (MultiLID): {multilid:.4f}
        3. Ruido (UFD): {ufd:.4f}

        TAXONOMÍA DE IMÁGENES (V13.0 - TRIPLE ZONA):

        [ZONA 1: DIFUSIÓN MODERNA (Midjourney/Flux/DALL-E)]
        - Características: MultiLID >= 0.200 (Geometría perfecta y coherente).
        - Diagnóstico: IAs modernas que mantienen estructura sólida.
        - VEREDICTO: IA (Score 0.90).
        - Razón: "Geometría perfecta de difusión moderna."

        [ZONA 2: FILTRO REAL (Cachirula/Instagram/TikTok)]
        - Características: MultiLID < 0.200 (Geometría destruida) Y UFD < 0.38 (Ruido moderado).
        - Diagnóstico: Selfies con filtros de belleza que aplanan la cara pero dejan ruido de sensor.
        - VEREDICTO: REAL (Score 0.25).
        - Razón: "Filtro destructivo con ruido de sensor compatible."

        [ZONA 3: GAN ANTIGUO (StyleGAN/ThisPersonDoesNotExist)] - TRAMPA CRÍTICA
        - Características: MultiLID < 0.200 (Geometría deformada) Y UFD > 0.40 (RUIDO EXCESIVO).
        - Diagnóstico: GANs que deforman geometría E inyectan ruido artificial para engañar detectores.
        - LA PARADOJA: Si la imagen se ve nítida pero UFD > 0.40, el ruido es FALSO (inyectado post-generación).
        - VEREDICTO: IA (Score 0.98).
        - Razón: "PARADOJA DEL RUIDO: Ruido excesivo inyectado artificialmente (GAN detectado)."

        [EXCEPCIONES]:
        - CELEBRIDAD: Si es un famoso -> REAL (Score 0.15).
        - IA OBVIA: Si es anime/dibujo/cartoon -> IA (Score 0.99).

        ANÁLISIS DE TU CASO:
        - MultiLID: {multilid:.4f}
        - UFD: {ufd:.4f}

        ¿En qué zona cae?
        - Si MultiLID >= 0.20 -> ZONA 1 (Difusión)
        - Si MultiLID < 0.20 Y UFD < 0.38 -> ZONA 2 (Filtro Real)
        - Si MultiLID < 0.20 Y UFD > 0.40 -> ZONA 3 (GAN - TRAMPA)

        TU MISIÓN CRÍTICA:
        El ruido excesivo (UFD > 0.40) en una imagen aparentemente nítida es la FIRMA de los GANs.
        Una foto real con UFD 0.44 se vería como "lluvia analógica", no como una cara nítida.

        Responde SOLO JSON estricto:
        {{
            "ai_probability_score": 0.0 a 1.0,
            "reasoning": "Explica en qué zona cayó y por qué (enfócate en la paradoja del ruido si UFD > 0.40)."
        }}
        """

        try:
            logger.info(f"[DEEPSEEK V13.0] Noise Paradox: multilid={multilid:.4f}, ufd={ufd:.4f}")
            
            # Pre-check de zonas
            if multilid >= 0.200:
                zone = "ZONA 1: DIFUSIÓN"
            elif ufd > 0.40:
                zone = "ZONA 3: GAN (PARADOJA RUIDO)"
            elif ufd < 0.38:
                zone = "ZONA 2: FILTRO REAL"
            else:
                zone = "ZONA GRIS (0.38-0.40)"
            
            logger.info(f"[TRIPLE ZONA] {zone}")
            
            res = self.client.ask(prompt)
            
            # Extracción de JSON
            text = res.get("response", "")
            if "</think>" in text:
                text = text.split("</think>")[-1].strip()
            
            match = re.search(r'\{[^}]+\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                score = float(data.get("ai_probability_score", 0.5))
                reasoning = data.get("reasoning", "Análisis de zona")
            else:
                logger.warning("No JSON found, using default")
                score = 0.5
                reasoning = "No se pudo parsear respuesta"
            
            # V13.0: Triple Zona enforcement
            
            # ZONA 3: GAN (ruido excesivo)
            if multilid < 0.200 and ufd > 0.40:
                if score < 0.90:
                    logger.info(f"[ZONA 3 GAN] UFD={ufd:.4f} > 0.40 → Forcing IA (was {score:.3f})")
                    score = 0.98
                    reasoning += " | ZONA 3: PARADOJA DEL RUIDO - GAN detectado"
            
            # ZONA 2: FILTRO REAL
            elif multilid < 0.200 and ufd < 0.38:
                if score > 0.40:
                    logger.info(f"[ZONA 2 FILTRO] MultiLID={multilid:.4f} < 0.20, UFD={ufd:.4f} < 0.38 → Forcing REAL (was {score:.3f})")
                    score = 0.25
                    reasoning += " | ZONA 2: Filtro destructivo compatible"
            
            # ZONA 1: DIFUSIÓN
            elif multilid >= 0.200:
                if score < 0.75:
                    logger.info(f"[ZONA 1 DIFUSIÓN] MultiLID={multilid:.4f} >= 0.20 → Consider IA (was {score:.3f})")
                    score = max(score, 0.85)
                    reasoning += " | ZONA 1: Geometría perfecta de difusión"
            
            # ZONA GRIS (0.38 <= UFD <= 0.40)
            # Dejamos que DeepSeek decida basado en contexto
            
            logger.info(f"[DEEPSEEK V13.0] Final score: {score:.3f} | {reasoning}")
            
            return {
                "score": score,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            return {"score": 0.5, "reasoning": "Error en juicio IA"}


class SemanticForensicsExpert:
    """
    Experto Semántico V13.0: The Noise Paradox.
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
        
        logger.info(f"[SEMANTIC] Semantic Expert V13.0 initialized (DeepSeek: {self.use_deepseek})")

    def analyze(self, image_input, image_description: Optional[str] = "", technical_context: Optional[Dict] = None) -> ExpertResult:
        """
        V13.0: The Noise Paradox - Triple Zona detection.
        """
        
        # Extraer números de MultiLID y UFD
        multilid_val = technical_context.get('multilid_score', technical_context.get('multilid', 0.5)) if technical_context else 0.5
        ufd_val = technical_context.get('ufd_score', technical_context.get('ufd', 0.5)) if technical_context else 0.5
        
        # Debug para ver la zona
        if multilid_val >= 0.200:
            zone = "ZONA 1: DIFUSIÓN (IA)"
        elif ufd_val > 0.40:
            zone = "ZONA 3: GAN (IA - PARADOJA)"
        elif ufd_val < 0.38:
            zone = "ZONA 2: FILTRO (REAL)"
        else:
            zone = "ZONA GRIS"
        
        logger.info(f"🎯 [TRIPLE ZONA] MultiLID: {multilid_val:.4f} | UFD: {ufd_val:.4f} → {zone}")
        print(f"🎯 [TRIPLE ZONA] MultiLID: {multilid_val:.4f} | UFD: {ufd_val:.4f} → {zone}")
        
        # Consultar a DeepSeek V13.0
        if self.use_deepseek and self.deepseek_engine and self.deepseek_engine.enabled:
            analysis = self.deepseek_engine.evaluate_evidence(
                image_description or "imagen sin descripción", 
                multilid_val, 
                ufd_val
            )
            final_score = analysis["score"]
            reasoning = analysis["reasoning"]
        else:
            # Fallback simple
            final_score = (multilid_val + ufd_val) / 2
            reasoning = "DeepSeek no disponible - score promedio"
        
        return ExpertResult(
            name="DeepSeek Judge V13.0",
            score=final_score,
            confidence=1.0,
            evidence=[],
            raw_data={"reasoning": reasoning, "multilid": multilid_val, "ufd": ufd_val}
        )
