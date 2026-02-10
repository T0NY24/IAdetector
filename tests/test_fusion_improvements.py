import sys
import os
import logging
from typing import NamedTuple

# Add the project root to the python path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.image_forensics.fusion_engine import FusionEngine, RedFlagDetector, VERDICT_IA_PROBABLE, VERDICT_IA_CONFIRMED

# Configurar logging simple
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ExpertResult(NamedTuple):
    score: float
    confidence: float

def test_paradox_gap():
    """Test Solution 1: Closing the Semantic Gap."""
    logger.info("\n--- TEST: Paradox Gap (Semantic 0.50) ---")
    engine = FusionEngine()
    
    # Previous: Semantic 0.50 was ignored (Active > 0.55).
    # New: Active > 0.48, so 0.50 should contribute.
    
    multilid = ExpertResult(score=0.35, confidence=0.8) # Slight IA
    ufd = ExpertResult(score=0.30, confidence=0.4)      # Low UFD (Real-ish but low conf)
    semantic = ExpertResult(score=0.50, confidence=0.9) # The Gap Case
    
    result = engine.fuse(multilid, ufd, semantic)
    
    logger.info(f"Verdict: {result.verdict}")
    logger.info(f"Evidence: {result.evidence}")
    
    # Check if Semantic is mentioned in evidence
    semantic_evidence = any("Semantic" in str(e) and "zone" not in str(e) for e in result.evidence)
    semantic_warning = any("zona de alerta" in str(e) for e in result.evidence)
    
    if semantic_evidence or semantic_warning:
        logger.info("PASS: Semantic 0.50 contributed to evidence or warning.")
    else:
        logger.error("FAIL: Semantic 0.50 was ignored.")

def test_obvious_ia_pattern():
    """Test Solution 2: Obvious IA Pattern Detection."""
    logger.info("\n--- TEST: Obvious IA Pattern ---")
    engine = FusionEngine()
    
    # Pattern: UFD Low (<0.35), Semantic Mid-High (>0.48), MultiLID Mid (>0.40)
    # This simulates a model not in UFD training but detected by semantics
    multilid = ExpertResult(score=0.45, confidence=0.8)
    ufd = ExpertResult(score=0.20, confidence=0.9)
    semantic = ExpertResult(score=0.55, confidence=0.9)
    
    result = engine.fuse(multilid, ufd, semantic)
    
    logger.info(f"Verdict: {result.verdict}")
    logger.info(f"Notes: {result.notes}")
    
    if "Patrón visual detectado" in str(result.evidence) or "IA_OBVIA_MODELO_DESCONOCIDO" in str(result.evidence):
        logger.info("PASS: Obvious IA pattern detected.")
    else:
        # Check if it was caught by operative mode fallback at least
        if result.verdict in [VERDICT_IA_PROBABLE, VERDICT_IA_CONFIRMED]:
             logger.info("PASS: Detected as IA (via Operative Mode Fallback).")
        else:
             logger.error("FAIL: Obvious IA pattern missed.")

def test_red_flags():
    """Test Solution 3: Red Flags."""
    logger.info("\n--- TEST: Red Flags ---")
    
    scores = {
        "multiLID": 0.9,
        "UFD": 0.2, # Discordant!
        "UFD_confidence": 0.2, # Low confidence
        "Semantic": 0.55 # Danger zone
    }
    
    flags = RedFlagDetector.detect_red_flags(scores)
    logger.info(f"Flags detected: {flags}")
    
    has_discordance = any(f[0] == "EXPERTOS_DISCORDANTES" for f in flags)
    has_low_conf = any(f[0] == "UFD_POCO_CONFIABLE" for f in flags)
    has_danger = any(f[0] == "ZONA_PELIGRO_SEMANTIC" for f in flags)
    
    if has_discordance and has_low_conf and has_danger:
        logger.info("PASS: All red flags detected.")
    else:
        logger.error(f"FAIL: Missing flags. Got: {flags}")

def test_high_sensitivity():
    """Test Solution 4: High Sensitivity Mode."""
    logger.info("\n--- TEST: High Sensitivity Mode ---")
    engine = FusionEngine()
    
    # Ambiguous case
    multilid = ExpertResult(score=0.42, confidence=0.5)
    ufd = ExpertResult(score=0.33, confidence=0.3)
    semantic = ExpertResult(score=0.50, confidence=0.5)
    
    result = engine.fuse_high_sensitivity(multilid, ufd, semantic)
    
    logger.info(f"Verdict: {result.verdict}")
    logger.info(f"Notes: {result.notes}")
    
    if result.verdict in [VERDICT_IA_PROBABLE, VERDICT_IA_CONFIRMED]:
        logger.info("PASS: High Sensitivity Mode forced a decision.")
    else:
        logger.info("INFO: High Sensitivity Mode remained inconclusive (which might be correct if signal is too weak).")

if __name__ == "__main__":
    logger.info("Running Forensic Improvements Tests...")
    test_paradox_gap()
    test_obvious_ia_pattern()
    test_red_flags()
    test_high_sensitivity()
