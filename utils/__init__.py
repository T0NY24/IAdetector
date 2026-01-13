"""
Utils - Utilidades y funciones auxiliares
UIDE Forense AI
"""

from .file_handlers import (
    validar_imagen,
    validar_video,
    validar_audio,
    generar_reporte_imagen,
    generar_reporte_video,
    generar_reporte_audio,
    generar_reporte_error,
    Timer,
)

from .plotting import (
    generar_grafico_temporal,
    generar_gauge_svg,
    generar_barra_progreso,
    generar_stat_card,
)

__all__ = [
    # File handlers
    'validar_imagen',
    'validar_video',
    'validar_audio',
    'generar_reporte_imagen',
    'generar_reporte_video',
    'generar_reporte_audio',
    'generar_reporte_error',
    'Timer',
    # Plotting
    'generar_grafico_temporal',
    'generar_gauge_svg',
    'generar_barra_progreso',
    'generar_stat_card',
]
