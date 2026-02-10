"""
FFT Frequency Expert - UIDE Forense AI
V12.0: The Trinity Judgment
Busca la 'Rejilla Invisible' que dejan los generadores de IA.
"""
import numpy as np
import cv2
from PIL import Image

from .schemas import ExpertResult


class FFTExpert:
    """
    Detector de Artefactos de Frecuencia (V12.0).
    Analiza el espectro de Fourier para detectar patrones artificiales.
    
    Teoría:
    - Fotos reales: espectro caótico/orgánico (score bajo)
    - IA generada: patrones de rejilla regulares (score alto)
    """
    
    def __init__(self):
        pass

    def analyze(self, image) -> ExpertResult:
        """
        Analiza el espectro de frecuencia de la imagen.
        
        Returns:
            ExpertResult con score 0.0-1.0:
            - < 0.50: Orgánico (Real)
            - > 0.60: Patrón Artificial (IA)
        """
        try:
            # Convertir PIL Image a numpy array
            if isinstance(image, Image.Image):
                img_np = np.array(image)
            else:
                img_np = image
            
            # Convertir a escala de grises
            if len(img_np.shape) == 3:
                img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            else:
                img_gray = img_np
            
            # Transformada de Fourier 2D
            f = np.fft.fft2(img_gray)
            fshift = np.fft.fftshift(f)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)

            # Análisis de Anomalías
            rows, cols = img_gray.shape
            crow, ccol = rows // 2, cols // 2
            
            # Ignoramos el centro (frecuencias bajas naturales)
            mask_r = 30
            magnitude_spectrum[crow-mask_r:crow+mask_r, ccol-mask_r:ccol+mask_r] = 0

            # Calculamos la energía en alta frecuencia
            # Las IAs suelen dejar picos brillantes aquí (patrones de rejilla)
            mean_energy = np.mean(magnitude_spectrum)
            
            # Normalización empírica basada en observaciones:
            # Fotos reales: 4.0 - 7.0
            # IAs generadas: 9.0 - 14.0
            # Mapeamos esto a 0.0 - 1.0
            
            score = (mean_energy - 5.0) / 10.0
            score = max(0.0, min(1.0, score))
            
            evidence = [f"Energía FFT: {mean_energy:.2f}"]
            
            return ExpertResult(
                name="FFT Frequency",
                score=score,
                confidence=1.0,
                evidence=evidence,
                raw_data={"mean_energy": mean_energy}
            )
            
        except Exception as e:
            # Fallback en caso de error
            return ExpertResult(
                name="FFT Frequency",
                score=0.5,
                confidence=0.0,
                evidence=[f"Error en análisis FFT: {str(e)}"],
                raw_data={"error": str(e)}
            )
