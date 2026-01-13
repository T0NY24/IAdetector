"""
Audio Forensics - Detección de Audio Sintético
UIDE Forense AI

Este módulo implementa la detección de voces generadas por IA
(ElevenLabs, RVC, TTS, etc.) usando modelos de HuggingFace.
"""

import logging
from typing import Dict, Any, Optional

import torch

import config
from core.processor import preprocess_audio

logger = logging.getLogger(__name__)


class AudioForensicsDetector:
    """
    Detector de audio sintético usando modelos de HuggingFace.
    
    Detecta voces generadas por:
    - ElevenLabs
    - RVC (Retrieval-based Voice Conversion)
    - Sistemas TTS modernos
    - Clonación de voz
    """

    def __init__(self):
        self.extractor = None
        self.model = None
        self._loaded = False
        self.device = torch.device(config.DEVICE)
        
        logger.info("🔊 AudioForensicsDetector inicializado")

    def _cargar_modelo(self):
        """Carga el modelo de detección de audio desde HuggingFace."""
        if self._loaded:
            return
        
        try:
            from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
            
            model_name = config.MODEL_AUDIO_NAME
            
            # ============================================
            # MENSAJE CLARO DE DESCARGA
            # ============================================
            print("\n" + "="*60)
            print("📥 DESCARGANDO MODELO DE DETECCIÓN DE AUDIO (HuggingFace)")
            print(f"   Modelo: {model_name}")
            print("   Esto puede tomar varios minutos la primera vez...")
            print("   (El modelo se cachea para futuras ejecuciones)")
            print("="*60 + "\n")
            
            logger.info(f"📥 Iniciando descarga del modelo de audio: {model_name}")
            
            # Cargar extractor de características
            print("   [1/2] Descargando extractor de características...")
            self.extractor = AutoFeatureExtractor.from_pretrained(model_name)
            logger.info("✅ Extractor de audio cargado")
            
            # Cargar modelo
            print("   [2/2] Descargando modelo de clasificación...")
            self.model = AutoModelForAudioClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            print("\n✅ Modelo de audio cargado exitosamente!\n")
            logger.info("✅ Modelo de audio cargado exitosamente")
            
            self._loaded = True
            
        except ImportError as e:
            logger.error("❌ transformers no instalado. Ejecuta: pip install transformers")
            raise
        except Exception as e:
            logger.error(f"❌ Error cargando modelo de audio: {e}")
            self._loaded = True  # Marcar como intentado
            raise

    def predict(self, audio_path: str) -> Dict[str, Any]:
        """
        Analiza un archivo de audio para detectar si es sintético.
        
        Args:
            audio_path: Ruta al archivo de audio
            
        Returns:
            Diccionario con score, verdict y detalles
        """
        logger.info(f"🔍 Iniciando análisis de audio: {audio_path}")
        
        try:
            # Cargar modelo si es necesario
            self._cargar_modelo()
            
            if self.model is None or self.extractor is None:
                logger.warning("⚠️ Modelo de audio no disponible")
                return {
                    "score": 50.0,
                    "verdict": "INDETERMINADO",
                    "confidence": 0.0,
                    "error": "Modelo no disponible",
                }
            
            # Preprocesar audio
            logger.info("   [1/2] Cargando y procesando audio...")
            audio_array, sr = preprocess_audio(audio_path, target_sr=config.AUDIO_SAMPLE_RATE)
            
            # Limitar duración si es necesario
            max_samples = config.AUDIO_MAX_DURATION * sr
            if len(audio_array) > max_samples:
                logger.info(f"   ⚠️ Audio truncado a {config.AUDIO_MAX_DURATION}s")
                audio_array = audio_array[:max_samples]
            
            # Extraer características
            logger.info("   [2/2] Analizando con modelo de IA...")
            inputs = self.extractor(
                audio_array, 
                sampling_rate=sr, 
                return_tensors="pt", 
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inferencia
            with torch.no_grad():
                logits = self.model(**inputs).logits
            
            probs = torch.softmax(logits, dim=-1)
            
            # Determinar índice de "fake"
            if hasattr(self.model.config, 'id2label'):
                id2label = self.model.config.id2label
                logger.debug(f"Labels del modelo: {id2label}")
                
                # Buscar índice de fake/synthetic
                fake_idx = None
                for idx, label in id2label.items():
                    label_lower = label.lower()
                    if any(kw in label_lower for kw in ['fake', 'spoof', 'synthetic', 'ai', 'cloned']):
                        fake_idx = int(idx)
                        break
                
                if fake_idx is None:
                    # Asumir índice 1 es fake
                    fake_idx = 1
            else:
                fake_idx = 1
            
            fake_prob = probs[0][fake_idx].item() * 100
            
            # Calcular confianza
            confidence = abs(fake_prob - 50) * 2  # 0-100%
            
            # Determinar veredicto
            if fake_prob > 60:
                verdict = "AUDIO SINTÉTICO"
            elif fake_prob > 40:
                verdict = "SOSPECHOSO"
            else:
                verdict = "HUMANO"
            
            result = {
                "score": fake_prob,
                "verdict": verdict,
                "confidence": confidence,
                "duration_analyzed": len(audio_array) / sr,
                "sample_rate": sr,
            }
            
            logger.info(f"✅ Análisis completado: {verdict} ({fake_prob:.2f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de audio: {e}", exc_info=True)
            return {
                "score": 50.0,
                "verdict": "ERROR",
                "confidence": 0.0,
                "error": str(e),
            }
