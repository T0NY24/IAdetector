import sys
import os
import logging
from typing import NamedTuple

# Add the project root to the python path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.image_forensics.fusion_engine import FusionEngine, VERDICT_IA_CONFIRMED, VERDICT_IA_PROBABLE, VERDICT_INCONCLUSIVE

# Configurar logging simple
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ExpertResult(NamedTuple):
    score: float
    confidence: float

def test_semantic_threshold():
    """Test: Semantic > 0.50 triggers GENERADA POR IA"""
    logger.info("\n--- TEST: Semantic > 0.50 ---")
    engine = FusionEngine()
    
    # Case: Semantic 0.51 (just above threshold)
    multilid = ExpertResult(score=0.2, confidence=0.8) 
    ufd = ExpertResult(score=0.2, confidence=0.8)
    semantic = ExpertResult(score=0.51, confidence=0.9)
    
    result = engine.fuse(multilid, ufd, semantic)
    
    logger.info(f"Verdict: {result.verdict}")
    logger.info(f"Evidence: {result.evidence}")
    
    if result.verdict == VERDICT_IA_CONFIRMED:
        logger.info("PASS: Semantic 0.51 triggered GENERADA POR IA.")
    else:
        logger.error(f"FAIL: Expected GENERADA POR IA, got {result.verdict}")

def test_combined_score_probable():
    """Test: Combined Score >= 0.50 triggers PROBABLEMENTE GENERADA POR IA"""
    logger.info("\n--- TEST: Combined Score >= 0.50 ---")
    engine = FusionEngine()
    
    # Case: Combined score should be around 0.50
    # Formula: 0.45 * semantic + 0.35 * ufd_effective + 0.20 * multilid
    # Let's try to hit exactly 0.50
    # Semantic 0.49 (below confirmed threshold), UFD 0.4, MultiLID 0.7
    # 0.45*0.49 + 0.35*0.4*1.0 + 0.20*0.7 = 0.2205 + 0.14 + 0.14 = 0.5005
    
    multilid = ExpertResult(score=0.7, confidence=0.9) 
    ufd = ExpertResult(score=0.4, confidence=1.0)
    semantic = ExpertResult(score=0.49, confidence=0.9)
    
    result = engine.fuse(multilid, ufd, semantic)
    
    logger.info(f"Verdict: {result.verdict}")
    logger.info(f"Scores: {result.scores}")
    
    if result.verdict == VERDICT_IA_PROBABLE:
        logger.info("PASS: Combined score >= 0.50 triggered PROBABLEMENTE GENERADA POR IA.")
    else:
        logger.error(f"FAIL: Expected PROBABLEMENTE GENERADA POR IA, got {result.verdict}")

def test_combined_score_inconclusive():
    """Test: Combined Score < 0.50 triggers SE REQUIERE ANALISIS POR UN TECNICO"""
    logger.info("\n--- TEST: Combined Score < 0.50 ---")
    engine = FusionEngine()
    
    # Case: Combined score just below 0.50
    # Semantic 0.40, UFD 0.40, MultiLID 0.40
    # 0.45*0.40 + 0.35*0.40 + 0.20*0.40 = 0.40
    
    multilid = ExpertResult(score=0.40, confidence=0.9) 
    ufd = ExpertResult(score=0.40, confidence=1.0)
    semantic = ExpertResult(score=0.40, confidence=0.9)
    
    result = engine.fuse(multilid, ufd, semantic)
    
    logger.info(f"Verdict: {result.verdict}")
    logger.info(f"Scores: {result.scores}")
    
    if result.verdict == VERDICT_INCONCLUSIVE:
        logger.info(f"PASS: Low score triggered {VERDICT_INCONCLUSIVE}.")
    else:
        logger.error(f"FAIL: Expected SE REQUIERE ANALISIS POR UN TECNICO, got {result.verdict}")

def test_verdict_text():
    """Test: Check if VERDICT_INCONCLUSIVE text is correct"""
    logger.info("\n--- TEST: INCONCLUSIVE Text ---")
    expected = "SE REQUIERE ANALISIS POR UN TECNICO"
    if VERDICT_INCONCLUSIVE == expected:
        logger.info(f"PASS: Verdict text is '{VERDICT_INCONCLUSIVE}'")
    else:
        logger.error(f"FAIL: Verdict text is '{VERDICT_INCONCLUSIVE}', expected '{expected}'")

if __name__ == "__main__":
    logger.info("Running Verdict Update Tests...")
    test_verdict_text()
    test_semantic_threshold()
    test_combined_score_probable()
    test_combined_score_inconclusive()
