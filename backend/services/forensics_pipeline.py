"""
Forensics Analysis Pipeline - UIDE Forense AI
V10.0: Data-Driven DeepSeek (Simplified)

Workflow:
1. Peritos: Collect technical numbers (MultiLID, UFD)
2. Doctor: DeepSeek reads numbers + image description → decides
3. Sentencia: Binary verdict (IA or REAL)
"""

import logging
from dataclasses import dataclass
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

from modules.image_forensics.feature_extractor import CLIPFeatureExtractor
from modules.image_forensics.multilid_expert import MultiLIDExpert
from modules.image_forensics.ufd_expert import UFDExpert
from modules.image_forensics.semantic_expert import SemanticForensicsExpert
from modules.image_forensics.fusion_engine import FusionEngine
from modules.image_forensics.schemas import ForensicResult
from services.deepseek_client import DeepSeekClient
import config

logger = logging.getLogger(__name__)


class ForensicsPipeline:
    """
    V10.0 Data-Driven Pipeline:
    Numbers → DeepSeek → Binary Decision
    """
    
    def __init__(self, deepseek_enabled=True):
        """Initialize V10.0 pipeline."""
        logger.info("[PIPELINE] Initializing UIDE Forense AI V10.0 (Data-Driven DeepSeek)...")
        
        # Device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"[PIPELINE] Using device: {self.device}")
        
        # CLIP feature extractor
        logger.info("[PIPELINE] Loading CLIP ViT-L/14...")
        self.feature_extractor = CLIPFeatureExtractor(device=self.device)
        
        # Forensic experts (number collectors)
        logger.info("[PIPELINE] Initializing MultiLID Expert...")
        self.multilid = MultiLIDExpert(self.feature_extractor)
        
        logger.info("[PIPELINE] Initializing UFD Expert...")
        self.ufd = UFDExpert(self.feature_extractor)
        
        # BLIP for image description
        logger.info("[PIPELINE] Loading BLIP Vision Model...")
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model.to(self.device)
        
        # Semantic Expert with DeepSeek
        self.deepseek_enabled = deepseek_enabled
        logger.info(f"[PIPELINE] Initializing Semantic Expert V10.0 (DeepSeek: {deepseek_enabled})...")
        self.semantic = SemanticForensicsExpert(
            self.feature_extractor,
            use_deepseek=deepseek_enabled
        )
        
        # Fusion Engine V10.0
        logger.info("[PIPELINE] Initializing Fusion Engine V10.0 (Binary Logic)...")
        self.fusion = FusionEngine()
        
        logger.info("[PIPELINE] V10.0 (Data-Driven DeepSeek) ready!")

    def process(self, image_path: str) -> ForensicResult:
        """
        V10.0 Pipeline:
        1. Collect numbers (MultiLID, UFD)
        2. Get image description (BLIP)
        3. DeepSeek reads everything → score
        4. Binary decision → verdict
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"[PIPELINE V10.0] Starting analysis...")
        logger.info(f"[PIPELINE] Image: {image_path}")
        logger.info(f"{'='*60}\n")
        
        try:
            # === ETAPA 1: COLLECT NUMBERS (Peritos) ===
            logger.info("[STAGE 1: PERITOS] Collecting technical numbers...")
            
            # MultiLID
            logger.info("  [PERITO 1/2] MultiLID (Geometry)...")
            multilid_result = self.multilid.analyze(image_path)
            logger.info(f"  -> MultiLID Score: {multilid_result.score:.4f}")
            
            # UFD
            logger.info("  [PERITO 2/2] UFD (Noise)...")
            ufd_result = self.ufd.analyze(image_path)
            logger.info(f"  -> UFD Score: {ufd_result.score:.4f}")
            
            # Technical context for DeepSeek
            technical_context = {
                "multilid": multilid_result.score,
                "ufd": ufd_result.score
            }
            
            # === ETAPA 2: GET IMAGE DESCRIPTION (Vision) ===
            logger.info("\n[STAGE 2: VISION] Generating image description...")
            try:
                pil_image = Image.open(image_path).convert('RGB')
                inputs = self.blip_processor(pil_image, return_tensors="pt").to(self.device)
                outputs = self.blip_model.generate(**inputs, max_new_tokens=50)
                image_description = self.blip_processor.decode(outputs[0], skip_special_tokens=True)
                logger.info(f"  -> Description: {image_description}")
            except Exception as e:
                logger.warning(f"  -> BLIP failed: {e}")
                image_description = "imagen sin descripción"
            
            # === ETAPA 3: DEEPSEEK JUDGE (Doctor) ===
            logger.info("\n[STAGE 3: DOCTOR] DeepSeek reading numbers + description...")
            logger.info(f"  -> Input: MultiLID={technical_context['multilid']:.3f}, UFD={technical_context['ufd']:.3f}")
            logger.info(f"  -> Context: {image_description}")
            
            semantic_result = self.semantic.analyze(
                image_path,
                image_description=image_description,
                technical_context=technical_context
            )
            
            logger.info(f"  -> DeepSeek Score: {semantic_result.score:.4f}")
            logger.info(f"  -> Reasoning: {semantic_result.raw_data.get('reasoning', 'N/A')}")
            
            # === ETAPA 4: BINARY VERDICT (Sentencia) ===
            logger.info("\n[STAGE 4: SENTENCIA] Fusion Engine V10.0 rendering binary verdict...")
            logger.info("  -> Threshold: > 0.60 = IA, ≤ 0.60 = REAL")
            
            final_result = self.fusion.fuse(
                multilid_result=multilid_result,
                ufd_result=ufd_result,
                semantic_result=semantic_result
            )
            
            logger.info(f"\n{'='*60}")
            logger.info(f"[VERDICT] {final_result.verdict}")
            logger.info(f"[CONFIDENCE] {final_result.confidence}")
            logger.info(f"[SCORE] {final_result.scores.get('unified', 0):.4f}")
            logger.info(f"[NOTES] {final_result.notes}")
            logger.info(f"{'='*60}\n")
            
            return final_result
            
        except Exception as e:
            logger.error(f"[PIPELINE ERROR] {str(e)}", exc_info=True)
            # Safe fallback
            return ForensicResult(
                verdict="ERROR EN ANÁLISIS",
                confidence="N/A",
                scores={
                    "unified": 0.0,
                    "ai_probability": 0.0,
                    "real_probability": 0.0
                },
                evidence=[],
                notes=f"Error: {str(e)}"
            )
    
    def analyze(self, image_path: str, use_deepseek: bool = True) -> ForensicResult:
        """Public method for analysis."""
        return self.process(image_path)
