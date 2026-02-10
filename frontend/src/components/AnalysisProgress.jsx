import './AnalysisProgress.css';

/**
 * Componente para mostrar progreso del análisis.
 */
function AnalysisProgress() {
    return (
        <div className="analysis-progress">
            <div className="progress-spinner">
                <div className="spinner"></div>
            </div>

            <div className="progress-text">
                <h3>🔍 Analizando imagen...</h3>
                <p>Ejecutando expertos forenses:</p>
                <ul className="progress-steps">
                    <li className="step">✅ Extracción de features (CLIP)</li>
                    <li className="step">🔬 Análisis multiLID</li>
                    <li className="step">🎯 Detector UFD</li>
                    <li className="step">🧠 Análisis semántico (DeepSeek-R1)</li>
                    <li className="step">⚗️ Fusión de resultados</li>
                </ul>
                <p className="progress-note">
                    Esto puede tomar 10-30 segundos dependiendo de DeepSeek...
                </p>
            </div>
        </div>
    );
}

export default AnalysisProgress;
