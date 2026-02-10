"""
UIDE Forense AI - Sistema de Detección de Contenido Sintético
Clean Architecture - Interfaz Gradio v3.0+

Este archivo contiene ÚNICAMENTE la interfaz de usuario.
Toda la lógica de decisión proviene de los detectores en modules/.

Módulo de imágenes v3.0+:
- multiLID (análisis geométrico)
- UFD (clasificador visual)
- Semantic Expert (plausibilidad semántica)
- Fusion Engine (decisión jerárquica)
"""

import logging
from typing import Optional, Tuple
from PIL import Image

import gradio as gr

# Importar configuración
import config

# Importar módulos de análisis
from modules.image_forensics import ImageForensicsDetector
from modules.video_forensics import VideoForensicsDetector
from modules.audio_forensics import AudioForensicsDetector

# Importar utilidades
from utils.file_handlers import (
    validar_imagen, 
    validar_video,
    validar_audio,
    generar_reporte_video,
    generar_reporte_audio,
    generar_reporte_error,
    Timer,
)
from utils.plotting import generar_grafico_temporal

# ==========================================
# 🔧 Configuración de Logging
# ==========================================
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

# ==========================================
# 🧠 Inicialización de Detectores
# ==========================================
logger.info("=" * 60)
logger.info("🚀 UIDE Forense AI 3.0+ - Iniciando Sistema")
logger.info("=" * 60)

# Los modelos se cargan bajo demanda (lazy loading)
image_detector = ImageForensicsDetector()
video_detector = VideoForensicsDetector()
audio_detector = AudioForensicsDetector()

logger.info("✅ Detectores inicializados (modelos: lazy loading)")


# ==========================================
# 🎨 Generación de Reportes HTML
# ==========================================

def generar_reporte_imagen_forense(resultado: dict, ancho: int, alto: int, tiempo: float) -> str:
    """
    Genera un reporte HTML forense detallado para el análisis de imagen.
    
    Args:
        resultado: Dict retornado por detector.analyze_dict()
        ancho: Ancho de la imagen
        alto: Alto de la imagen
        tiempo: Tiempo de procesamiento
        
    Returns:
        HTML formateado para Gradio
    """
    verdict = resultado.get("verdict", "ERROR")
    confidence = resultado.get("confidence", "N/A")
    scores = resultado.get("scores", {})
    evidence = resultado.get("evidence", [])
    notes = resultado.get("notes", "")
    
    # Determinar color y emoji según veredicto
    if "IA" in verdict or "GENERADA" in verdict:
        color = "#ef4444"  # Rojo
        emoji = "🚨"
        bg_color = "#fef2f2"
        border_color = "#fca5a5"
    elif "REAL" in verdict:
        color = "#22c55e"  # Verde
        emoji = "✅"
        bg_color = "#f0fdf4"
        border_color = "#86efac"
    elif "NO CONCLUYENTE" in verdict:
        color = "#f59e0b"  # Ámbar
        emoji = "⚠️"
        bg_color = "#fffbeb"
        border_color = "#fcd34d"
    else:
        color = "#6b7280"  # Gris
        emoji = "❓"
        bg_color = "#f9fafb"
        border_color = "#d1d5db"
    
    # Generar barras de scores
    scores_html = ""
    for expert, score in scores.items():
        percent = score * 100
        bar_color = "#ef4444" if percent > 50 else "#22c55e"
        scores_html += f"""
        <div style="margin: 8px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-weight: 500;">{expert}</span>
                <span style="font-weight: 600; color: {bar_color};">{percent:.1f}%</span>
            </div>
            <div style="background: #e5e7eb; border-radius: 4px; height: 8px; overflow: hidden;">
                <div style="background: {bar_color}; height: 100%; width: {percent}%; transition: width 0.3s;"></div>
            </div>
        </div>
        """
    
    # Generar lista de evidencia
    evidence_html = ""
    for item in evidence:
        evidence_html += f'<li style="margin: 4px 0; color: #374151;">{item}</li>'
    
    html = f"""
    <div style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; max-width: 600px;">
        
        <!-- Header con veredicto -->
        <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 12px; padding: 20px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 2.5em;">{emoji}</span>
                <div>
                    <h2 style="margin: 0; color: {color}; font-size: 1.4em;">{verdict}</h2>
                    <p style="margin: 4px 0 0 0; color: #6b7280;">Confianza: <strong>{confidence}</strong></p>
                </div>
            </div>
        </div>
        
        <!-- Scores de expertos -->
        <div style="background: #f9fafb; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
            <h3 style="margin: 0 0 12px 0; color: #1f2937; font-size: 1.1em;">📊 Análisis por Experto</h3>
            {scores_html}
        </div>
        
        <!-- Evidencia forense -->
        <div style="background: #f9fafb; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
            <h3 style="margin: 0 0 12px 0; color: #1f2937; font-size: 1.1em;">🔍 Evidencia Forense</h3>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.95em;">
                {evidence_html}
            </ul>
        </div>
        
        <!-- Notas -->
        <div style="background: #eff6ff; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
            <h3 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1em;">💡 Interpretación</h3>
            <p style="margin: 0; color: #1e3a8a; font-size: 0.95em;">{notes}</p>
        </div>
        
        <!-- Metadatos -->
        <div style="display: flex; gap: 16px; flex-wrap: wrap; font-size: 0.85em; color: #6b7280;">
            <span>📐 {ancho} × {alto} px</span>
            <span>⏱️ {tiempo:.2f}s</span>
            <span>🔬 Módulo v3.0+</span>
        </div>
        
    </div>
    """
    
    return html


