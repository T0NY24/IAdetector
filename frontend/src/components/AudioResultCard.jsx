import { AlertTriangle, Bot, AlertCircle, User, Lightbulb } from 'lucide-react';
import './AudioResultCard.css';

/**
 * Tarjeta de resultados para análisis de audio (Synthetic Audio Detection).
 */
function AudioResultCard({ result }) {
    if (!result) return null;

    const hasError = result.error;
    const score = result.score || 0;
    const verdict = result.verdict;

    // Determinar color y estilo según resultado
    const getVerdictStyle = () => {
        if (hasError) return { color: '#6b7280', bg: '#f9fafb', border: '#e5e7eb', Icon: AlertTriangle };
        if (verdict === 'AUDIO SINTÉTICO') return { color: '#dc2626', bg: '#fef2f2', border: '#fca5a5', Icon: Bot };
        if (verdict === 'SOSPECHOSO') return { color: '#f59e0b', bg: '#fffbeb', border: '#fcd34d', Icon: AlertCircle };
        return { color: '#16a34a', bg: '#f0fdf4', border: '#86efac', Icon: User };
    };

    const style = getVerdictStyle();
    const Icon = style.Icon;

    return (
        <div className="result-card">
            {/* Header con veredicto */}
            <div className="verdict-box" style={{ background: style.bg, borderColor: style.border }}>
                <div className="verdict-emoji">
                    <Icon size={32} color={style.color} />
                </div>
                <div>
                    <h2 className="verdict-title" style={{ color: style.color }}>
                        {hasError ? 'ERROR' : verdict || 'INDETERMINADO'}
                    </h2>
                    {!hasError && (
                        <p className="verdict-probability">Score de Síntesis: {score.toFixed(1)}%</p>
                    )}
                </div>
            </div>

            {/* Error message */}
            {hasError && (
                <div className="error-section">
                    <p>{result.error}</p>
                </div>
            )}

            {/* Detalles del análisis */}
            {!hasError && (
                <div className="details-grid">
                    <div className="detail-item">
                        <span className="detail-label">Confianza</span>
                        <span className="detail-value">{result.confidence?.toFixed(1) || 0}%</span>
                    </div>
                    <div className="detail-item">
                        <span className="detail-label">Duración Analizada</span>
                        <span className="detail-value">{result.duration_analyzed?.toFixed(1) || 0}s</span>
                    </div>
                    <div className="detail-item">
                        <span className="detail-label">Sample Rate</span>
                        <span className="detail-value">{result.sample_rate || 16000} Hz</span>
                    </div>
                </div>
            )}

            {/* Interpretación */}
            {!hasError && (
                <div className="interpretation-box">
                    <h3 className="interpretation-title">
                        <Lightbulb size={20} style={{ marginRight: '0.5rem' }} />
                        Interpretación
                    </h3>
                    <p className="interpretation-text">
                        {verdict === 'AUDIO SINTÉTICO'
                            ? `El análisis detectó patrones característicos de audio generado por IA (ElevenLabs, RVC, TTS, etc.). Score de síntesis: ${score.toFixed(0)}%.`
                            : verdict === 'SOSPECHOSO'
                                ? `El audio presenta características ambiguas. Se recomienda revisión manual. Score: ${score.toFixed(0)}%.`
                                : `El audio parece ser voz humana auténtica. No se detectaron patrones de síntesis por IA. Score: ${score.toFixed(0)}%.`}
                    </p>
                </div>
            )}
        </div>
    );
}

export default AudioResultCard;
