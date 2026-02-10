"""
Flask Backend - UIDE Forense AI 3.0+
Application Factory

Migración de Grad io a Flask + React con DeepSeek-R1 integrado.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from datetime import datetime

import sys
from pathlib import Path

# Agregar directorio padre al path para importar config
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

# Importar configuración
import config

# Importar rutas
from routes import analyze, semantic, fusion, health, upload


def create_app(config_name='default'):
    """
    Application Factory para Flask.
    
    Args:
        config_name: Nombre de la configuración a usar
        
    Returns:
        Flask app configurada
    """
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object(config)
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB max upload
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    
    # CORS (permitir requests desde React frontend)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],  # Vite/React dev servers
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Logging
    setup_logging(app)
    
    # Crear directorios necesarios
    ensure_directories()
    
    # Inicializar base de datos
    from backend import database
    try:
        database.init_db()
        app.logger.info("✅ Database initialized")
    except Exception as e:
        app.logger.error(f"❌ Database initialization failed: {e}")
    
    # Registrar blueprints (rutas)
    register_blueprints(app)
    
    # Error handlers
    register_error_handlers(app)
    
    # Request logging
    @app.before_request
    def log_request():
        app.logger.info(f"Request: {request.method} {request.path}")
    
    @app.after_request
    def log_response(response):
        app.logger.info(f"Response: {response.status_code}")
        return response
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            "message": "UIDE Forense AI 3.0+ Backend",
            "version": "3.0.0",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    app.logger.info("UIDE Forense AI backend initialized")
    
    return app


def setup_logging(app):
    """Configurar logging de la aplicación."""
    if not app.debug:
        # Crear directorio de logs
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'))
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('UIDE Forense AI startup')


def ensure_directories():
    """Crear directorios necesarios si no existen."""
    directories = [
        config.UPLOAD_FOLDER,
        os.path.join(os.path.dirname(__file__), 'logs')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def register_blueprints(app):
    """Registrar blueprints de rutas."""
    app.register_blueprint(health.bp, url_prefix='/api')
    app.register_blueprint(upload.bp, url_prefix='/api')
    app.register_blueprint(analyze.bp, url_prefix='/api')
    
    # Semantic Blueprint (prefix defined in bp)
    from routes.semantic import bp as semantic_bp
    app.register_blueprint(semantic_bp)
    
    app.register_blueprint(fusion.bp, url_prefix='/api')
    
    # Video and Audio routes
    from routes.analyze_video import bp as video_bp
    from routes.analyze_audio import bp as audio_bp
    app.register_blueprint(video_bp, url_prefix='/api')
    app.register_blueprint(audio_bp, url_prefix='/api')
    
    # History route
    from routes.history import bp as history_bp
    app.register_blueprint(history_bp, url_prefix='/api')


def register_error_handlers(app):
    """Registrar manejadores de errores."""
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Endpoint not found"}, 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad request"}, 400
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {error}")
        return {"error": "Internal server error"}, 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return {"error": "File too large. Maximum size is 20MB"}, 413


if __name__ == '__main__':
    from flask import request
    
    app = create_app()
    
    # Modo desarrollo
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
