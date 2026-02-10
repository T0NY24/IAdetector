"""
Detector - Orquestador principal del módulo de análisis forense de imágenes.

UIDE Forense AI v3.0+
Clean Architecture - Capa de Aplicación (Facade)

Este es el punto de entrada principal al módulo.
Coordina todos los componentes internos y expone una API simple.

Expertos disponibles:
- multiLID: Análisis geométrico del espacio de features
- UFD: Clasificador visual universal
- Semantic: Análisis de plausibilidad semántica (NUEVO)

Uso:
    from modules.image_forensics import ImageForensicsDetector
    
    detector = ImageForensicsDetector()
    result = detector.analyze(image)
    print(result.to_dict())
"""

import logging
from typing import Optional, Union
from pathlib import Path

import numpy as np
from PIL import Image

from .schemas import ForensicResult, AnalysisContext
from .feature_extractor import CLIPFeatureExtractor
from .multilid_expert import MultiLIDExpert
from .ufd_expert import UFDExpert
from .semantic_expert import SemanticForensicsExpert
from .fusion_engine import FusionEngine

import config

logger = logging.getLogger(__name__)


class ImageForensicsDetector:
    """
    Detector principal de imágenes sintéticas.
    
    Orquesta el pipeline completo de análisis forense:
    1. Extracción de features con CLIP ViT-L/14
    2. Análisis geométrico con multiLID
    3. Clasificación visual con UFD
    4. Análisis de plausibilidad semántica (opcional pero recomendado)
    5. Fusión de evidencias con lógica jerárquica
    
    Implementa el patrón Facade para ocultar la complejidad interna
    y proporcionar una API simple para el frontend (Gradio).
    
    Características:
    - Lazy loading de todos los componentes
    - Semantic Expert con alta prioridad para casos "NO CONCLUYENTE"
    - Manejo robusto de errores
    - Logging detallado para debugging
    - Output estructurado y explicable
    
    Attributes:
        device: Dispositivo para inferencia ("cpu" o "cuda")
        enable_semantic: Si habilitar el experto semántico
        
    Example:
        detector = ImageForensicsDetector()
        result = detector.analyze("path/to/image.jpg")
        
        # Output:
        # {
        #     "verdict": "PROBABLEMENTE SINTÉTICA",
        #     "confidence": "ALTA",
        #     "scores": {"multiLID": 0.72, "UFD": 0.68, "Semantic": 0.65},
        #     "evidence": [...],
        #     "notes": "..."
        # }
    """
    
    def __init__(
        self, 
        device: Optional[str] = None,
        enable_semantic: bool = True
    ):
        """
        Inicializa el detector.
        
        Args:
            device: Dispositivo para inferencia. Si no se especifica,
                   usa el valor de config.DEVICE
            enable_semantic: Habilitar experto semántico (recomendado: True)
        """
        self.device = device or getattr(config, 'DEVICE', 'cpu')
        self.enable_semantic = enable_semantic
        
        # Componentes (lazy loading)
        self._extractor: Optional[CLIPFeatureExtractor] = None
        self._multilid: Optional[MultiLIDExpert] = None
        self._ufd: Optional[UFDExpert] = None
        self._semantic: Optional[SemanticForensicsExpert] = None
        self._fusion: Optional[FusionEngine] = None
        
        self._initialized = False
        
        logger.info(f"🕵️ ImageForensicsDetector v3.0+ inicializado (device={self.device}, semantic={enable_semantic})")
    
    def _lazy_load(self) -> None:
        """
        Carga todos los componentes de forma diferida.
        
        Se ejecuta solo la primera vez que se llama a analyze().
        Esto permite que el detector se instancie rápidamente
        sin cargar modelos pesados.
        """
        if self._initialized:
            return
        
        logger.info("🔧 Inicializando componentes del detector...")
        
        n_components = 5 if self.enable_semantic else 4
        
        print("\n" + "=" * 60)
        print("🕵️ UIDE FORENSE AI - DETECTOR DE IMÁGENES v3.0+")
        print("   Inicializando sistema de análisis forense...")
        if self.enable_semantic:
            print("   📍 Incluye: Semantic Expert (análisis de plausibilidad)")
        print("=" * 60 + "\n")
        
        # 1. Feature Extractor (backbone compartido)
        print(f"📦 [1/{n_components}] Inicializando extractor de features CLIP...")
        self._extractor = CLIPFeatureExtractor(device=self.device)
        
        # 2. multiLID Expert
        print(f"📦 [2/{n_components}] Inicializando experto multiLID...")
        k_neighbors = getattr(config, 'LID_K_NEIGHBORS', 20)
        self._multilid = MultiLIDExpert(
            feature_extractor=self._extractor,
            k_neighbors=k_neighbors
        )
        
        # 3. UFD Expert
        print(f"📦 [3/{n_components}] Inicializando experto UFD...")
        self._ufd = UFDExpert(feature_extractor=self._extractor)
        
        # 4. Semantic Expert (opcional pero recomendado)
        if self.enable_semantic:
            print(f"📦 [4/{n_components}] Inicializando experto Semantic...")
            self._semantic = SemanticForensicsExpert(
                feature_extractor=self._extractor
            )
        
        # 5. Fusion Engine
        print(f"📦 [{n_components}/{n_components}] Inicializando motor de fusión...")
        self._fusion = FusionEngine(semantic_priority=self.enable_semantic)
        
        self._initialized = True
        
        print("\n✅ Sistema de análisis forense listo!\n")
        logger.info("✅ Todos los componentes inicializados")
    
    def _preprocess_input(
        self, 
        image_input: Union[str, Path, np.ndarray, Image.Image]
    ) -> Image.Image:
        """
        Preprocesa la entrada a formato PIL Image.
        
        Args:
            image_input: Varios formatos soportados
            
        Returns:
            PIL Image en modo RGB
            
        Raises:
            ValueError: Si el formato no es soportado
        """
        if isinstance(image_input, (str, Path)):
            # Path a archivo
            path = Path(image_input)
            if not path.exists():
                raise ValueError(f"Archivo no encontrado: {path}")
            return Image.open(path).convert("RGB")
        
        elif isinstance(image_input, np.ndarray):
            # Numpy array
            if image_input.ndim == 2:
                # Grayscale
                return Image.fromarray(image_input).convert("RGB")
            elif image_input.ndim == 3:
                if image_input.shape[2] == 4:
                    # RGBA
                    return Image.fromarray(image_input[:, :, :3]).convert("RGB")
                else:
                    return Image.fromarray(image_input).convert("RGB")
            else:
                raise ValueError(f"Numpy array con dimensiones no soportadas: {image_input.shape}")
        
        elif isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        
        else:
            raise TypeError(f"Tipo de entrada no soportado: {type(image_input)}")
    
    def analyze(
        self, 
        image_input: Union[str, Path, np.ndarray, Image.Image]
    ) -> ForensicResult:
        """
        Analiza una imagen y produce un resultado forense completo.
        
        Pipeline de análisis:
        1. Preprocesar input a PIL Image
        2. Extraer features de CLIP
        3. Ejecutar análisis multiLID (geométrico)
        4. Ejecutar análisis UFD (visual)
        5. Ejecutar análisis Semantic (plausibilidad) si está habilitado
        6. Fusionar evidencias con lógica jerárquica
        7. Generar resultado final
        
        Args:
            image_input: Imagen a analizar. Soporta:
                - str/Path: Ruta a archivo de imagen
                - numpy.ndarray: Array de imagen (HxWxC)
                - PIL.Image: Imagen PIL
        
        Returns:
            ForensicResult con veredicto, confianza, scores y evidencia
            
        Raises:
            ValueError: Si la imagen no puede ser procesada
            
        Example:
            result = detector.analyze("suspicious_image.jpg")
            print(result.verdict)  # "PROBABLEMENTE SINTÉTICA"
            print(result.to_dict())
        """
        logger.info("=" * 50)
        logger.info("🔍 INICIANDO ANÁLISIS FORENSE DE IMAGEN")
        logger.info("=" * 50)
        
        try:
            # Lazy loading de componentes
            self._lazy_load()
            
            # Preprocesar input
            logger.info("📷 Preprocesando imagen...")
            image = self._preprocess_input(image_input)
            logger.info(f"   Tamaño: {image.size}")
            
            # Análisis multiLID
            logger.info("🔬 Ejecutando análisis multiLID...")
            multilid_result = self._multilid.analyze(image)
            logger.info(f"   Score: {multilid_result.score:.2f}")
            
            # Análisis UFD
            logger.info("🎯 Ejecutando análisis UFD...")
            ufd_result = self._ufd.analyze(image)
            logger.info(f"   Score: {ufd_result.score:.2f}")
            
            # Análisis Semantic (si está habilitado)
            semantic_result = None
            if self.enable_semantic and self._semantic:
                logger.info("🧠 Ejecutando análisis Semantic...")
                semantic_result = self._semantic.analyze(image)
                logger.info(f"   Score: {semantic_result.score:.2f}")
            
            # Fusión de evidencias
            logger.info("⚗️ Fusionando evidencias...")
            result = self._fusion.fuse(multilid_result, ufd_result, semantic_result)
            
            logger.info("=" * 50)
            logger.info(f"✅ ANÁLISIS COMPLETADO: {result.verdict}")
            logger.info(f"   Confianza: {result.confidence}")
            logger.info("=" * 50)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en análisis: {e}", exc_info=True)
            
            # Retornar resultado de error estructurado
            return ForensicResult(
                verdict="ERROR",
                confidence="N/A",
                scores={"multiLID": 0.0, "UFD": 0.0, "Semantic": 0.0},
                evidence=[f"⚠️ Error durante el análisis: {str(e)}"],
                notes="El análisis no pudo completarse debido a un error. "
                      "Verifique que la imagen sea válida y los modelos estén disponibles."
            )
    
    def analyze_dict(
        self, 
        image_input: Union[str, Path, np.ndarray, Image.Image]
    ) -> dict:
        """
        Analiza una imagen y retorna resultado como diccionario.
        
        Convenience method para uso en Gradio y serialización JSON.
        
        Args:
            image_input: Imagen a analizar
            
        Returns:
            Dict con estructura del output esperado
        """
        result = self.analyze(image_input)
        return result.to_dict()
    
    @property
    def is_initialized(self) -> bool:
        """Indica si el detector está completamente inicializado."""
        return self._initialized
    
    def get_model_info(self) -> dict:
        """
        Retorna información sobre los modelos cargados.
        
        Returns:
            Dict con información de versiones y configuración
        """
        components = {
            "feature_extractor": "CLIP ViT-L/14",
            "multilid": {
                "k_neighbors": getattr(config, 'LID_K_NEIGHBORS', 20),
                "layers": CLIPFeatureExtractor.INTERMEDIATE_LAYERS
            },
            "ufd": "UniversalFakeDetect (Linear Classifier)",
            "fusion": "Hierarchical Logic Fusion with Semantic Priority"
        }
        
        if self.enable_semantic:
            components["semantic"] = {
                "enabled": True,
                "sub_scores": ["improbability", "collision", "composition"],
                "priority": "HIGH (Level 0)"
            }
        
        return {
            "version": "3.0+",
            "device": self.device,
            "initialized": self._initialized,
            "semantic_enabled": self.enable_semantic,
            "components": components,
            "references": [
                "Ojha et al., CVPR 2023 - UniversalFakeDetect",
                "Radford et al., 2021 - CLIP",
                "Ma et al., ICLR 2018 - LID",
                "Semantic Forensic Analysis - UIDE 2026"
            ]
        }
