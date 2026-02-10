"""
API Route: Analyze Image
Conecta el Frontend con el ForensicsPipeline V5.0.
"""
import os
import time
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from services.forensics_pipeline import ForensicsPipeline

# Logger
logger = logging.getLogger(__name__)
bp = Blueprint('analyze', __name__) # Usamos 'bp' para coincidir con tu app.py

# --- VARIABLE GLOBAL PARA EL PIPELINE ---
# Se iniciará solo una vez
pipeline_instance = None

def get_pipeline():
    """Singleton para obtener el pipeline cargado"""
    global pipeline_instance
    if pipeline_instance is None:
        logger.info("⚡ Iniciando Pipeline Forense V5.0 por primera vez...")
        pipeline_instance = ForensicsPipeline()
    return pipeline_instance

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/analyze_image', methods=['POST'])
def analyze_image():
    start_time = time.time()
    
    # 1. Obtener el pipeline (Cargará modelos si es la primera vez)
    try:
        pipeline = get_pipeline()
    except Exception as e:
        return jsonify({"error": f"Fallo al iniciar sistema: {str(e)}"}), 500

    # 2. Validaciones de archivo
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # 3. Guardar imagen
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(os.getcwd(), 'backend', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            # 4. EJECUTAR PIPELINE V5.0
            current_app.logger.info(f"[API] Procesando imagen: {filename}")
            result = pipeline.process(filepath)

            # 5. Guardar en base de datos
            try:
                from backend import database
                database.insert_analysis(filename, 'IMAGE', result.to_dict())
            except Exception as e:
                logger.warning(f"Error guardando en DB: {e}")

            # 6. Log final seguro (Sin emojis)
            processing_time = time.time() - start_time
            current_app.logger.info(f"[API] Respuesta: {result.verdict} ({processing_time:.2f}s)")

            return jsonify({
                "status": "success",
                "result": result.to_dict(),
                "processing_time": round(processing_time, 2)
            })

        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400
