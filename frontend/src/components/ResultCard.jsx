import './ResultCard.css';

function ResultCard({ result }) {
    if (!result) return null;

    const { verdict, confidence, scores, evidence, processing_time } = result;

    const isFake = verdict.includes('GENERADA') || verdict.includes('IA');
    const isReal = verdict.includes('REAL');
    const verdictClass = isFake ? 'verdict-fake' : isReal ? 'verdict-real' : 'verdict-inconclusive';

    return (
        <div className={`result-card ${verdictClass}`}>
            {/* Header */}
            <div className="result-header">
                <h2>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
                    </svg>
                    Informe Forense
                </h2>
                {processing_time && (
                    <span className="processing-time">PROCESADO EN {processing_time}s</span>
                )}
            </div>

            {/* Veredicto Principal */}
            <div className="verdict-panel">
                <div className="verdict-label">CONCLUSIÓN DEL SISTEMA</div>
                <div className="verdict-text">{verdict}</div>
                <div className="confidence-badge">
                    <span>CONFIANZA {confidence}</span>
                </div>
            </div>

            <div className="details-grid">
                {/* Columna de Scores */}
                <div className="scores-column">
                    <h3>Métricas de Detección</h3>
                    <div className="scores-list">
                        {scores.multiLID !== undefined && (
                            <div className="score-row">
                                <div className="score-info">
                                    <span className="score-name">Análisis Dimensional (multiLID)</span>
                                    <span className="score-num">{(scores.multiLID * 100).toFixed(1)}%</span>
                                </div>
                                <div className="progress-track">
                                    <div className="progress-fill" style={{ width: `${scores.multiLID * 100}%` }}></div>
                                </div>
                            </div>
                        )}

                        {scores.UFD !== undefined && (
                            <div className="score-row">
                                <div className="score-info">
                                    <span className="score-name">Detector Universal (UFD)</span>
                                    <span className="score-num">{(scores.UFD * 100).toFixed(1)}%</span>
                                </div>
                                <div className="progress-track">
                                    <div className="progress-fill" style={{ width: `${scores.UFD * 100}%` }}></div>
                                </div>
                            </div>
                        )}

                        {scores.Semantic !== undefined && (
                            <div className="score-row">
                                <div className="score-info">
                                    <span className="score-name">Análisis Semántico (DeepSeek)</span>
                                    <span className="score-num">{(scores.Semantic * 100).toFixed(1)}%</span>
                                </div>
                                <div className="progress-track">
                                    <div className="progress-fill" style={{ width: `${scores.Semantic * 100}%`, backgroundColor: 'var(--color-success)' }}></div>
                                </div>
                            </div>
                        )}

                        {scores.final_score !== undefined && (
                            <div className="score-row highlight">
                                <div className="score-info">
                                    <span className="score-name">Score Unificado</span>
                                    <span className="score-num">{(scores.final_score * 100).toFixed(1)}%</span>
                                </div>
                                <div className="progress-track">
                                    <div className="progress-fill" style={{ width: `${scores.final_score * 100}%` }}></div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Columna de Evidencias */}
                {evidence && evidence.length > 0 && (
                    <div className="evidence-column">
                        <h3>Evidencia Técnica</h3>
                        <div className="evidence-list">
                            {evidence.map((item, index) => (
                                <div key={index} className="evidence-item">
                                    {item}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default ResultCard;
