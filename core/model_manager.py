"""
Model Manager - Gestión centralizada de modelos de Deep Learning
UIDE Forense AI

Este módulo maneja la carga y gestión de todos los modelos del sistema
con soporte para lazy loading y manejo robusto de errores.
"""

import os
import logging
from typing import Optional

import torch
import torch.nn as nn
from torchvision import models, transforms
import timm

import config

# Configurar logging
logger = logging.getLogger(__name__)


class ModelManager:
    """
    Gestor centralizado de modelos con caché y manejo robusto de errores.
    Implementa lazy loading para optimizar el uso de memoria.
    """

    def __init__(self):
        self.modelo_imagen_gan: Optional[nn.Module] = None
        self.modelo_video: Optional[nn.Module] = None
        self.dispositivo = torch.device(config.DEVICE)
        
        # Estado de carga
        self._imagen_gan_cargado = False
        self._video_cargado = False

        # Transformaciones de imagen (CNNDetection - ResNet50)
        self.transform_imagen = transforms.Compose([
            transforms.Resize(config.TRANSFORMS_RESIZE),
            transforms.CenterCrop(config.TRANSFORMS_CROP),
            transforms.ToTensor(),
            transforms.Normalize(
                config.TRANSFORMS_MEAN,
                config.TRANSFORMS_STD,
            ),
        ])

        # Transformaciones de video (Xception)
        self.transform_video = transforms.Compose([
            transforms.Resize((config.VIDEO_SIZE, config.VIDEO_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize([0.5] * 3, [0.5] * 3),
        ])

        logger.info("📦 ModelManager inicializado (lazy loading activado)")

    def cargar_modelo_imagen_gan(self) -> Optional[nn.Module]:
        """
        Carga el modelo de detección de imágenes GAN (ResNet50 Modificado).
        Usa lazy loading - solo carga cuando se necesita.
        """
        if self._imagen_gan_cargado:
            return self.modelo_imagen_gan
            
        logger.info("🖼️ Cargando modelo de imágenes GAN (ResNet50)...")

        try:
            model_path = config.MODEL_IMAGE_PATH
            if not os.path.exists(model_path):
                logger.warning(
                    f"⚠️ No se encontró el modelo en: {model_path}"
                )
                logger.warning("📥 Modo demostración activado para imágenes GAN")
                self._imagen_gan_cargado = True
                return None

            # 1. Cargar arquitectura base ResNet50
            model = models.resnet50(pretrained=False)

            # 2. Modificar última capa para 1 salida (Real vs Fake)
            num_ftrs = model.fc.in_features
            model.fc = nn.Linear(num_ftrs, 1)

            # 3. Cargar los pesos
            logger.info(f"📂 Leyendo pesos desde {model_path}")
            state_dict = torch.load(model_path, map_location=self.dispositivo)

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

            self.modelo_imagen_gan = model
            self._imagen_gan_cargado = True
            logger.info("✅ Modelo GAN de imágenes cargado exitosamente")
            return model

        except Exception as e:
            logger.error(
                f"❌ Error cargando modelo de imágenes GAN: {e}",
                exc_info=True,
            )
            logger.warning("📥 Usando modo demostración para imágenes GAN")
            self._imagen_gan_cargado = True
            return None

    def cargar_modelo_video(self) -> Optional[nn.Module]:
        """
        Carga el modelo de detección de deepfakes en video (Xception).
        Usa lazy loading - solo carga cuando se necesita.
        """
        if self._video_cargado:
            return self.modelo_video
            
        logger.info("🎥 Cargando modelo de video (XceptionNet)...")

        try:
            modelo = timm.create_model(
                config.MODEL_VIDEO_NAME,
                pretrained=True,
                num_classes=2,
            )
            modelo.to(self.dispositivo)
            modelo.eval()

            self.modelo_video = modelo
            self._video_cargado = True
            logger.info("✅ Modelo de video cargado exitosamente")
            return modelo

        except Exception as e:
            logger.error(
                f"❌ Error cargando modelo de video: {e}",
                exc_info=True,
            )
            logger.warning("📥 Modo demostración activado para videos")
            self._video_cargado = True
            return None

    def get_dispositivo(self) -> torch.device:
        """Retorna el dispositivo configurado (CPU/CUDA)."""
        return self.dispositivo


# Singleton global del gestor de modelos
_model_manager_instance: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """
    Obtiene la instancia singleton del ModelManager.
    Crea una nueva instancia si no existe.
    """
    global _model_manager_instance
    if _model_manager_instance is None:
        _model_manager_instance = ModelManager()
    return _model_manager_instance
