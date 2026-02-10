import './VideoResultCard.css';

/**
 * Tarjeta de resultados para análisis de video (Deepfake Detection).
 */
function VideoResultCard({ result }) {
    if (!result) return null;

    const hasError = result.error;
    const isDeepfake = result.is_deepfake;
    const probability = result.probability || 0;

    // Determinar color y estilo según resultado
    const getVerdictStyle = () => {
        if (hasError) return { color: '#6b7280', bg: '#f9fafb', border: '#e5e7eb', emoji: '❌' };
        if (isDeepfake) return { color: '#dc2626', bg: '#fef2f2', border: '#fca5a5', emoji: '🚨' };
        return { color: '#16a34a', bg: '#f0fdf4', border: '#86efac', emoji: '✅' };
    };

    const style = getVerdictStyle();

    return (
        <div className="result-card">
            {/* Header con veredicto */}
            <div className="verdict-box" style={{ background: style.bg, borderColor: style.border }}>
                <span className="verdict-emoji">{style.emoji}</span>
                <div>
                    <h2 className="verdict-title" style={{ color: style.color }}>
                        {hasError ? 'ERROR' : result.verdict || (isDeepfake ? 'DEEPFAKE' : 'REAL')}
                    </h2>
                    {!hasError && (
                        <p className="verdict-probability">Probabilidad: {probability.toFixed(1)}%</p>
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
                        <span className="detail-label">Frames Analizados</span>
                        <span className="detail-value">{result.frames_analyzed || 0} / {result.frames_total || 0}</span>
                    </div>
                    <div className="detail-item">
                        <span className="detail-label">Duración</span>
                        <span className="detail-value">{result.duration?.toFixed(1) || 0}s</span>
                    </div>
                    <div className="detail-item">
                        <span className="detail-label">Probabilidad Máxima</span>
                        <span className="detail-value">{result.max_probability?.toFixed(1) || probability.toFixed(1)}%</span>
                    </div>
                </div>
            )}

            {/* Interpretación */}
            {!hasError && (
                <div className="interpretation-box">
                    <h3 className="interpretation-title">💡 Interpretación</h3>
                    <p className="interpretation-text">
                        {isDeepfake
                            ? `El análisis detectó anomalías faciales consistentes con manipulación por IA. El modelo XceptionNet identificó patrones de deepfake en ${probability.toFixed(0)}% de los frames analizados.`
                            : `El video parece auténtico. No se detectaron patrones característicos de deepfakes. La probabilidad de manipulación es baja (${probability.toFixed(0)}%).`}
                    </p>
                </div>
            )}
        </div>
    );
}

export default VideoResultCard;
