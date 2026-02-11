import './ResultCard.css';
import { Activity, FileText, BarChart2 } from 'lucide-react';

function ResultCard({ result }) {
    if (!result) return null;

    // Destructure properties, including ai_probability which might come directly from backend
    const { verdict, confidence, scores, evidence, processing_time, ai_probability } = result;

    // Calculate probabilities
    // If ai_probability is present, use it. Otherwise fall back to scores.fake_evidence or 0.
    const aiScore = ai_probability !== undefined ? ai_probability : (scores?.fake_evidence || 0);
    const realScore = 1.0 - aiScore;

    // Determine verdict class
    const isFake = verdict.includes('GENERADA') || verdict.includes('IA');
    const isReal = verdict.includes('REAL');
    const verdictClass = isFake ? 'verdict-fake' : isReal ? 'verdict-real' : 'verdict-inconclusive';

    return (
        <div className={`result-card ${verdictClass}`}>
            {/* Header */}
            <div className="result-header">
                <h2>
                    <Activity size={20} />
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
                    <h3>
                        <BarChart2 size={18} />
                        Métricas de Detección
                    </h3>
                    <div className="scores-list">
                        {/* Display AI Probability from backend if available directly, or calculated */}
                        <div className="score-row highlight">
                            <div className="score-info">
                                <span className="score-name">Probabilidad IA</span>
                                <span className="score-num">{(aiScore * 100).toFixed(1)}%</span>
                            </div>
                            <div className="progress-track">
                                <div className="progress-fill" style={{ width: `${aiScore * 100}%`, background: 'var(--color-error)' }}></div>
                            </div>
                        </div>

                        <div className="score-row">
                            <div className="score-info">
                                <span className="score-name">Probabilidad Real</span>
                                <span className="score-num">{(realScore * 100).toFixed(1)}%</span>
                            </div>
                            <div className="progress-track">
                                <div className="progress-fill" style={{ width: `${realScore * 100}%`, background: 'var(--color-success)' }}></div>
                            </div>
                        </div>

                        {/* Additional granular scores if available */}
                        {scores?.multiLID !== undefined && (
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

                        {scores?.UFD !== undefined && (
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

                        {scores?.Semantic !== undefined && (
                            <div className="score-row">
                                <div className="score-info">
                                    <span className="score-name">Análisis Semántico</span>
                                    <span className="score-num">{(scores.Semantic * 100).toFixed(1)}%</span>
                                </div>
                                <div className="progress-track">
                                    <div className="progress-fill" style={{ width: `${scores.Semantic * 100}%`, backgroundColor: 'var(--color-accent)' }}></div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Columna de Evidencias */}
                {evidence && evidence.length > 0 && (
                    <div className="evidence-column">
                        <h3>
                            <FileText size={18} />
                            Evidencia Técnica
                        </h3>
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