# ==========================================
# 🔍 Funciones de Análisis
# ==========================================

def analizar_imagen(imagen_input) -> str:
    """
    Analiza una imagen usando el detector forense v3.0+.
    
    Pipeline:
    1. Validar entrada
    2. Llamar a detector.analyze_dict()
    3. Generar reporte HTML forense
    
    NO contiene lógica de decisión - todo viene del detector.
    """
    logger.info("📸 Solicitud de análisis de imagen recibida")
    
    # Validación de entrada
    if imagen_input is None:
        return generar_reporte_error("No se proporcionó ninguna imagen", "warning")
    
    es_valida, mensaje = validar_imagen(imagen_input)
    if not es_valida:
        return generar_reporte_error(mensaje, "error")
    
    try:
        with Timer() as timer:
            # Análisis con el detector v3.0+ (toda la lógica está aquí)
            resultado = image_detector.analyze_dict(imagen_input)
        
        # Obtener dimensiones
        if hasattr(imagen_input, 'shape'):
            alto, ancho = imagen_input.shape[:2]
        else:
            ancho, alto = imagen_input.size
        
        # Generar reporte forense explicable
        return generar_reporte_imagen_forense(
            resultado=resultado,
            ancho=ancho,
            alto=alto,
            tiempo=timer.duracion,
        )
        
    except Exception as e:
        logger.error(f"❌ Error en análisis de imagen: {e}", exc_info=True)
        return generar_reporte_error(f"Error durante el análisis: {str(e)}", "error")


