"""
Video Forensics - Detección de Deepfakes en Video
UIDE Forense AI

Este módulo implementa la detección de deepfakes faciales usando
XceptionNet pre-entrenado en FaceForensics++.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional, Generator
import cv2
from PIL import Image

import torch
import gradio as gr

import config
from core.model_manager import get_model_manager
from core.processor import preprocess_video_frame

logger = logging.getLogger(__name__)


class VideoForensicsDetector:
    """
    Detector de deepfakes en video usando análisis facial frame-by-frame.
    
    Usa XceptionNet para clasificar rostros como reales o manipulados.
    Implementa estrategia Top-K para clasificación robusta.
    """

    def __init__(self):
        self.model_manager = get_model_manager()
        self.face_cascade = None
        
        logger.info("🎥 VideoForensicsDetector inicializado")

    def _cargar_detector_rostros(self):
        """Carga el detector de rostros Haar Cascade."""
        if self.face_cascade is None:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            logger.info("👤 Detector de rostros cargado")
        return self.face_cascade

    def _analizar_frame(self, frame: any, face_region: Tuple[int, int, int, int]) -> float:
        """
        Analiza un rostro extraído de un frame.
        
        Args:
            frame: Frame de video (BGR)
            face_region: Tupla (x, y, w, h) del rostro
            
        Returns:
            Probabilidad de ser deepfake (0-100)
        """
        modelo = self.model_manager.cargar_modelo_video()
        
        if modelo is None:
            return 50.0  # Valor neutro si no hay modelo
        
        try:
            # Preprocesar frame
            face_pil, _ = preprocess_video_frame(frame, face_region)
            
            # Aplicar transformaciones
            face_tensor = self.model_manager.transform_video(face_pil).unsqueeze(0)
            face_tensor = face_tensor.to(self.model_manager.get_dispositivo())
            
            with torch.no_grad():
                output = modelo(face_tensor)
                prob_fake = torch.softmax(output, dim=1)[0][1].item() * 100
                
            return prob_fake
            
        except Exception as e:
            logger.error(f"Error analizando frame: {e}")
            return 50.0

    def predict(
        self, 
        video_path: str, 
        progress: Optional[gr.Progress] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Analiza un video para detectar deepfakes.
        Función generadora que emite actualizaciones de estado.
        
        Args:
            video_path: Ruta al archivo de video
            progress: Objeto Progress de Gradio (opcional)
            
        Yields:
            Diccionarios con estado del análisis
        """
        logger.info(f"🎬 Iniciando análisis de video: {video_path}")
        
        # Estado inicial
        yield {
            "status": "starting",
            "message": "🚀 Iniciando proceso...",
            "report": "",
            "timeline": None,
            "culprit_frame": None,
        }
        
        try:
            # Abrir video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                yield {
                    "status": "error",
                    "message": "❌ Error abriendo video",
                    "report": None,
                    "timeline": None,
                    "culprit_frame": None,
                }
                return
            
            # Metadatos
            frames_totales = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duracion = frames_totales / fps if fps and fps > 0 else 0
            
            yield {
                "status": "processing",
                "message": f"ℹ️ Video: {frames_totales} frames, {duracion:.1f}s",
                "report": "",
                "timeline": None,
                "culprit_frame": None,
            }
            
            # Validar duración
            if duracion > config.MAX_VIDEO_DURATION_SECONDS:
                cap.release()
                yield {
                    "status": "error",
                    "message": f"⚠️ Video demasiado largo ({duracion:.1f}s)",
                    "report": None,
                    "timeline": None,
                    "culprit_frame": None,
                }
                return
            
            # Cargar detector de rostros
            face_cascade = self._cargar_detector_rostros()
            
            # Variables de seguimiento
            predicciones: List[Tuple[int, float]] = []
            frames_con_rostro = 0
            max_fake_prob = 0.0
            culprit_frame: Optional[Image.Image] = None
            
            # Configurar stride
            stride = config.VIDEO_FRAME_STRIDE
            if duracion > 60:
                stride = 60
            
            yield {
                "status": "processing",
                "message": f"🧠 Analizando (stride: {stride})...",
                "report": "",
                "timeline": None,
                "culprit_frame": None,
            }
            
            # Bucle de análisis
            frame_indices = range(0, frames_totales, stride)
            if progress:
                frame_indices = progress.tqdm(frame_indices, desc="🔍 Analizando frames...")
            
            for i in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detectar rostros
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    frames_con_rostro += 1
                    
                    # Procesar primer rostro
                    x, y, w, h = faces[0]
                    prob_fake = self._analizar_frame(frame, (x, y, w, h))
                    
                    predicciones.append((i, prob_fake))
                    
                    # Guardar frame más sospechoso
                    if prob_fake > max_fake_prob:
                        max_fake_prob = prob_fake
                        face_pil, _ = preprocess_video_frame(frame, (x, y, w, h))
                        culprit_frame = face_pil
                
                # Actualización periódica
                if i % (stride * 5) == 0 and not progress:
                    yield {
                        "status": "processing",
                        "message": f"⏳ Frame {i}/{frames_totales} ({(i/frames_totales)*100:.0f}%)",
                        "report": "",
                        "timeline": None,
                        "culprit_frame": None,
                    }
            
            cap.release()
            
            # Verificar rostros suficientes
            if frames_con_rostro < config.MIN_FACES_REQUIRED:
                yield {
                    "status": "error",
                    "message": f"⚠️ Pocos rostros detectados ({frames_con_rostro})",
                    "report": None,
                    "timeline": None,
                    "culprit_frame": None,
                }
                return
            
            # Calcular promedio Top-K
            if predicciones:
                probs_values = [p[1] for p in predicciones]
                probs_values.sort(reverse=True)
                
                k = max(1, int(len(probs_values) * 0.1))
                top_k_values = probs_values[:k]
                promedio_fake = sum(top_k_values) / len(top_k_values)
            else:
                promedio_fake = 0.0
            
            es_deepfake = promedio_fake > config.VIDEO_THRESHOLD
            
            logger.info(f"✅ Análisis completado: {'DEEPFAKE' if es_deepfake else 'REAL'} ({promedio_fake:.1f}%)")
            
            yield {
                "status": "complete",
                "message": f"🏁 {'DEEPFAKE' if es_deepfake else 'REAL'} ({promedio_fake:.1f}%)",
                "is_deepfake": es_deepfake,
                "probability": promedio_fake,
                "frames_total": frames_totales,
                "frames_analyzed": frames_con_rostro,
                "duration": duracion,
                "predictions": predicciones,
                "culprit_frame": culprit_frame,
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de video: {e}", exc_info=True)
            yield {
                "status": "error",
                "message": f"❌ Error: {str(e)}",
                "report": None,
                "timeline": None,
                "culprit_frame": None,
            }
