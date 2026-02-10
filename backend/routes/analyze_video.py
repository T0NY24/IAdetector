"""
API Route: Analyze Video
Detección de deepfakes en videos usando XceptionNet.
"""
import os
import time
import logging
import sys
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

# Agregar directorio padre al path para importar modules
root_path = str(Path(__file__).parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from modules.video_forensics import VideoForensicsDetector
import config

logger = logging.getLogger(__name__)
bp = Blueprint('analyze_video', __name__)

# Singleton para el detector
detector_instance = None

def get_detector():
    global detector_instance
    if detector_instance is None:
        logger.info("⚡ Iniciando Video Forensics Detector...")
        detector_instance = VideoForensicsDetector()
    return detector_instance

def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = '.' + filename.rsplit('.', 1)[1].lower()
    return ext in config.SUPPORTED_VIDEO_FORMATS

@bp.route('/analyze_video', methods=['POST'])
def analyze_video():
    start_time = time.time()
    
    # Obtener detector
    try:
        detector = get_detector()
    except Exception as e:
        logger.error(f"Error inicializando detector: {e}")
        return jsonify({"error": f"Fallo al iniciar detector: {str(e)}"}), 500

    # Validación
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Supported formats: {', '.join(config.SUPPORTED_VIDEO_FORMATS)}"}), 400

    try:
        # Guardar video
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(os.getcwd(), 'backend', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Verificar tamaño
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if file_size_mb > config.MAX_VIDEO_SIZE_MB:
            os.remove(filepath)
            return jsonify({"error": f"Video too large ({file_size_mb:.1f}MB). Maximum: {config.MAX_VIDEO_SIZE_MB}MB"}), 400
        
        # Analizar
        current_app.logger.info(f"[API] Procesando video: {filename} ({file_size_mb:.1f}MB)")
        result = detector.predict(filepath)
        
        # Guardar en base de datos
        try:
            from backend import database
            database.insert_analysis(filename, 'VIDEO', result)
        except Exception as e:
            logger.warning(f"Error guardando en DB: {e}")
        
        # Limpiar archivo temporal
        try:
            os.remove(filepath)
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo temporal: {e}")

        processing_time = time.time() - start_time
        current_app.logger.info(f"[API] Video analizado: {result.get('verdict', 'UNKNOWN')} ({processing_time:.2f}s)")

        return jsonify({
            "status": "success",
            "result": result,
            "processing_time": round(processing_time, 2)
        })

    except Exception as e:
        logger.error(f"Error procesando video: {e}", exc_info=True)
        # Intentar limpiar archivo si existe
        try:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass
        return jsonify({"error": str(e)}), 500
