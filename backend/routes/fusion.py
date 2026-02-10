"""
Routes - Fusion Engine
POST /api/fusion

Endpoint para fusión de resultados de expertos.
"""

from flask import Blueprint, request, jsonify, current_app

from modules.image_forensics.fusion_engine import FusionEngine
from modules.image_forensics.schemas import ExpertResult


bp = Blueprint('fusion', __name__)


@bp.route('/fusion', methods=['POST'])
def fuse_results():
    """
    Fusiona resultados de expertos individuales.
    
    Request (JSON):
        {
            "multilid_result": {
                "score": 0.68,
                "confidence": 0.85,
                "evidence": [...]
            },
            "ufd_result": {
                "score": 0.72,
                "confidence": 0.78,
                "evidence": [...]
            },
            "semantic_result": {
                "score": 0.85,
                "confidence": 0.80,
                "evidence": [...]
            }
        }
        
    Response:
        {
            "status": "success",
            "verdict": "GENERADA POR IA",
            "confidence": "ALTA",
            "final_score": 0.75,
            "evidence": [...],
            "notes": "..."
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validar campos requeridos
        required = ['multilid_result', 'ufd_result']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing '{field}'"}), 400
        
        # Crear ExpertResult objects
        multilid_result = ExpertResult(
            name="multiLID",
            score=data['multilid_result']['score'],
            confidence=data['multilid_result']['confidence'],
            evidence=data['multilid_result'].get('evidence', [])
        )
        
        ufd_result = ExpertResult(
            name="UFD",
            score=data['ufd_result']['score'],
            confidence=data['ufd_result']['confidence'],
            evidence=data['ufd_result'].get('evidence', [])
        )
        
        # Semantic result (opcional)
        semantic_result = None
        if 'semantic_result' in data:
            semantic_result = ExpertResult(
                name="Semantic",
                score=data['semantic_result']['score'],
                confidence=data['semantic_result']['confidence'],
                evidence=data['semantic_result'].get('evidence', [])
            )
        
        # Fusionar
        fusion_engine = FusionEngine()
        result = fusion_engine.fuse(
            multilid_result=multilid_result,
            ufd_result=ufd_result,
            semantic_result=semantic_result
        )
        
        current_app.logger.info(f"Fusion result: {result.verdict}")
        
        return jsonify({
            "status": "success",
            "verdict": result.verdict,
            "confidence": result.confidence,
            "scores": result.scores,
            "evidence": result.evidence,
            "notes": result.notes
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Fusion error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
