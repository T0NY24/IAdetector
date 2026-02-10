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
        self.device = torch.device(config.DEVICE)
        logger.info("🔊 AudioForensicsDetector inicializado (Modo Heurístico)")
        logger.info("   📊 Usando análisis espectral sin modelo pesado")

    def _extract_spectral_features(self, audio_array, sr):
        """
        Extrae características espectrales del audio para detección heurística.
        
        Returns:
            Dict con features y score de artificialidad (0-100)
        """
        import librosa
        import numpy as np
        
        # 1. MFCCs (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=audio_array, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        
        # 2. Zero Crossing Rate (voces sintéticas tienden a tener patrones diferentes)
        zcr = librosa.feature.zero_crossing_rate(audio_array)[0]
        zcr_mean = np.mean(zcr)
        zcr_std = np.std(zcr)
        
        # 3. Spectral Contrast (diferencias entre picos y valles en espectro)
        contrast = librosa.feature.spectral_contrast(y=audio_array, sr=sr)
        contrast_mean = np.mean(contrast, axis=1)
        
        # 4. Spectral Rolloff (frecuencia donde 85% de energía está debajo)
        rolloff = librosa.feature.spectral_rolloff(y=audio_array, sr=sr)[0]
        rolloff_mean = np.mean(rolloff)
        
        # 5. Spectral Centroid (centro de masa del espectro)
        centroid = librosa.feature.spectral_centroid(y=audio_array, sr=sr)[0]
        centroid_mean = np.mean(centroid)
        centroid_std = np.std(centroid)
        
        # HEURÍSTICAS PARA DETECCIÓN
        synthetic_score = 0.0
        reasons = []
        
        # Heurística 1: MFCCs muy uniformes (TTS tiene menos variación natural)
        mfcc_uniformity = np.mean(mfcc_std)
        if mfcc_uniformity < 15:  # Umbral empírico
            synthetic_score += 25
            reasons.append(f"MFCCs muy uniformes ({mfcc_uniformity:.1f})")
        
        # Heurística 2: Zero-crossing muy regular
        if zcr_std < 0.02:  # Poca variación en ZCR
            synthetic_score += 20
            reasons.append(f"ZCR muy regular ({zcr_std:.3f})")
        
        # Heurística 3: Spectral contrast anormal (voces sintéticas tienen patrones diferentes)
        contrast_score = np.mean(contrast_mean)
        if contrast_score > 30 or contrast_score < 15:
            synthetic_score += 20
            reasons.append(f"Contraste espectral anómalo ({contrast_score:.1f})")
        
        # Heurística 4: Spectral centroid muy estable (menos prosody natural)
        if centroid_std < 200:
            synthetic_score += 20
            reasons.append(f"Centroide muy estable ({centroid_std:.1f})")
        
        # Heurística 5: Rolloff anormal
        if rolloff_mean > 4000 or rolloff_mean < 1500:
            synthetic_score += 15
            reasons.append(f"Rolloff anómalo ({rolloff_mean:.0f} Hz)")
        
        return {
            'synthetic_score': min(synthetic_score, 100),
            'reasons': reasons,
            'features': {
                'mfcc_uniformity': float(mfcc_uniformity),
                'zcr_std': float(zcr_std),
                'contrast_mean': float(contrast_score),
                'centroid_std': float(centroid_std),
                'rolloff_mean': float(rolloff_mean)
            }
        }

    def predict(self, audio_path: str) -> Dict[str, Any]:
        """
        Analiza un archivo de audio para detectar si es sintético usando análisis espectral.
        
        Args:
            audio_path: Ruta al archivo de audio
            
        Returns:
            Diccionario con score, verdict y detalles
        """
        logger.info(f"🔍 Iniciando análisis de audio: {audio_path}")
        
        try:
            # Preprocesar audio
            logger.info("   [1/2] Cargando y procesando audio...")
            audio_array, sr = preprocess_audio(audio_path, target_sr=config.AUDIO_SAMPLE_RATE)
            
            # Limitar duración si es necesario
            max_samples = config.AUDIO_MAX_DURATION * sr
            if len(audio_array) > max_samples:
                logger.info(f"   ⚠️ Audio truncado a {config.AUDIO_MAX_DURATION}s")
                audio_array = audio_array[:max_samples]
            
            # Extraer features espectrales y calcular score
            logger.info("   [2/2] Analizando características espectrales...")
            analysis = self._extract_spectral_features(audio_array, sr)
            
            fake_prob = analysis['synthetic_score']
            
            # Calcular confianza basada en cuántas heurísticas activadas
            num_reasons = len(analysis['reasons'])
            confidence = min(num_reasons * 20, 100)  # Más razones = más confianza
            
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
                "features": analysis['features'],
                "detection_reasons": analysis['reasons']
            }
            
            logger.info(f"✅ Análisis completado: {verdict} ({fake_prob:.2f}%)")
            if analysis['reasons']:
                logger.info(f"   📋 Razones: {', '.join(analysis['reasons'])}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de audio: {e}", exc_info=True)
            return {
                "score": 50.0,
                "verdict": "ERROR",
                "confidence": 0.0,
                "error": str(e),
            }

