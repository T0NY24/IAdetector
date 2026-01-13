"""
File Handlers - Validación de archivos y generación de reportes HTML
UIDE Forense AI

Este módulo contiene funciones para validar archivos multimedia
y generar reportes HTML con estilo profesional.
"""

import os
import time
import logging
from typing import Tuple

import config
from .plotting import generar_gauge_svg, generar_barra_progreso, generar_stat_card

logger = logging.getLogger(__name__)


# ==========================================
# 📊 Validación de Archivos
# ==========================================

def validar_imagen(imagen_array, tamaño_max_mb: int = config.MAX_IMAGE_SIZE_MB) -> Tuple[bool, str]:
    """
    Valida que una imagen cumpla los requisitos.
    
    Args:
        imagen_array: Array numpy de la imagen
        tamaño_max_mb: Tamaño máximo en MB
        
    Returns:
        Tupla (es_valida, mensaje_error)
    """
    try:
        if imagen_array is None:
            return False, "No se proporcionó ninguna imagen"
        
        # Validar dimensiones mínimas
        if imagen_array.shape[0] < 32 or imagen_array.shape[1] < 32:
            return False, "La imagen es demasiado pequeña (mínimo 32x32 píxeles)"
        
        # Validar dimensiones máximas (para evitar OOM)
        if imagen_array.shape[0] > 8192 or imagen_array.shape[1] > 8192:
            return False, "La imagen es demasiado grande (máximo 8192x8192 píxeles)"
        
        return True, ""
    except Exception as e:
        logger.error(f"Error validando imagen: {e}")
        return False, f"Error al validar imagen: {str(e)}"


def validar_video(video_path: str) -> Tuple[bool, str]:
    """
    Valida que un video cumpla los requisitos.
    
    Args:
        video_path: Ruta al archivo de video
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    try:
        if not os.path.exists(video_path):
            return False, "El archivo de video no existe"
        
        # Validar tamaño del archivo
        tamaño_mb = os.path.getsize(video_path) / (1024 * 1024)
        if tamaño_mb > config.MAX_VIDEO_SIZE_MB:
            return False, f"El video es demasiado grande ({tamaño_mb:.1f}MB). Máximo: {config.MAX_VIDEO_SIZE_MB}MB"
        
        # Validar extensión
        ext = os.path.splitext(video_path)[1].lower()
        if ext not in config.SUPPORTED_VIDEO_FORMATS:
            return False, f"Formato no soportado. Use: {', '.join(config.SUPPORTED_VIDEO_FORMATS)}"
        
        return True, ""
    except Exception as e:
        logger.error(f"Error validando video: {e}")
        return False, f"Error al validar video: {str(e)}"


def validar_audio(audio_path: str) -> Tuple[bool, str]:
    """
    Valida que un archivo de audio cumpla los requisitos.
    
    Args:
        audio_path: Ruta al archivo de audio
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    try:
        if not os.path.exists(audio_path):
            return False, "El archivo de audio no existe"
        
        # Validar tamaño del archivo
        tamaño_mb = os.path.getsize(audio_path) / (1024 * 1024)
        if tamaño_mb > config.MAX_AUDIO_SIZE_MB:
            return False, f"El audio es demasiado grande ({tamaño_mb:.1f}MB). Máximo: {config.MAX_AUDIO_SIZE_MB}MB"
        
        # Validar extensión
        ext = os.path.splitext(audio_path)[1].lower()
        if ext not in config.SUPPORTED_AUDIO_FORMATS:
            return False, f"Formato no soportado. Use: {', '.join(config.SUPPORTED_AUDIO_FORMATS)}"
        
        return True, ""
    except Exception as e:
        logger.error(f"Error validando audio: {e}")
        return False, f"Error al validar audio: {str(e)}"


# ==========================================
# 🎨 Generación de Reportes HTML
# ==========================================

