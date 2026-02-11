import './ResultCard.css';
import { Activity, ShieldCheck, FileText, Brain } from 'lucide-react';

function ResultCard({ result, imagePreview }) {
    if (!result) return null;

    const { verdict, confidence, scores, evidence, processing_time } = result;

    // Mapping Error Fix: Use ai_probability if available, else fallback to final_score
    // If ai_probability is null, use 0. Note that backend sends ai_probability as 0-100 float.
    const aiProb = result.ai_probability !== undefined && result.ai_probability !== null
        ? result.ai_probability
        : (scores.final_score !== undefined ? scores.final_score * 100 : 0);

    const realProb = 100 - aiProb;

    const isFake = verdict.includes('GENERADA') || verdict.includes('IA');
    const isReal = verdict.includes('REAL');
    const verdictClass = isFake ? 'verdict-fake' : isReal ? 'verdict-real' : 'verdict-inconclusive';

    return (
        <div className={`result-card ${verdictClass}`}>
            {/* Header */}
            <div className="result-header">
                <h2>
                    <ShieldCheck size={20} className="icon" />
                    Informe Forense
                </h2>
                {processing_time && (
                    <span className="processing-time">PROCESADO EN {processing_time}s</span>
                )}
            </div>

            {/* Image Preview - Fix for "Imagen Cortada" */}
            {imagePreview && (
                <div className="result-image-container" style={{
                    backgroundColor: 'black',
                    width: '100%',
                    height: '300px',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    marginBottom: '1rem',
                    borderRadius: '8px',
                    overflow: 'hidden',
                    border: '1px solid var(--color-border)'
                }}>
                    <img
                        src={imagePreview}
                        alt="Evidencia Analizada"
                        style={{
                            maxWidth: '100%',
                            maxHeight: '100%',
                            objectFit: 'contain'
                        }}
                    />
                </div>
            )}

            {/* Veredicto Principal */}
            <div className="verdict-panel">
                <div className="verdict-label">CONCLUSIÓN DEL SISTEMA</div>
                <div className="verdict-text">{verdict}</div>
                <div className="confidence-badge">
                    <Activity size={16} style={{marginRight: '6px'}} />
                    <span>CONFIANZA {confidence}</span>
                </div>
            </div>

            <div className="details-grid">
                {/* Columna de Scores */}
                <div className="scores-column">
                    <h3><Activity size={18} style={{marginRight: '8px', verticalAlign: 'text-bottom'}}/>Métricas de Detección</h3>
                    <div className="scores-list">
                        {/* Unified Score based on ai_probability */}
                        <div className="score-row highlight">
                            <div className="score-info">
                                <span className="score-name">Probabilidad IA</span>
                                <span className="score-num">{aiProb.toFixed(1)}%</span>
                            </div>
                            <div className="progress-track">
                                <div className="progress-fill" style={{ width: `${aiProb}%` }}></div>
                            </div>
                        </div>

                         <div className="score-row">
                            <div className="score-info">
                                <span className="score-name">Probabilidad Real</span>
                                <span className="score-num">{realProb.toFixed(1)}%</span>
                            </div>
                            <div className="progress-track">
                                <div className="progress-fill" style={{ width: `${realProb}%`, backgroundColor: 'var(--color-success)' }}></div>
                            </div>
                        </div>

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
                                    <span className="score-name">Análisis Semántico (Asistente Forense)</span>
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
                        <h3><FileText size={18} style={{marginRight: '8px', verticalAlign: 'text-bottom'}}/>Evidencia Técnica</h3>
                        <div className="evidence-list">
                            {evidence.map((item, index) => (
                                <div key={index} className="evidence-item">
                                    <Brain size={14} style={{marginRight: '8px', flexShrink: 0, marginTop: '4px'}} />
                                    <span>{item}</span>
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
