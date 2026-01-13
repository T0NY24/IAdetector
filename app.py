"""
UIDE Forense AI - Sistema de Detección de Contenido Sintético
Clean Architecture - Interfaz Gradio

Este archivo contiene únicamente la interfaz de usuario.
La lógica de negocio está separada en los módulos core/ y modules/.
"""

import logging
from typing import Optional, Tuple, Generator
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
    generar_reporte_imagen, 
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
logger.info("🚀 UIDE Forense AI 2.0 - Iniciando Sistema")
logger.info("=" * 60)

# Los modelos se cargan bajo demanda (lazy loading)
image_detector = ImageForensicsDetector()
video_detector = VideoForensicsDetector()
audio_detector = AudioForensicsDetector()

logger.info("✅ Detectores inicializados (modelos: lazy loading)")


# ==========================================
# 🔍 Funciones de Análisis
# ==========================================

def analizar_imagen(imagen_input) -> str:
    """
    Analiza una imagen para detectar si es sintética usando el ensamble GAN+Difusión.
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
            # Análisis con el detector de imagen (ensamble)
            resultado = image_detector.predict(imagen_input)
        
        # Obtener dimensiones
        if hasattr(imagen_input, 'shape'):
            alto, ancho = imagen_input.shape[:2]
        else:
            ancho, alto = imagen_input.size
        
        # Generar reporte mejorado con info del ensamble
        return generar_reporte_imagen(
            es_fake=resultado["score"] > 50,
            probabilidad=resultado["score"],
            ancho=ancho,
            alto=alto,
            tiempo_proceso=timer.duracion,
            origen_detectado=resultado.get("detected_source", "N/A"),
            gan_score=resultado.get("gan_score", 0),
            diffusion_score=resultado.get("diffusion_score", 0),
        )
        
    except Exception as e:
        logger.error(f"❌ Error en análisis de imagen: {e}", exc_info=True)
        return generar_reporte_error(f"Error durante el análisis: {str(e)}", "error")


def analizar_video(video_path: str, progress=gr.Progress()) -> Tuple[str, str, Optional[Image.Image], Optional[Image.Image]]:
    """
    Analiza un video para detectar deepfakes.
    Función generadora que emite actualizaciones de estado.
    """
    logger.info("🎬 Solicitud de análisis de video recibida")
    
    # Estados iniciales
    log_text = "🚀 Iniciando proceso..."
    
    # Validación de entrada
    if video_path is None:
        yield generar_reporte_error("No se proporcionó ningún video", "warning"), "❌ Error: Sin video", None, None
        return
    
    es_valido, mensaje = validar_video(video_path)
    if not es_valido:
        yield generar_reporte_error(mensaje, "error"), f"❌ Error: {mensaje}", None, None
        return
    
    try:
        with Timer() as timer:
            # Usar el detector de video
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
        
        # Generar gráfico de timeline
        timeline_plot = generar_grafico_temporal(resultado_final.get("predictions", []))
        
        # Generar reporte HTML
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
    
    # Validación de entrada
    if audio_path is None:
        return generar_reporte_error("No se proporcionó ningún archivo de audio", "warning")
    
    es_valido, mensaje = validar_audio(audio_path)
    if not es_valido:
        return generar_reporte_error(mensaje, "error")
    
    try:
        with Timer() as timer:
            # Análisis con el detector de audio
            resultado = audio_detector.predict(audio_path)
        
        if "error" in resultado and resultado.get("verdict") == "ERROR":
            return generar_reporte_error(resultado["error"], "error")
        
        # Generar reporte
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

with gr.Blocks(title="UIDE Forense AI 2.0") as demo:
    gr.Markdown(
        """
        # 🕵️ UIDE Forense AI 2.0
        ### Sistema Multimodal de Detección de Contenido Sintético y Deepfakes
        
        > **Nuevo en v2.0**: Detección de imágenes mejorada con ensamble GAN+Difusión, 
        > soporte para detección de audio sintético.
        """
    )

    with gr.Tabs():

        # =============================================
        # TAB 1: Imágenes (GAN + Difusión)
        # =============================================
        with gr.TabItem("🖼️ Imágenes (GAN + Difusión)"):
            gr.Markdown("""
            ### Detección de Imágenes Generadas por IA
            - **Modelo GAN**: Detecta imágenes de StyleGAN, FaceApp, ProGAN
            - **Modelo Difusión**: Detecta imágenes de Midjourney, DALL-E, Stable Diffusion
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
                    img_output = gr.HTML(label="Resultados")

            btn_img.click(analizar_imagen, inputs=img_input, outputs=img_output)

        # =============================================
        # TAB 2: Video (Deepfakes)
        # =============================================
        with gr.TabItem("🎥 Video (Deepfakes)"):
            gr.Markdown("""
            ### Detección de Deepfakes en Video
            - **Modelo**: XceptionNet (FaceForensics++)
            - **Método**: Análisis de consistencia facial frame-by-frame
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    vid_input = gr.Video(label="Video a analizar", sources=["upload"])
                    btn_vid = gr.Button("▶️ Iniciar Análisis Profundo", variant="primary", size="lg")

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
                            label="📸 Frame Más Sospechoso", 
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
        with gr.TabItem("🔊 Audio (Voz Sintética)"):
            gr.Markdown("""
            ### Detección de Audio Generado por IA
            - **Detecta**: ElevenLabs, RVC, TTS modernos, clonación de voz
            - **Método**: Análisis espectral con modelos de HuggingFace
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
                ### UIDE Forense AI 2.0
                Sistema multimodal de detección de contenido sintético desarrollado para 
                análisis forense digital.
                
                ---
                
                #### 🧠 Modelos Utilizados
                
                | Tipo | Modelo | Descripción |
                |------|--------|-------------|
                | 🖼️ Imagen GAN | ResNet50 (Wang et al.) | Detecta artefactos de redes GAN |
                | 🖼️ Imagen Difusión | ViT (HuggingFace) | Detecta imágenes de modelos de difusión |
                | 🎥 Video | XceptionNet | Detecta deepfakes faciales |
                | 🔊 Audio | Wav2Vec2 | Detecta voces sintéticas |
                
                ---
                
                #### 📚 Referencias
                - Wang et al. "CNN-generated images are surprisingly easy to spot... for now"
                - FaceForensics++ Benchmark
                - HuggingFace Transformers
                
                ---
                
                #### ⚙️ Arquitectura
                ```
                ProyectoForenseUIDE/
                ├── app.py          # Interfaz (este archivo)
                ├── config.py       # Configuración
                ├── core/           # Gestión de modelos
                ├── modules/        # Detectores especializados
                └── utils/          # Utilidades y reportes
                ```
                """
            )

if __name__ == "__main__":
    logger.info("🌐 Iniciando servidor Gradio...")
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