def _determinar_estado(probabilidad: float, tipo: str = "imagen") -> Tuple[str, str, str, float]:
    """
    Determina el estado, color, icono y confianza visual basado en probabilidad.
    """
    if probabilidad > 60:
        # FAKE
        color = config.COLOR_FAKE
        icono = "🚨"
        diagnostico = "POSIBLE MANIPULACIÓN DETECTADA" if tipo == "imagen" else "DEEPFAKE DETECTADO"
        confianza_visual = probabilidad
    elif probabilidad > 40:
        # SOSPECHOSO
        color = config.COLOR_WARNING
        icono = "⚠️"
        diagnostico = "SOSPECHOSO / INCIERTO"
        confianza_visual = probabilidad
    else:
        # REAL
        color = config.COLOR_REAL
        icono = "✅"
        diagnostico = "CONTENIDO AUTÉNTICO" if tipo == "imagen" else "VIDEO AUTÉNTICO"
        confianza_visual = 100 - probabilidad

    return color, icono, diagnostico, confianza_visual


def generar_reporte_imagen(
    es_fake: bool, 
    probabilidad: float,
    ancho: int, 
    alto: int, 
    tiempo_proceso: float,
    origen_detectado: str = "N/A",
    gan_score: float = 0.0,
    diffusion_score: float = 0.0
) -> str:
    """
    Genera el reporte HTML completo para análisis de imagen.
    Ahora incluye información del ensamble GAN+Difusión.
    """
    # Usar lógica de 3 estados
    color, icono, diagnostico, confianza_visual = _determinar_estado(probabilidad, "imagen")
    
    gauge = generar_gauge_svg(confianza_visual, color)
    barra = generar_barra_progreso(confianza_visual, color)
    
    # Cards de estadísticas
    stats_html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0;">
        {generar_stat_card(f"{ancho}x{alto}", "Resolución", "🖼️")}
        {generar_stat_card(f"{tiempo_proceso:.2f}s", "Tiempo", "⚡")}
        {generar_stat_card(f"{confianza_visual:.1f}%", "Confianza", "🎯")}
    </div>
    """
    
    # Sección de ensamble
    ensemble_html = f"""
    <div style="background: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h4 style="margin-top: 0; color: #1f2937;">📊 Análisis de Ensamble</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div style="padding: 10px; background: rgba(255,255,255,0.5); border-radius: 6px;">
                <strong>Detector GAN:</strong> {gan_score:.1f}%
            </div>
            <div style="padding: 10px; background: rgba(255,255,255,0.5); border-radius: 6px;">
                <strong>Detector Difusión:</strong> {diffusion_score:.1f}%
            </div>
        </div>
        <p style="margin: 10px 0 0 0; font-size: 0.9em;">
            <strong>Origen probable:</strong> {origen_detectado}
        </p>
    </div>
    """ if gan_score > 0 or diffusion_score > 0 else ""
    
    return f"""
    <div style="background: linear-gradient(135deg, {color}15 0%, {color}05 100%); 
                padding: 30px; border-radius: 15px; border-left: 5px solid {color}; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.1); animation: slideIn 0.5s ease;">
        
        <h2 style="color: {color}; margin-top: 0; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5em;">{icono}</span>
            <span>Análisis de Imagen: {diagnostico}</span>
        </h2>
        
        <div style="display: flex; align-items: center; justify-content: center; margin: 30px 0;">
            {gauge}
        </div>
        
        {barra}
        {stats_html}
        {ensemble_html}
        
        <div style="background: rgba(255,255,255,0.5); padding: 20px; border-radius: 10px; margin-top: 20px;">
            <h3 style="margin-top: 0; color: #1f2937;">🔍 Detalles Técnicos</h3>
            <ul style="line-height: 1.8; color: #374151;">
                <li><strong>Modelo:</strong> Ensamble GAN + Difusión (ResNet50 + ViT)</li>
                <li><strong>Método:</strong> Detección de artefactos de GANs y modelos de Difusión</li>
                <li><strong>Resolución analizada:</strong> {ancho} × {alto} píxeles</li>
                <li><strong>Tiempo de procesamiento:</strong> {tiempo_proceso:.3f} segundos</li>
            </ul>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: rgba(59, 130, 246, 0.1); 
                    border-radius: 8px; border-left: 3px solid #3b82f6;">
            <p style="margin: 0; font-size: 0.9em; color: #1f2937;">
                ℹ️ <strong>Nota:</strong> Este análisis es probabilístico y debe ser verificado por un experto forense. 
                Los resultados pueden variar según la calidad y origen de la imagen.
            </p>
        </div>
    </div>
    
    <style>
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    """


def generar_reporte_video(
    es_deepfake: bool, 
    probabilidad: float,
    frames_totales: int, 
    frames_analizados: int,
    duracion: float, 
    tiempo_proceso: float
) -> str:
    """
    Genera el reporte HTML completo para análisis de video.
    """
    # Usar lógica de 3 estados
    color, icono, diagnostico, confianza_visual = _determinar_estado(probabilidad, "video")
    
    gauge = generar_gauge_svg(confianza_visual, color)
    barra = generar_barra_progreso(confianza_visual, color)
    
    # Cards de estadísticas
    stats_html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0;">
        {generar_stat_card(f"{duracion:.1f}s", "Duración", "🎬")}
        {generar_stat_card(frames_analizados, "Rostros", "👤")}
        {generar_stat_card(f"{tiempo_proceso:.1f}s", "Tiempo", "⚡")}
        {generar_stat_card(f"{confianza_visual:.1f}%", "Confianza", "🎯")}
    </div>
    """
    
    return f"""
    <div style="background: linear-gradient(135deg, {color}15 0%, {color}05 100%); 
                padding: 30px; border-radius: 15px; border-left: 5px solid {color}; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.1); animation: slideIn 0.5s ease;">
        
        <h2 style="color: {color}; margin-top: 0; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5em;">{icono}</span>
            <span>Análisis de Video: {diagnostico}</span>
        </h2>
        
        <div style="display: flex; align-items: center; justify-content: center; margin: 30px 0;">
            {gauge}
        </div>
        
        {barra}
        {stats_html}
        
        <div style="background: rgba(255,255,255,0.5); padding: 20px; border-radius: 10px; margin-top: 20px;">
            <h3 style="margin-top: 0; color: #1f2937;">📹 Análisis Forense</h3>
            <ul style="line-height: 1.8; color: #374151;">
                <li><strong>Modelo:</strong> XceptionNet (Pre-entrenado en FaceForensics++)</li>
                <li><strong>Método:</strong> Análisis de consistencia facial frame-a-frame</li>
                <li><strong>Frames totales:</strong> {frames_totales}</li>
                <li><strong>Rostros detectados:</strong> {frames_analizados}</li>
                <li><strong>Tasa de muestreo:</strong> 1 frame cada {config.VIDEO_FRAME_STRIDE} frames</li>
                <li><strong>Tiempo total:</strong> {tiempo_proceso:.2f} segundos</li>
            </ul>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: rgba(59, 130, 246, 0.1); 
                    border-radius: 8px; border-left: 3px solid #3b82f6;">
            <p style="margin: 0; font-size: 0.9em; color: #1f2937;">
                ℹ️ <strong>Nota:</strong> El análisis de videos es computacionalmente intensivo. 
                Se utiliza muestreo inteligente para optimizar el rendimiento manteniendo la precisión.
            </p>
        </div>
    </div>
    
    <style>
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    """