def analizar_video(video_path: str, progress=gr.Progress()) -> Tuple[str, str, Optional[Image.Image], Optional[Image.Image]]:
    """
    Analiza un video para detectar deepfakes.
    """
    logger.info("🎬 Solicitud de análisis de video recibida")
    
    log_text = "🚀 Iniciando proceso..."
    
    if video_path is None:
        yield generar_reporte_error("No se proporcionó ningún video", "warning"), "❌ Error: Sin video", None, None
        return
    
    es_valido, mensaje = validar_video(video_path)
    if not es_valido:
        yield generar_reporte_error(mensaje, "error"), f"❌ Error: {mensaje}", None, None
        return
    
    try:
        with Timer() as timer:
            resultado_final = None
            for resultado in video_detector.predict(video_path, progress):
                if resultado["status"] == "error":
                    yield generar_reporte_error(resultado["message"], "error"), resultado["message"], None, None
                    return
                elif resultado["status"] == "complete":
                    resultado_final = resultado
                else:
                    log_text += f"\n{resultado['message']}"
                    yield "", log_text, None, None
        
        if resultado_final is None:
            yield generar_reporte_error("No se obtuvo resultado", "error"), "❌ Error inesperado", None, None
            return
        
        timeline_plot = generar_grafico_temporal(resultado_final.get("predictions", []))
        
        reporte_html = generar_reporte_video(
            es_deepfake=resultado_final["is_deepfake"],
            probabilidad=resultado_final["probability"],
            frames_totales=resultado_final["frames_total"],
            frames_analizados=resultado_final["frames_analyzed"],
            duracion=resultado_final["duration"],
            tiempo_proceso=timer.duracion,
        )
        
        final_log = log_text + f"\n🏁 Completado: {'DEEPFAKE' if resultado_final['is_deepfake'] else 'REAL'} ({resultado_final['probability']:.1f}%)"
        
        yield reporte_html, final_log, timeline_plot, resultado_final.get("culprit_frame")
        
    except Exception as e:
        logger.error(f"❌ Error en video: {e}", exc_info=True)
        yield generar_reporte_error(str(e), "error"), f"❌ Error crítico: {str(e)}", None, None


def analizar_audio(audio_path: str) -> str:
    """
    Analiza un archivo de audio para detectar si es sintético.
    """
    logger.info("🔊 Solicitud de análisis de audio recibida")
    
    if audio_path is None:
        return generar_reporte_error("No se proporcionó ningún archivo de audio", "warning")
    
    es_valido, mensaje = validar_audio(audio_path)
    if not es_valido:
        return generar_reporte_error(mensaje, "error")
    
    try:
        with Timer() as timer:
            resultado = audio_detector.predict(audio_path)
        
        if "error" in resultado and resultado.get("verdict") == "ERROR":
            return generar_reporte_error(resultado["error"], "error")
        
        return generar_reporte_audio(
            es_sintetico=resultado["score"] > 50,
            probabilidad=resultado["score"],
            duracion=resultado.get("duration_analyzed", 0),
            tiempo_proceso=timer.duracion,
        )
        
    except Exception as e:
        logger.error(f"❌ Error en análisis de audio: {e}", exc_info=True)
        return generar_reporte_error(f"Error durante el análisis: {str(e)}", "error")


# ==========================================
# 🖥️ Interfaz Gradio
# ==========================================

css_custom = """
.gradio-container { 
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
}
.tab-nav button {
    font-size: 1.1em !important;
}
"""

