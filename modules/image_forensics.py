"""
Image Forensics - Detección de imágenes sintéticas con Ensamble
UIDE Forense AI

Este módulo implementa un sistema de detección de imágenes IA usando 
dos modelos complementarios:
- Experto GAN: ResNet50 (Wang et al.) para detectar artefactos de GANs
- Experto Difusión: ViT (HuggingFace) para detectar imágenes de DALL-E/Midjourney/SD
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

import torch
from PIL import Image

import config
from core.model_manager import get_model_manager
from core.processor import preprocess_image

logger = logging.getLogger(__name__)


@dataclass
class ImageAnalysisResult:
    """Resultado del análisis de imagen."""
    score: float
    verdict: str
    detected_source: str
    gan_score: float
    diffusion_score: float
    model_used: str


class ImageForensicsDetector:
    """
    Detector de imágenes sintéticas usando ensamble de modelos.
    
    Combina:
    - Modelo GAN (ResNet50): Detecta artefactos de StyleGAN, FaceApp, etc.
    - Modelo Difusión (ViT): Detecta imágenes de Midjourney, DALL-E, Stable Diffusion
    
    La decisión final usa MAX de ambas probabilidades (alta sensibilidad).
    """

    def __init__(self):
        self.model_manager = get_model_manager()
        
        # Modelo de difusión (HuggingFace)
        self.diff_processor = None
        self.diff_model = None
        self._diffusion_loaded = False
        
        logger.info("🖼️ ImageForensicsDetector inicializado")

    def _cargar_modelo_diffusion(self):
        """Carga el modelo de difusión desde HuggingFace con mensajes de progreso."""
        if self._diffusion_loaded:
            return
            
        try:
            from transformers import AutoImageProcessor, AutoModelForImageClassification
            
            model_name = config.MODEL_DIFFUSION_NAME
            
            # ============================================
            # MENSAJE CLARO DE DESCARGA
            # ============================================
            print("\n" + "="*60)
            print("📥 DESCARGANDO MODELO DE DIFUSIÓN (HuggingFace)")
            print(f"   Modelo: {model_name}")
            print("   Esto puede tomar varios minutos la primera vez...")
            print("   (El modelo se cachea para futuras ejecuciones)")
            print("="*60 + "\n")
            
            logger.info(f"📥 Iniciando descarga del modelo: {model_name}")
            
            # Cargar procesador de imágenes
            print("   [1/2] Descargando procesador de imágenes...")
            self.diff_processor = AutoImageProcessor.from_pretrained(model_name)
            logger.info("✅ Procesador de difusión cargado")
            
            # Cargar modelo
            print("   [2/2] Descargando modelo de clasificación (~500MB)...")
            self.diff_model = AutoModelForImageClassification.from_pretrained(model_name)
            self.diff_model.to(self.model_manager.get_dispositivo())
            self.diff_model.eval()
            
            print("\n✅ Modelo de difusión cargado exitosamente!\n")
            logger.info("✅ Modelo de difusión cargado exitosamente")
            
            self._diffusion_loaded = True
            
        except ImportError as e:
            logger.error("❌ transformers no está instalado. Ejecuta: pip install transformers")
            raise
        except Exception as e:
            logger.error(f"❌ Error cargando modelo de difusión: {e}")
            self._diffusion_loaded = True  # Marcar como intentado
            raise

    def _analizar_gan(self, img_pil: Image.Image) -> float:
        """
        Analiza la imagen con el modelo GAN (ResNet50).
        
        Returns:
            Probabilidad de ser fake (0-100)
        """
        modelo = self.model_manager.cargar_modelo_imagen_gan()
        
        if modelo is None:
            logger.warning("⚠️ Modelo GAN no disponible, usando valor neutro")
            return 25.0  # Valor bajo neutral si no hay modelo
        
        try:
            # Aplicar transformaciones
            img_tensor = self.model_manager.transform_imagen(img_pil).unsqueeze(0)
            img_tensor = img_tensor.to(self.model_manager.get_dispositivo())
            
            with torch.no_grad():
                # Predicción original
                output = modelo(img_tensor)
                prob1 = torch.sigmoid(output).item() * 100
                
                # TTA: Predicción con flip horizontal
                img_tensor_flip = torch.flip(img_tensor, [3])
                output_flip = modelo(img_tensor_flip)
                prob2 = torch.sigmoid(output_flip).item() * 100
                
                # Tomar máximo (mayor sensibilidad)
                prob_gan = max(prob1, prob2)
                
            logger.debug(f"GAN TTA: Original={prob1:.2f}%, Flip={prob2:.2f}% -> Final={prob_gan:.2f}%")
            return prob_gan
            
        except Exception as e:
            logger.error(f"Error en análisis GAN: {e}")
            return 25.0

    def _analizar_diffusion(self, img_pil: Image.Image) -> float:
        """
        Analiza la imagen con el modelo de difusión (ViT).
        
        Returns:
            Probabilidad de ser fake (0-100)
        """
        try:
            # Cargar modelo si es necesario
            self._cargar_modelo_diffusion()
            
            if self.diff_model is None or self.diff_processor is None:
                logger.warning("⚠️ Modelo de difusión no disponible")
                return 25.0
            
            # Procesar imagen
            inputs = self.diff_processor(images=img_pil, return_tensors="pt")
            inputs = {k: v.to(self.model_manager.get_dispositivo()) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.diff_model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1)
                
                # El modelo tiene labels: 0=human, 1=ai
                # Verificar el orden de las etiquetas
                if hasattr(self.diff_model.config, 'id2label'):
                    id2label = self.diff_model.config.id2label
                    logger.debug(f"Labels del modelo: {id2label}")
                    
                    # Buscar el índice de "artificial" o "ai"
                    ai_idx = None
                    for idx, label in id2label.items():
                        if 'ai' in label.lower() or 'artificial' in label.lower() or 'fake' in label.lower():
                            ai_idx = int(idx)
                            break
                    
                    if ai_idx is not None:
                        prob_diff = probs[0][ai_idx].item() * 100
                    else:
                        # Asumir que índice 1 es AI
                        prob_diff = probs[0][1].item() * 100
                else:
                    prob_diff = probs[0][1].item() * 100
                
            logger.debug(f"Difusión: {prob_diff:.2f}%")
            return prob_diff
            
        except Exception as e:
            logger.error(f"Error en análisis de difusión: {e}")
            return 25.0

    def predict(self, image_input) -> Dict[str, Any]:
        """
        Analiza una imagen usando el ensamble GAN + Difusión.
        
        Args:
            image_input: PIL Image o numpy array
            
        Returns:
            Diccionario con score, verdict, detected_source, etc.
        """
        logger.info("🔍 Iniciando análisis de imagen con ensamble...")
        
        # Convertir a PIL si es necesario
        if not isinstance(image_input, Image.Image):
            img_pil = preprocess_image(image_input)
        else:
            img_pil = image_input.convert("RGB")
        
        # Análisis con ambos modelos
        logger.info("   [1/2] Analizando con modelo GAN...")
        prob_gan = self._analizar_gan(img_pil)
        
        logger.info("   [2/2] Analizando con modelo de Difusión...")
        prob_diff = self._analizar_diffusion(img_pil)
        
        # ============================================
        # LÓGICA DE ENSAMBLE: MAX (Alta sensibilidad)
        # Si cualquiera detecta fake con alta confianza, es fake
        # ============================================
        final_score = max(prob_gan, prob_diff)
        
        # Determinar origen más probable
        if final_score > 50:
            if prob_gan > prob_diff:
                origin = "GAN (StyleGAN/FaceApp/ProGAN)"
                model_used = "GAN Detector"
            else:
                origin = "Difusión (Midjourney/DALL-E/Stable Diffusion)"
                model_used = "Diffusion Detector"
            verdict = "SINTÉTICO"
        else:
            origin = "N/A"
            model_used = "Ensemble"
            verdict = "REAL"
        
        result = {
            "score": final_score,
            "verdict": verdict,
            "detected_source": origin,
            "gan_score": prob_gan,
            "diffusion_score": prob_diff,
            "model_used": model_used,
        }
        
        logger.info(f"✅ Análisis completado: {verdict} ({final_score:.2f}%)")
        logger.info(f"   GAN: {prob_gan:.2f}% | Difusión: {prob_diff:.2f}%")
        
        return result
