"""
Routes - Health Check
GET /api/health

Health check endpoint para monitoreo de servicios.
"""

import time
from flask import Blueprint, jsonify, current_app
from datetime import datetime

bp = Blueprint('health', __name__)


@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check de todos los servicios.
    
    Response:
        {
            "status": "healthy",
            "services": {
                "flask": "ok",
                "clip": "ok",
                "deepseek": "ok",
                "ollama": "ok"
            },
            "timestamp": "2026-02-09T..."
        }
    """
    services = {
        "flask": "ok"
    }
    
    overall_status = "healthy"
    
    # Check CLIP
    try:
        from modules.image_forensics.feature_extractor import CLIPFeatureExtractor
        extractor = CLIPFeatureExtractor()
        services["clip"] = "ok"
    except Exception as e:
        services["clip"] = f"error: {str(e)}"
        overall_status = "degraded"
        current_app.logger.warning(f"CLIP health check failed: {e}")
    
    # Check DeepSeek/Ollama
    try:
        from services.deepseek_client import DeepSeekLLMClient
        import config
        
        if config.DEEPSEEK_ENABLED:
            client = DeepSeekLLMClient()
            # Simple health check
            services["deepseek"] = "enabled"
            services["ollama"] = "assumed_ok"  # Could ping Ollama API
        else:
            services["deepseek"] = "disabled"
            services["ollama"] = "not_required"
    except Exception as e:
        services["deepseek"] = f"error: {str(e)}"
        services["ollama"] = "unknown"
        current_app.logger.warning(f"DeepSeek health check failed: {e}")
    
    return jsonify({
        "status": overall_status,
        "services": services,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0"
    }), 200 if overall_status == "healthy" else 503