def generar_reporte_audio(
    es_sintetico: bool,
    probabilidad: float,
    duracion: float,
    tiempo_proceso: float
) -> str:
    """
    Genera el reporte HTML completo para análisis de audio.
    """
    # Determinar estado
    if probabilidad > 60:
        color = config.COLOR_FAKE
        icono = "🚨"
        diagnostico = "AUDIO SINTÉTICO DETECTADO"
        confianza_visual = probabilidad
    elif probabilidad > 40:
        color = config.COLOR_WARNING
        icono = "⚠️"
        diagnostico = "AUDIO SOSPECHOSO"
        confianza_visual = probabilidad
    else:
        color = config.COLOR_REAL
        icono = "✅"
        diagnostico = "VOZ HUMANA AUTÉNTICA"
        confianza_visual = 100 - probabilidad
    
    gauge = generar_gauge_svg(confianza_visual, color)
    barra = generar_barra_progreso(confianza_visual, color)
    
    # Cards de estadísticas
    stats_html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0;">
        {generar_stat_card(f"{duracion:.1f}s", "Duración", "🔊")}
        {generar_stat_card(f"{tiempo_proceso:.2f}s", "Tiempo", "⚡")}
        {generar_stat_card(f"{confianza_visual:.1f}%", "Confianza", "🎯")}
    </div>
    """
    
    return f"""
    <div style="background: linear-gradient(135deg, {color}15 0%, {color}05 100%); 
                padding: 30px; border-radius: 15px; border-left: 5px solid {color}; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.1); animation: slideIn 0.5s ease;">
        
        <h2 style="color: {color}; margin-top: 0; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5em;">{icono}</span>
            <span>Análisis de Audio: {diagnostico}</span>
        </h2>
        
        <div style="display: flex; align-items: center; justify-content: center; margin: 30px 0;">
            {gauge}
        </div>
        
        {barra}
        {stats_html}
        
        <div style="background: rgba(255,255,255,0.5); padding: 20px; border-radius: 10px; margin-top: 20px;">
            <h3 style="margin-top: 0; color: #1f2937;">🎤 Análisis Forense de Voz</h3>
            <ul style="line-height: 1.8; color: #374151;">
                <li><strong>Modelo:</strong> Wav2Vec2 / Audio Classification (HuggingFace)</li>
                <li><strong>Método:</strong> Análisis espectral y características de voz</li>
                <li><strong>Duración analizada:</strong> {duracion:.2f} segundos</li>
                <li><strong>Sample Rate:</strong> {config.AUDIO_SAMPLE_RATE} Hz</li>
                <li><strong>Detección de:</strong> ElevenLabs, RVC, TTS, Clonación de voz</li>
            </ul>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: rgba(59, 130, 246, 0.1); 
                    border-radius: 8px; border-left: 3px solid #3b82f6;">
            <p style="margin: 0; font-size: 0.9em; color: #1f2937;">
                ℹ️ <strong>Nota:</strong> El análisis de audio detecta voces generadas por IA 
                incluyendo sistemas TTS modernos y clonación de voz. Los resultados son probabilísticos.
            </p>
        </div>
    </div>
    
    <style>
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    """


def generar_reporte_error(mensaje: str, tipo: str = "error") -> str:
    """Genera un reporte de error con estilo."""
    colores = {
        "error": ("#ef4444", "❌"),
        "warning": ("#f59e0b", "⚠️"),
        "info": ("#3b82f6", "ℹ️")
    }
    color, icono = colores.get(tipo, colores["error"])
    
    return f"""
    <div style="background: {color}15; padding: 25px; border-radius: 12px; 
                border-left: 5px solid {color}; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h3 style="color: {color}; margin-top: 0; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5em;">{icono}</span>
            <span>{"Error" if tipo == "error" else "Aviso"}</span>
        </h3>
        <p style="font-size: 1.1em; color: #1f2937; margin: 10px 0;">{mensaje}</p>
    </div>
    """


# ==========================================
# ⏱️ Utilidades de Tiempo
# ==========================================

def formatear_tiempo(segundos: float) -> str:
    """Formatea segundos a formato legible."""
    if segundos < 1:
        return f"{segundos*1000:.0f}ms"
    elif segundos < 60:
        return f"{segundos:.2f}s"
    else:
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos}m {segs}s"


class Timer:
    """Context manager para medir tiempo de ejecución."""
    
    def __init__(self):
        self.inicio = None
        self.fin = None
        
    def __enter__(self):
        self.inicio = time.time()
        return self
        
    def __exit__(self, *args):
        self.fin = time.time()
        
    @property
    def duracion(self) -> float:
        if self.inicio and self.fin:
            return self.fin - self.inicio
        return 0.0
