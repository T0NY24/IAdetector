import { useState } from 'react';
import UploadImage from './components/UploadImage';
import ResultCard from './components/ResultCard';
import AnalysisProgress from './components/AnalysisProgress';
import DeepSeekChat from './components/DeepSeekChat';
import ResultsPanel from './components/ResultsPanel';
import { analyzeImage } from './services/api';
import './App.css';

function App() {
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [useDeepseek, setUseDeepseek] = useState(true);
    const [activeTab, setActiveTab] = useState('image');
    const [showResults, setShowResults] = useState(false);
    const [imagePreview, setImagePreview] = useState(null);

    const handleImageUpload = async (imageFile) => {
        setAnalyzing(true);
        setError(null);
        setResult(null);
        setShowResults(false);

        // Create preview URL
        const previewUrl = URL.createObjectURL(imageFile);
        setImagePreview(previewUrl);

        try {
            console.log('Analyzing image...', imageFile.name);
            const response = await analyzeImage(imageFile, useDeepseek);
            setResult(response.result);
            setShowResults(true); // Auto-open results panel
        } catch (err) {
            console.error('Analysis error:', err);
            setError(err.message);
        } finally {
            setAnalyzing(false);
        }
    };

    return (
        <>
            <nav className="navbar">
                <div className="nav-container">
                    <div className="logo">
                        <div className="logo-icon">
                            <svg viewBox="0 0 24 24">
                                <path d="M12 2L2 7L12 12L22 7L12 2Z" />
                                <path d="M2 17L12 22L22 17" />
                                <path d="M2 12L12 17L22 12" />
                            </svg>
                        </div>
                        <span className="logo-text">ForensicAI</span>
                    </div>
                    <ul className="nav-menu">
                        <li><a href="#analisis">Análisis</a></li>
                        <li><a href="#documentacion">Documentación</a></li>
                        <li><a href="#api">API</a></li>
                        <li><a href="#casos">Casos de Uso</a></li>
                    </ul>
                </div>
            </nav>

            <div className="main-container">
                {/* Sidebar */}
                <aside className="sidebar">
                    <div className="sidebar-section">
                        <h3 className="sidebar-title">Tipo de Análisis</h3>
                        <div className="analysis-tabs">
                            <button
                                className={`tab-button ${activeTab === 'image' ? 'active' : ''}`}
                                onClick={() => setActiveTab('image')}
                            >
                                <svg className="icon" viewBox="0 0 24 24">
                                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                                    <circle cx="8.5" cy="8.5" r="1.5" />
                                    <polyline points="21 15 16 10 5 21" />
                                </svg>
                                Imágenes
                            </button>
                            <button
                                className={`tab-button ${activeTab === 'video' ? 'active' : ''}`}
                                onClick={() => setActiveTab('video')}
                            >
                                <svg className="icon" viewBox="0 0 24 24">
                                    <polygon points="23 7 16 12 23 17 23 7" />
                                    <rect x="2" y="5" width="14" height="14" rx="2" ry="2" />
                                </svg>
                                Videos
                            </button>
                            <button
                                className={`tab-button ${activeTab === 'audio' ? 'active' : ''}`}
                                onClick={() => setActiveTab('audio')}
                            >
                                <svg className="icon" viewBox="0 0 24 24">
                                    <path d="M9 18V5l12-2v13" />
                                    <circle cx="6" cy="18" r="3" />
                                    <circle cx="18" cy="16" r="3" />
                                </svg>
                                Audio
                            </button>
                        </div>
                    </div>

                    <div className="sidebar-section">
                        <h3 className="sidebar-title">Configuración</h3>
                        <div className="toggle-wrapper">
                            <label className="toggle-label">
                                <input
                                    type="checkbox"
                                    checked={useDeepseek}
                                    onChange={(e) => setUseDeepseek(e.target.checked)}
                                    disabled={analyzing}
                                    className="toggle-checkbox"
                                />
                                <span>DeepSeek-R1 (Reasoning)</span>
                            </label>
                        </div>
                    </div>

                    <div className="sidebar-section">
                        <h3 className="sidebar-title">Estadísticas del Sistema</h3>
                        <div className="stats-box">
                            <div className="stat-item">
                                <span className="stat-label">Precisión</span>
                                <span className="stat-value">98.7%</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-label">Uptime</span>
                                <span className="stat-value">99.9%</span>
                            </div>
                        </div>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="content">
                    {activeTab === 'image' && (
                        <>
                            <div className="content-header">
                                <h1 className="content-title">Análisis de Imágenes Generadas por IA</h1>
                                <p className="content-description">
                                    Detecte imágenes sintéticas generadas por modelos de difusión, GANs y otros sistemas mediante análisis de artefactos, inconsistencias estructurales y razonamiento semántico con DeepSeek-R1.
                                </p>
                            </div>

                            <div className="analysis-workflow">
                                {/* Upload Area */}
                                {!analyzing && (
                                    <UploadImage onUpload={handleImageUpload} disabled={analyzing} />
                                )}

                                {/* Progress */}
                                {analyzing && <AnalysisProgress />}

                                {/* Inline Result Summary (Optional - keeps flow) */}
                                {result && !showResults && (
                                    <div className="results-wrapper">
                                        <div style={{ marginBottom: '2rem', display: 'flex', gap: '1rem' }}>
                                            <button
                                                className="btn-upload"
                                                onClick={() => setResult(null)}
                                                style={{ background: 'var(--color-bg-tertiary)', border: '1px solid var(--color-border)' }}
                                            >
                                                ← Analizar otra
                                            </button>
                                            <button
                                                className="btn-upload"
                                                onClick={() => setShowResults(true)}
                                                style={{ background: 'var(--color-accent)', border: 'none', color: 'white' }}
                                            >
                                                Ver Análisis Detallado
                                            </button>
                                        </div>
                                        <ResultCard result={result} />
                                    </div>
                                )}

                                {/* Error */}
                                {error && (
                                    <div className="error-box" style={{ marginTop: '2rem', padding: '2rem', background: 'rgba(239,68,68,0.1)', borderRadius: '8px' }}>
                                        <h3 style={{ color: 'var(--color-error)' }}>Error en el análisis</h3>
                                        <p>{error}</p>
                                        <button className="btn-upload" onClick={() => setError(null)}>Reintentar</button>
                                    </div>
                                )}
                            </div>

                            {/* Features Grid (Initial State) */}
                            {!result && !analyzing && (
                                <>
                                    <div style={{ marginTop: '3rem', borderTop: '1px solid var(--color-border)' }}>
                                        <DeepSeekChat />
                                    </div>

                                    <div className="features-grid">
                                        <div className="feature-card">
                                            <div className="feature-icon">
                                                <svg viewBox="0 0 24 24">
                                                    <circle cx="12" cy="12" r="10" />
                                                    <line x1="12" y1="16" x2="12" y2="12" />
                                                    <line x1="12" y1="8" x2="12.01" y2="8" />
                                                </svg>
                                            </div>
                                            <h3 className="feature-title">Razonamiento Semántico</h3>
                                            <p className="feature-description">
                                                DeepSeek-R1 analiza la plausibilidad de la escena, buscando inconsistencias semánticas que los modelos de píxeles ignoran.
                                            </p>
                                        </div>
                                        <div className="feature-card">
                                            <div className="feature-icon">
                                                <svg viewBox="0 0 24 24">
                                                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                                                </svg>
                                            </div>
                                            <h3 className="feature-title">Fusión de Expertos</h3>
                                            <p className="feature-description">
                                                Combina MultiLID, detectores de frecuencias y análisis semántico para un veredicto robusto.
                                            </p>
                                        </div>
                                        <div className="feature-card">
                                            <div className="feature-icon">
                                                <svg viewBox="0 0 24 24">
                                                    <circle cx="12" cy="12" r="3"></circle>
                                                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                                                </svg>
                                            </div>
                                            <h3 className="feature-title">Procesamiento Local</h3>
                                            <p className="feature-description">
                                                Todo el análisis se realiza en su infraestructura segura, garantizando la privacidad de los datos forenses.
                                            </p>
                                        </div>
                                    </div>
                                </>
                            )}
                        </>
                    )}

                    {activeTab !== 'image' && (
                        <div className="upload-container" style={{ opacity: 0.5 }}>
                            <h3>Próximamente</h3>
                            <p>El módulo de {activeTab === 'video' ? 'Video' : 'Audio'} estará disponible en la versión 3.1</p>
                        </div>
                    )}

                    {/* Results Overlay Panel */}
                    <ResultsPanel
                        isOpen={showResults}
                        onClose={() => setShowResults(false)}
                        result={result}
                        imagePreview={imagePreview}
                    />
                </main>
            </div>
        </>
    );
}

export default App;
