"""
Feature Extractor - Backbone CLIP compartido para extracción de features.

UIDE Forense AI v3.0
Clean Architecture - Capa de Infraestructura

Este módulo proporciona:
- Carga lazy de CLIP ViT-L/14
- Extracción de features finales para UFD
- Extracción de features intermedias para multiLID
- Caché de modelos para eficiencia
"""

import logging
from typing import List, Optional, Tuple, Dict
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class CLIPFeatureExtractor:
    """
    Extractor de features usando CLIP ViT-L/14.
    
    Este es el backbone compartido por ambos expertos (multiLID y UFD).
    Usa lazy loading para cargar el modelo solo cuando se necesita.
    
    Características:
    - Lazy loading del modelo CLIP
    - Extracción de features del penúltimo layer
    - Acceso a features intermedias para análisis LID
    - Compatible con CPU y CUDA
    
    Example:
        extractor = CLIPFeatureExtractor(device="cuda")
        features = extractor.extract_features(image)
        intermediate = extractor.extract_intermediate_features(image)
    """
    
    # Capas del ViT a extraer para multiLID
    INTERMEDIATE_LAYERS = [6, 8, 10, 11]
    
    def __init__(self, device: str = "cpu"):
        """
        Inicializa el extractor.
        
        Args:
            device: Dispositivo para inferencia ("cpu" o "cuda")
        """
        self.device = device
        self._model = None
        self._preprocess = None
        self._loaded = False
        
        logger.info(f"🔧 CLIPFeatureExtractor inicializado (device={device})")
    
    def _load_model(self) -> None:
        """
        Carga el modelo CLIP ViT-L/14 de OpenAI.
        
        Se ejecuta solo la primera vez que se necesita el modelo.
        Muestra mensajes de progreso para el usuario.
        """
        if self._loaded:
            return
        
        try:
            import clip
            
            print("\n" + "=" * 60)
            print("📥 CARGANDO MODELO CLIP ViT-L/14")
            print("   Este es el backbone para análisis forense de imágenes")
            print("   Primera carga puede tomar 1-2 minutos...")
            print("=" * 60 + "\n")
            
            logger.info("📥 Iniciando carga de CLIP ViT-L/14...")
            
            # Cargar modelo y preprocesador
            self._model, self._preprocess = clip.load(
                "ViT-L/14", 
                device=self.device,
                jit=False  # Deshabilitamos JIT para acceder a intermedios
            )
            
            # Modo evaluación
            self._model.eval()
            
            # Congelar parámetros (solo inferencia)
            for param in self._model.parameters():
                param.requires_grad = False
            
            self._loaded = True
            
            print("✅ CLIP ViT-L/14 cargado exitosamente!\n")
            logger.info("✅ CLIP ViT-L/14 cargado exitosamente")
            
        except ImportError:
            logger.error("❌ Paquete 'clip' no instalado. Ejecutar: pip install git+https://github.com/openai/CLIP.git")
            raise ImportError(
                "El paquete CLIP de OpenAI es requerido. "
                "Instalar con: pip install git+https://github.com/openai/CLIP.git"
            )
        except Exception as e:
            logger.error(f"❌ Error cargando CLIP: {e}")
            raise
    
    def _ensure_loaded(self) -> None:
        """Asegura que el modelo esté cargado."""
        if not self._loaded:
            self._load_model()
    
    def preprocess_image(self, image_input) -> torch.Tensor:
        """
        Preprocesa una imagen para CLIP.
        
        Args:
            image_input: PIL.Image, numpy array, o path a archivo
            
        Returns:
            Tensor preprocesado listo para el modelo
        """
        self._ensure_loaded()
        
        # Convertir a PIL si es necesario
        if isinstance(image_input, (str, Path)):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            image = Image.fromarray(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")
        else:
            raise TypeError(f"Tipo de imagen no soportado: {type(image_input)}")
        
        # Aplicar preprocesamiento de CLIP
        processed = self._preprocess(image).unsqueeze(0).to(self.device)
        
        return processed
    
    def extract_features(self, image_input) -> torch.Tensor:
        """
        Extrae el embedding final de CLIP para una imagen.
        
        Este es el vector de features usado por UFD para clasificación.
        
        Args:
            image_input: PIL.Image, numpy array, o path a archivo
            
        Returns:
            Tensor de shape (1, 768) con el embedding de la imagen
        """
        self._ensure_loaded()
        
        # Preprocesar imagen
        image_tensor = self.preprocess_image(image_input)
        
        with torch.no_grad():
            # Extraer features del encoder visual
            features = self._model.encode_image(image_tensor)
            
            # Normalizar (como hace CLIP internamente)
            features = features / features.norm(dim=-1, keepdim=True)
        
        logger.debug(f"Features extraídas: shape={features.shape}")
        return features
    
    def calculate_probabilities(self, image_features: torch.Tensor, text_prompts: List[str]) -> Dict[str, float]:
        """
        Calcula la probabilidad de que la imagen coincida con cada prompt.
        
        Args:
            image_features: Tensor de features de imagen (1, 768)
            text_prompts: Lista de descripciones textuales
            
        Returns:
            Diccionario {prompt: probabilidad}
        """
        self._ensure_loaded()
        import clip
        
        with torch.no_grad():
            # Tokenizar y codificar textos
            text_tokens = clip.tokenize(text_prompts).to(self.device)
            text_features = self._model.encode_text(text_tokens)
            
            # Normalizar
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Calcular similitud (cosine similarity)
            # Logit scale es aprendido por CLIP para escalar los productos punto
            logit_scale = self._model.logit_scale.exp()
            logits_per_image = logit_scale * image_features @ text_features.t()
            
            # Softmax para obtener probabilidades
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
            
            return {
                prompt: float(prob) 
                for prompt, prob in zip(text_prompts, probs)
            }
    
    def extract_intermediate_features(self, image_input) -> List[torch.Tensor]:
        """
        Extrae features de capas intermedias del ViT para análisis LID.
        
        El análisis multiLID requiere features de múltiples profundidades
        para detectar anomalías en el espacio de representaciones.
        
        Args:
            image_input: PIL.Image, numpy array, o path a archivo
            
        Returns:
            Lista de tensores, uno por cada capa en INTERMEDIATE_LAYERS
        """
        self._ensure_loaded()
        
        # Preprocesar imagen
        image_tensor = self.preprocess_image(image_input)
        
        intermediate_features = []
        
        with torch.no_grad():
            # Acceder al visual transformer
            visual = self._model.visual
            
            # Patch embedding + position embedding
            x = visual.conv1(image_tensor.type(visual.conv1.weight.dtype))
            x = x.reshape(x.shape[0], x.shape[1], -1)  # (batch, hidden, grid**2)
            x = x.permute(0, 2, 1)  # (batch, grid**2, hidden)
            
            # Agregar class token
            x = torch.cat([
                visual.class_embedding.to(x.dtype) + 
                torch.zeros(x.shape[0], 1, x.shape[-1], dtype=x.dtype, device=x.device),
                x
            ], dim=1)
            
            # Agregar position embedding
            x = x + visual.positional_embedding.to(x.dtype)
            
            # Pre-LN
            x = visual.ln_pre(x)
            
            # Permutar para transformer: (seq_len, batch, hidden)
            x = x.permute(1, 0, 2)
            
            # Pasar por cada bloque del transformer y guardar intermedios
            for i, block in enumerate(visual.transformer.resblocks):
                x = block(x)
                
                if i in self.INTERMEDIATE_LAYERS:
                    # Guardar features de esta capa (solo class token)
                    layer_features = x[0, :, :]  # (batch, hidden)
                    intermediate_features.append(layer_features.clone())
        
        logger.debug(f"Features intermedias extraídas: {len(intermediate_features)} capas")
        return intermediate_features
    
    def get_feature_dim(self) -> int:
        """
        Retorna la dimensión de los features de CLIP ViT-L/14.
        
        Returns:
            768 para ViT-L/14
        """
        return 768
    
    @property
    def is_loaded(self) -> bool:
        """Indica si el modelo está cargado."""
        return self._loaded
