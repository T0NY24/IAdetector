"""
Routes - Upload
POST /api/upload

Endpoint para subir imágenes.
"""

import os
import time
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from PIL import Image

bp = Blueprint('upload', __name__)


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    from config import ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Sube una imagen para análisis posterior.
    
    Response:
        {
            "status": "success",
            "filename": "image_123.jpg",
            "path": "/uploads/image_123.jpg",
            "size": 2048576,
            "format": "JPEG"
        }
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        
        from config import UPLOAD_FOLDER
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Obtener info de imagen
        image = Image.open(filepath)
        
        current_app.logger.info(f"File uploaded: {filename}")
        
        return jsonify({
            "status": "success",
            "filename": filename,
            "path": filepath,
            "size": os.path.getsize(filepath),
            "format": image.format,
            "dimensions": {
                "width": image.width,
                "height": image.height
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Upload error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