with gr.Blocks(title="UIDE Forense AI 3.0+") as demo:
    gr.HTML(f"<style>{css_custom}</style>")
    gr.Markdown(
        """
        # 🕵️ UIDE Forense AI 3.0+
        ### Sistema Multimodal de Detección de Contenido Sintético
        
        > **Nuevo en v3.0+**: Detector de imágenes con multiLID, UFD y Semantic Expert.  
        > Motor de fusión jerárquico optimizado para difusión ultra-realista.
        """
    )

    with gr.Tabs():

        # =============================================
        # TAB 1: Imágenes (Detector Forense v3.0+)
        # =============================================
        with gr.TabItem("🖼️ Imágenes"):
            gr.Markdown("""
            ### Análisis Forense de Imágenes
            
            **Expertos utilizados:**
            - 🔬 **multiLID**: Análisis geométrico del espacio de features
            - 🎯 **UFD**: Clasificador visual universal (CLIP)
            - 🧠 **Semantic**: Análisis de plausibilidad de la escena
            
            **Veredictos posibles:**
            - 🚨 GENERADA POR IA
            - ⚠️ PROBABLEMENTE GENERADA POR IA
            - ✅ PROBABLEMENTE REAL / REAL
            - ❓ NO CONCLUYENTE (raro)
            """)
            
            with gr.Row():
                with gr.Column():
                    img_input = gr.Image(
                        label="Imagen a analizar", 
                        type="numpy", 
                        sources=["upload", "clipboard"]
                    )
                    btn_img = gr.Button("🔍 Analizar Imagen", variant="primary", size="lg")
                    
                with gr.Column():
                    img_output = gr.HTML(label="Resultados Forenses")

            btn_img.click(analizar_imagen, inputs=img_input, outputs=img_output)

        # =============================================
        # TAB 2: Video (Deepfakes)
        # =============================================
        with gr.TabItem("🎥 Video"):
            gr.Markdown("""
            ### Detección de Deepfakes en Video
            - **Modelo**: XceptionNet (FaceForensics++)
            - **Método**: Análisis de consistencia facial frame-by-frame
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    vid_input = gr.Video(label="Video a analizar", sources=["upload"])
                    btn_vid = gr.Button("▶️ Iniciar Análisis", variant="primary", size="lg")

                    log_output = gr.Textbox(
                        label="📜 Log de Estado",
                        lines=10,
                        interactive=False,
                        info="Progreso en tiempo real"
                    )

                with gr.Column(scale=1):
                    vid_report_output = gr.HTML(label="Informe Forense")
                    
                    with gr.Row():
                        timeline_output = gr.Image(
                            label="📈 Línea de Tiempo", 
                            type="pil"
                        )
                        culprit_output = gr.Image(
                            label="📸 Frame Sospechoso", 
                            type="pil"
                        )

            btn_vid.click(
                fn=analizar_video,
                inputs=vid_input,
                outputs=[vid_report_output, log_output, timeline_output, culprit_output]
            )

        # =============================================
        # TAB 3: Audio (Voz Sintética)
        # =============================================
        with gr.TabItem("🔊 Audio"):
            gr.Markdown("""
            ### Detección de Audio Sintético
            - **Detecta**: ElevenLabs, RVC, TTS, clonación de voz
            - **Método**: Análisis espectral con Wav2Vec2
            """)
            
            with gr.Row():
                with gr.Column():
                    audio_input = gr.Audio(
                        label="Audio a analizar",
                        type="filepath",
                        sources=["upload", "microphone"]
                    )
                    btn_audio = gr.Button("🎤 Analizar Audio", variant="primary", size="lg")
                    
                with gr.Column():
                    audio_output = gr.HTML(label="Resultados")

            btn_audio.click(analizar_audio, inputs=audio_input, outputs=audio_output)

        # =============================================
        # TAB 4: Acerca de
        # =============================================
        with gr.TabItem("ℹ️ Acerca de"):
            gr.Markdown(
                """
                ### UIDE Forense AI 3.0+
                Sistema multimodal de detección de contenido sintético.
                
                ---
                
                #### 🧠 Arquitectura de Imagen v3.0+
                
                | Componente | Tecnología | Función |
                |------------|------------|---------|
                | Backbone | CLIP ViT-L/14 | Extracción de features |
                | multiLID | LID Analysis | Anomalías geométricas |
                | UFD | Linear Classifier | Patrones visuales IA |
                | Semantic | CLIP Prompting | Plausibilidad escena |
                | Fusion | Hierarchical Logic | Decisión explicable |
                
                ---
                
                #### 📚 Referencias
                - Radford et al., 2021 - CLIP
                - Ojha et al., CVPR 2023 - UniversalFakeDetect
                - Ma et al., ICLR 2018 - LID
                
                ---
                
                #### 👥 Equipo
                **Universidad Internacional del Ecuador (UIDE)**  
                Anthony Pérez • Bruno Ortega • Manuel Pacheco
                """
            )

if __name__ == "__main__":
    logger.info("🌐 Iniciando servidor Gradio...")
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
