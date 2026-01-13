"""
Plotting - Generación de gráficos y visualizaciones
UIDE Forense AI

Este módulo contiene funciones para generar gráficos SVG,
medidores visuales y líneas de tiempo para reportes.
"""

import io
import logging
from typing import List, Tuple, Optional
from PIL import Image

# Matplotlib backend setup for headless environment
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import config

logger = logging.getLogger(__name__)


def generar_gauge_svg(probabilidad: float, color: str, tamaño: int = 200) -> str:
    """
    Genera un medidor circular SVG animado.
    
    Args:
        probabilidad: Valor de 0 a 100
        color: Color en formato hex
        tamaño: Tamaño del medidor en píxeles
        
    Returns:
        String con el SVG del medidor
    """
    # Calcular el stroke-dashoffset para la animación circular
    circunferencia = 2 * 3.14159 * 70  # radio = 70
    offset = circunferencia - (probabilidad / 100 * circunferencia)
    
    return f"""
    <svg width="{tamaño}" height="{tamaño}" viewBox="0 0 200 200" style="transform: rotate(-90deg);">
        <circle cx="100" cy="100" r="70" fill="none" stroke="#e5e7eb" stroke-width="12"/>
        <circle cx="100" cy="100" r="70" fill="none" stroke="{color}" stroke-width="12"
                stroke-dasharray="{circunferencia}" stroke-dashoffset="{offset}"
                stroke-linecap="round" style="transition: stroke-dashoffset 1s ease;">
        </circle>
        <text x="100" y="110" text-anchor="middle" font-size="32" font-weight="bold" 
              fill="{color}" style="transform: rotate(90deg); transform-origin: center;">
            {probabilidad:.1f}%
        </text>
    </svg>
    """


def generar_barra_progreso(probabilidad: float, color: str) -> str:
    """
    Genera una barra de progreso animada HTML/CSS.
    
    Args:
        probabilidad: Valor de 0 a 100
        color: Color en formato hex
        
    Returns:
        String con el HTML de la barra
    """
    return f"""
    <div style="background-color: #e5e7eb; height: 20px; border-radius: 10px; width: 100%; overflow: hidden; margin: 15px 0;">
        <div style="background: linear-gradient(90deg, {color}, {color}dd); height: 100%; border-radius: 10px; 
                    width: {probabilidad}%; transition: width 1.5s ease; box-shadow: 0 0 10px {color}88;">
        </div>
    </div>
    """


def generar_stat_card(valor, etiqueta: str, icono: str = "📊") -> str:
    """
    Genera una tarjeta de estadística con gradiente.
    
    Args:
        valor: Valor a mostrar
        etiqueta: Etiqueta descriptiva
        icono: Emoji o icono
        
    Returns:
        String con el HTML de la tarjeta
    """
    return f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 12px; text-align: center; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.1); min-width: 150px;">
        <div style="font-size: 2.5em; margin-bottom: 5px;">{icono}</div>
        <div style="font-size: 2em; font-weight: bold; color: white; margin-bottom: 5px;">{valor}</div>
        <div style="font-size: 0.9em; color: rgba(255,255,255,0.9); text-transform: uppercase; letter-spacing: 1px;">
            {etiqueta}
        </div>
    </div>
    """


def generar_grafico_temporal(predicciones_por_frame: List[Tuple[int, float]]) -> Optional[Image.Image]:
    """
    Genera un gráfico de línea temporal de probabilidades de fake.

    Args:
        predicciones_por_frame: Lista de tuplas (frame_idx, probabilidad)

    Returns:
        Imagen PIL del gráfico o None si hay error
    """
    try:
        if not predicciones_por_frame:
            return None

        frames = [p[0] for p in predicciones_por_frame]
        probs = [p[1] for p in predicciones_por_frame]

        plt.figure(figsize=(10, 4))
        plt.plot(frames, probs, color=config.COLOR_FAKE, linewidth=2, label="Probabilidad Fake")
        plt.axhline(y=config.VIDEO_THRESHOLD, color='gray', linestyle='--', alpha=0.5, label="Umbral")

        plt.fill_between(frames, probs, alpha=0.1, color=config.COLOR_FAKE)

        plt.title("Línea de Tiempo de Detección de Deepfakes")
        plt.xlabel("Frame")
        plt.ylabel("Probabilidad (%)")
        plt.ylim(0, 105)  # Un poco más de 100 para margen
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()  # Liberar memoria
        buf.seek(0)

        return Image.open(buf)
    except Exception as e:
        logger.error(f"Error generando gráfico: {e}", exc_info=True)
        return None


def generar_espectrograma_imagen(mel_spec_db, sr: int = 16000) -> Optional[Image.Image]:
    """
    Genera una imagen del espectrograma Mel para visualización de audio.
    
    Args:
        mel_spec_db: Espectrograma Mel en dB (numpy array)
        sr: Sample rate
        
    Returns:
        Imagen PIL del espectrograma
    """
    try:
        import librosa.display
        
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(
            mel_spec_db, 
            sr=sr, 
            x_axis='time', 
            y_axis='mel',
            cmap='magma'
        )
        plt.colorbar(format='%+2.0f dB')
        plt.title('Espectrograma Mel')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        buf.seek(0)
        
        return Image.open(buf)
    except Exception as e:
        logger.error(f"Error generando espectrograma: {e}")
        return None
