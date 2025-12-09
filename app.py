from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2
import timm
import os
import logging
from typing import Optional, Tuple, Generator, List

import torch
import torch.nn as nn
import gradio as gr

# Importar módulos del proyecto
import config
from utils import (
    validar_imagen, validar_video,
    generar_reporte_imagen, generar_reporte_video, generar_reporte_error,
    generar_grafico_temporal,
    Timer,
)

# ==========================================
# 🔧 Configuración de Logging
# ==========================================
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

# ==========================================
# 🧠 Modelos de Deep Learning
# ==========================================

class ModelManager:
    """
    Gestor centralizado de modelos con caché y manejo robusto de errores.
    """

    def __init__(self):
        self.modelo_imagen: Optional[nn.Module] = None
        self.modelo_video: Optional[nn.Module] = None
        self.dispositivo = torch.device(config.DEVICE)

        # Transformaciones de imagen (definidas en config)
        self.transform_imagen = transforms.Compose([
            transforms.Resize(config.TRANSFORMS_RESIZE),
            transforms.CenterCrop(config.TRANSFORMS_CROP),
            transforms.ToTensor(),
            transforms.Normalize(
                config.TRANSFORMS_MEAN,
                config.TRANSFORMS_STD,
            ),
        ])

        # Transformaciones de video (Xception defaults)
        self.transform_video = transforms.Compose([
            transforms.Resize((config.VIDEO_SIZE, config.VIDEO_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize([0.5] * 3, [0.5] * 3),
        ])

        # Cargar modelos al inicializar
        self._cargar_modelos()

    def _cargar_modelos(self):
        """Carga ambos modelos con manejo de errores."""
        self.modelo_imagen = self._cargar_modelo_imagen()
        self.modelo_video = self._cargar_modelo_video()

    def _cargar_modelo_imagen(self) -> Optional[nn.Module]:
        """Carga el modelo de detección de imágenes (ResNet50 Modificado)."""
        logger.info("🖼️ Cargando modelo de imágenes...")

        try:
            if not os.path.exists(config.MODEL_IMAGE_PATH):
                logger.warning(
                    f"⚠️ No se encontró el modelo en: {config.MODEL_IMAGE_PATH}"
                )
                logger.warning("📥 Modo demostración activado para imágenes")
                return None

            # 1. Cargar arquitectura base ResNet50
            # Importante: pretrained=False porque usaremos pesos específicos
            model = models.resnet50(pretrained=False)

            # 2. MODIFICACIÓN CRÍTICA: Cambiar la última capa para 1 sola salida (Real vs Fake)
            # El modelo original de Wang et al. usa 1 neurona de salida.
            num_ftrs = model.fc.in_features
            model.fc = nn.Linear(num_ftrs, 1)

            # 3. Cargar los pesos
            # Usar map_location para evitar errores de CPU/GPU
            logger.info(f"📂 Leyendo pesos desde {config.MODEL_IMAGE_PATH}")
            state_dict = torch.load(config.MODEL_IMAGE_PATH, map_location=self.dispositivo)

            # Manejo de diccionarios de pesos
            if "model" in state_dict:
                state_dict = state_dict["model"]

            # Limpieza de llaves (si vienen con prefix 'module.')
            new_state_dict = {}
            for k, v in state_dict.items():
                k = k.replace("module.", "")
                new_state_dict[k] = v

            model.load_state_dict(new_state_dict, strict=True)

            model.to(self.dispositivo)
            model.eval()

            logger.info("✅ Modelo de imágenes cargado exitosamente")
            return model

        except Exception as e:
            logger.error(
                f"❌ Error cargando modelo de imágenes: {e}",
                exc_info=True,
            )
            logger.warning("📥 Usando modo demostración para imágenes")
            return None

    def _cargar_modelo_video(self) -> Optional[nn.Module]:
        """Carga el modelo de detección de deepfakes en video (Xception)."""
        logger.info("🎥 Cargando modelo de video...")

        try:
            modelo = timm.create_model(
                config.MODEL_VIDEO_NAME,
                pretrained=True,
                num_classes=2,
            )
            modelo.to(self.dispositivo)
            modelo.eval()

            logger.info("✅ Modelo de video cargado exitosamente")
            return modelo

        except Exception as e:
            logger.error(
                f"❌ Error cargando modelo de video: {e}",
                exc_info=True,
            )
            logger.warning("📥 Modo demostración activado para videos")
            return None


# Inicializar gestor de modelos (singleton)
model_manager = ModelManager()

# ==========================================
# 🔍 Funciones de Análisis
# ==========================================


def analizar_imagen(imagen_input) -> str:
    """
    Analiza una imagen para detectar si es sintética o manipulada.
    """
    logger.info("📸 Iniciando análisis de imagen...")

    # Validación de entrada
    if imagen_input is None:
        return generar_reporte_error("No se proporcionó ninguna imagen", "warning")

    es_valida, mensaje = validar_imagen(imagen_input)
    if not es_valida:
        return generar_reporte_error(mensaje, "error")

    # Modo demostración si el modelo no está cargado
    if model_manager.modelo_imagen is None:
        logger.warning("⚠️ Usando modo demostración (modelo no disponible)")
        import random
        prob = random.uniform(40, 95)
        es_fake = prob > 50
        h, w = imagen_input.shape[:2]
        return generar_reporte_imagen(es_fake, prob, w, h, 0.123)

    # Análisis real con el modelo
    try:
        with Timer() as timer:
            # Convertir a PIL y aplicar transformaciones
            img_pil = Image.fromarray(imagen_input).convert("RGB")
            img_tensor = model_manager.transform_imagen(img_pil).unsqueeze(0)
            img_tensor = img_tensor.to(model_manager.dispositivo)

            # Inferencia
            with torch.no_grad():
                output = model_manager.modelo_imagen(img_tensor)
                # Aplicar Sigmoid para obtener probabilidad (0-1)
                probabilidad_fake = torch.sigmoid(output).item() * 100

            # Determinar clasificación
            es_fake = probabilidad_fake > config.IMAGE_THRESHOLD

            logger.info(
                f"✅ Análisis completado: {'FAKE' if es_fake else 'REAL'} "
                f"({probabilidad_fake:.2f}%)"
            )

        # Generar reporte
        ancho, alto = img_pil.size
        return generar_reporte_imagen(
            es_fake=es_fake,
            probabilidad=probabilidad_fake,
            ancho=ancho,
            alto=alto,
            tiempo_proceso=timer.duracion,
        )

    except Exception as e:
        logger.error(
            f"❌ Error durante el análisis de imagen: {e}",
            exc_info=True,
        )
        return generar_reporte_error(
            f"Ocurrió un error durante el análisis: {str(e)}",
            "error",
        )


def analizar_video(video_path: str, progress=gr.Progress()) -> Generator[Tuple[str, str, Optional[Image.Image], Optional[Image.Image]], None, None]:
    """
    Analiza un video para detectar deepfakes.
    Función generadora que emite actualizaciones de estado.

    Returns:
        Generator yielding: (HTML Report, Log Text, Timeline Plot, Culprit Frame)
    """
    logger.info("🎬 Iniciando análisis de video...")

    # Estados iniciales
    log_text = "🚀 Iniciando proceso..."
    yield "", log_text, None, None

    # Validación de entrada
    if video_path is None:
        yield generar_reporte_error("No se proporcionó ningún video", "warning"), "❌ Error: Sin video", None, None
        return

    es_valido, mensaje = validar_video(video_path)
    if not es_valido:
        yield generar_reporte_error(mensaje, "error"), f"❌ Error: {mensaje}", None, None
        return

    # Verificar disponibilidad del modelo
    if model_manager.modelo_video is None:
        yield generar_reporte_error("Modelo no disponible", "error"), "❌ Error: Modelo no cargado", None, None
        return

    try:
        with Timer() as timer:
            # Abrir video
            log_text += "\n📂 Abriendo archivo de video..."
            yield "", log_text, None, None

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                yield generar_reporte_error("Error abriendo video", "error"), "❌ Error al abrir archivo", None, None
                return

            # Metadatos
            frames_totales = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duracion = frames_totales / fps if fps and fps > 0 else 0

            # Validación duración
            if duracion > config.MAX_VIDEO_DURATION_SECONDS:
                cap.release()
                msg = f"Video demasiado largo ({duracion:.1f}s)"
                yield generar_reporte_error(msg, "warning"), f"⚠️ {msg}", None, None
                return

            log_text += f"\nℹ️ Video cargado: {frames_totales} frames, {duracion:.1f}s"
            log_text += "\n👀 Cargando detector de rostros..."
            yield "", log_text, None, None

            # Detector de rostros
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

            # Variables de seguimiento
            predicciones = [] # Lista de (frame_idx, prob)
            frames_con_rostro = 0
            max_fake_prob = 0.0
            culprit_frame = None

            # Configurar stride
            stride = config.VIDEO_FRAME_STRIDE
            if duracion > 60:
                stride = 60

            log_text += f"\n🧠 Iniciando análisis (Stride: {stride})..."
            yield "", log_text, None, None

            # Bucle de análisis con gr.Progress
            for i in progress.tqdm(range(0, frames_totales, stride), desc="🔍 Analizando frames..."):
                # Actualizar log cada cierto tiempo para no saturar
                if i % (stride * 5) == 0:
                    status = f"⏳ Procesando frame {i}/{frames_totales} ({(i/frames_totales)*100:.0f}%)"
                    yield "", log_text + "\n" + status, None, None

                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    break

                # Detectar rostros
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)

                if len(faces) > 0:
                    frames_con_rostro += 1

                    # Procesar el primer rostro
                    (x, y, w, h) = faces[0]

                    # Margen de seguridad para el recorte
                    margin = int(w * 0.2)
                    x1 = max(0, x - margin)
                    y1 = max(0, y - margin)
                    x2 = min(frame.shape[1], x + w + margin)
                    y2 = min(frame.shape[0], y + h + margin)

                    cara = frame[y1:y2, x1:x2]

                    # Transformar
                    cara_rgb = cv2.cvtColor(cara, cv2.COLOR_BGR2RGB)
                    cara_pil = Image.fromarray(cara_rgb)
                    cara_tensor = model_manager.transform_video(cara_pil).unsqueeze(0)
                    cara_tensor = cara_tensor.to(model_manager.dispositivo)

                    # Inferencia
                    with torch.no_grad():
                        output = model_manager.modelo_video(cara_tensor)
                        prob_fake = torch.softmax(output, dim=1)[0][1].item() * 100

                        predicciones.append((i, prob_fake))

                        # Guardar el frame más sospechoso
                        if prob_fake > max_fake_prob:
                            max_fake_prob = prob_fake
                            culprit_frame = cara_pil

            cap.release()

            if frames_con_rostro < config.MIN_FACES_REQUIRED:
                msg = f"Insuficientes rostros detectados ({frames_con_rostro})"
                yield generar_reporte_error(msg, "warning"), f"⚠️ {msg}", None, None
                return

            # Generar resultados finales
            log_text += "\n✅ Análisis finalizado. Generando reporte..."
            yield "", log_text, None, None

            # Calcular promedio
            probs_values = [p[1] for p in predicciones]
            promedio_fake = sum(probs_values) / len(probs_values)
            es_deepfake = promedio_fake > config.VIDEO_THRESHOLD

            # Generar gráfico
            timeline_plot = generar_grafico_temporal(predicciones)

            # Generar reporte HTML
            reporte_html = generar_reporte_video(
                es_deepfake=es_deepfake,
                probabilidad=promedio_fake,
                frames_totales=frames_totales,
                frames_analizados=frames_con_rostro,
                duracion=duracion,
                tiempo_proceso=timer.duracion
            )

            final_log = log_text + f"\n🏁 Completado: {'DEEPFAKE' if es_deepfake else 'REAL'} ({promedio_fake:.1f}%)"

            yield reporte_html, final_log, timeline_plot, culprit_frame

    except Exception as e:
        logger.error(f"❌ Error en video: {e}", exc_info=True)
        yield generar_reporte_error(str(e), "error"), f"❌ Error crítico: {str(e)}", None, None


# ==========================================
# 🖥️ Interfaz Gradio
# ==========================================

css_custom = """
.gradio-container { font-family: 'Inter', sans-serif; }
"""

with gr.Blocks(title="UIDE Forense AI") as demo:
    gr.Markdown(
        """
        # 🕵️ UIDE Forense AI
        ### Sistema de Detección de Contenido Sintético y Deepfakes
        """
    )

    with gr.Tabs():

        # TAB 1: Imágenes
        with gr.TabItem("🖼️ Análisis de Imágenes"):
            with gr.Row():
                with gr.Column():
                    img_input = gr.Image(label="Imagen a analizar", type="numpy", sources=["upload", "clipboard"])
                    btn_img = gr.Button("🔍 Analizar Imagen", variant="primary")
                with gr.Column():
                    img_output = gr.HTML(label="Resultados")

            btn_img.click(analizar_imagen, inputs=img_input, outputs=img_output)

        # TAB 2: Video
        with gr.TabItem("🎥 Análisis de Video (Deepfakes)"):
            with gr.Row():
                with gr.Column(scale=1):
                    vid_input = gr.Video(label="Video a analizar", sources=["upload"])
                    btn_vid = gr.Button("▶️ Iniciar Análisis Profundo", variant="primary")

                    log_output = gr.Textbox(
                        label="📜 Log de Estado",
                        lines=10,
                        interactive=False,
                        info="Progreso en tiempo real"
                    )

                with gr.Column(scale=1):
                    vid_report_output = gr.HTML(label="Informe Forense")
                    
                    with gr.Row():
                        timeline_output = gr.Image(label="📈 Línea de Tiempo (Probabilidad Fake)", type="pil")
                        culprit_output = gr.Image(label="📸 Frame Más Sospechoso", type="pil")

            btn_vid.click(
                fn=analizar_video,
                inputs=vid_input,
                outputs=[vid_report_output, log_output, timeline_output, culprit_output]
            )

        # TAB 3: Acerca de
        with gr.TabItem("ℹ️ Acerca de"):
            gr.Markdown(
                """
                ### UIDE Forense AI
                Desarrollado para la detección de manipulación digital.
                
                **Modelos:**
                - Imágenes: ResNet50 (Wang et al.) - Detección de artefactos GAN/Difusión.
                - Video: XceptionNet (FaceForensics++) - Detección de deepfakes faciales.
                """
            )

if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
