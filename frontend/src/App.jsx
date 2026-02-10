import { useState, useEffect } from 'react';
import { ShieldCheck, Image as ImageIcon, Video, Mic, Brain, Activity, Layers, Scan } from 'lucide-react';
import UploadImage from './components/UploadImage';
import UploadVideo from './components/UploadVideo';
import UploadAudio from './components/UploadAudio';
import ResultCard from './components/ResultCard';
import VideoResultCard from './components/VideoResultCard';
import AudioResultCard from './components/AudioResultCard';
import AnalysisProgress from './components/AnalysisProgress';
import ResultsPanel from './components/ResultsPanel';
import { analyzeImage, analyzeVideo, analyzeAudio, getHistory } from './services/api';
import './App.css';

function App() {
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [useDeepseek, setUseDeepseek] = useState(true);
    const [activeTab, setActiveTab] = useState('image');
    const [showResults, setShowResults] = useState(false);
    const [imagePreview, setImagePreview] = useState(null);
    const [videoPreview, setVideoPreview] = useState(null);
    const [audioPreview, setAudioPreview] = useState(null);
    const [videoResult, setVideoResult] = useState(null);
    const [audioResult, setAudioResult] = useState(null);
    const [history, setHistory] = useState([]);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        try {
            const data = await getHistory(20);
            setHistory(data.results || []);
        } catch (err) {
            console.error("Failed to load history:", err);
        }
    };

    const loadHistoryItem = (item) => {
        if (!item || !item.result) return;

        if (item.type === 'image') {
            setActiveTab('image');
            setResult(item.result);
            setShowResults(true);
            setImagePreview(null);
        } else if (item.type === 'video') {
            setActiveTab('video');
            setVideoResult(item.result);
        } else if (item.type === 'audio') {
            setActiveTab('audio');
            setAudioResult(item.result);
        }
    };

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
            loadHistory();
        } catch (err) {
            console.error('Analysis error:', err);
            setError(err.message);
        } finally {
            setAnalyzing(false);
        }
    };

    const handleVideoUpload = async (videoFile) => {
        setAnalyzing(true);
        setError(null);
        setVideoResult(null);

        const previewUrl = URL.createObjectURL(videoFile);
        setVideoPreview(previewUrl);

        try {
            console.log('Analyzing video...', videoFile.name);
            const response = await analyzeVideo(videoFile);
            setVideoResult(response.result);
        } catch (err) {
            console.error('Video analysis error:', err);
            setError(err.message);
        } finally {
            setAnalyzing(false);
        }
    };

    const handleAudioUpload = async (audioFile) => {
        setAnalyzing(true);
        setError(null);
        setAudioResult(null);

        const previewUrl = URL.createObjectURL(audioFile);
        setAudioPreview(previewUrl);

        try {
            console.log('Analyzing audio...', audioFile.name);
            const response = await analyzeAudio(audioFile);
            setAudioResult(response.result);
        } catch (err) {
            console.error('Audio analysis error:', err);
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
                            <ShieldCheck size={20} color="white" />
                        </div>
                        <span className="logo-text">ForensicAI</span>
                    </div>
                    <ul className="nav-menu">
                        <li><a href="#analisis" className="active">Análisis Forense</a></li>
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
                                <ImageIcon size={18} />
                                Imágenes
                            </button>
                            <button
                                className={`tab-button ${activeTab === 'video' ? 'active' : ''}`}
                                onClick={() => setActiveTab('video')}
                            >
                                <Video size={18} />
                                Videos
                            </button>
                            <button
                                className={`tab-button ${activeTab === 'audio' ? 'active' : ''}`}
                                onClick={() => setActiveTab('audio')}
                            >
                                <Mic size={18} />
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
                                <span>Asistente Forense (Reasoning)</span>
                            </label>
                        </div>
                    </div>

                    <div className="sidebar-section">
                        <h3 className="sidebar-title">Historial Reciente</h3>
                        <div className="history-list">
                            {history.length === 0 ? (
                                <p style={{color: 'var(--color-text-muted)', fontSize: '0.85rem'}}>No hay análisis recientes</p>
                            ) : (
                                history.slice(0, 20).map((item, idx) => (
                                    <div key={idx} className="history-item" onClick={() => loadHistoryItem(item)}>
                                        <div className="history-icon">
                                            {item.type === 'image' && <ImageIcon size={14} />}
                                            {item.type === 'video' && <Video size={14} />}
                                            {item.type === 'audio' && <Mic size={14} />}
                                        </div>
                                        <div className="history-info">
                                            <span className="history-date">
                                                {new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                            </span>
                                            <span className={`history-verdict ${item.result?.verdict?.includes('IA') ? 'fake' : 'real'}`}>
                                                {item.result?.verdict || 'Result'}
                                            </span>
                                        </div>
                                    </div>
                                ))
                            )}
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
                                    Detecte imágenes sintéticas generadas por modelos de difusión, GANs y otros sistemas mediante análisis de artefactos, inconsistencias estructurales y razonamiento semántico con Asistente Forense.
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
                                    <div className="features-grid">
                                        <div className="feature-card">
                                            <div className="feature-icon">
                                                <Brain size={24} color="var(--color-accent)" />
                                            </div>
                                            <h3 className="feature-title">Razonamiento Semántico</h3>
                                            <p className="feature-description">
                                                El Asistente Forense analiza la plausibilidad de la escena, buscando inconsistencias semánticas que los modelos de píxeles ignoran.
                                            </p>
                                        </div>
                                        <div className="feature-card">
                                            <div className="feature-icon">
                                                <Layers size={24} color="var(--color-accent)" />
                                            </div>
                                            <h3 className="feature-title">Fusión de Expertos</h3>
                                            <p className="feature-description">
                                                Combina MultiLID, detectores de frecuencias y análisis semántico para un veredicto robusto.
                                            </p>
                                        </div>
                                        <div className="feature-card">
                                            <div className="feature-icon">
                                                <ShieldCheck size={24} color="var(--color-accent)" />
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

                    {activeTab === 'video' && (
                        <>
                            <div className="content-header">
                                <h1 className="content-title">Detección de Deepfakes en Video</h1>
                                <p className="content-description">
                                    Detecte videos manipulados con deepfakes faciales usando XceptionNet entrenado en FaceForensics++.
                                </p>
                            </div>

                            <div className="analysis-workflow">
                                {!analyzing && (
                                    <UploadVideo onUpload={handleVideoUpload} disabled={analyzing} />
                                )}

                                {analyzing && <AnalysisProgress />}

                                {videoResult && !analyzing && (
                                    <div className="results-wrapper">
                                        <button
                                            className="btn-upload"
                                            onClick={() => { setVideoResult(null); setVideoPreview(null); }}
                                            style={{ marginBottom: '2rem', background: 'var(--color-bg-tertiary)', border: '1px solid var(--color-border)' }}
                                        >
                                            ← Analizar otro video
                                        </button>
                                        <VideoResultCard result={videoResult} />
                                    </div>
                                )}

                                {error && activeTab === 'video' && (
                                    <div className="error-box" style={{ marginTop: '2rem', padding: '2rem', background: 'rgba(239,68,68,0.1)', borderRadius: '8px' }}>
                                        <h3 style={{ color: 'var(--color-error)' }}>Error en el análisis</h3>
                                        <p>{error}</p>
                                        <button className="btn-upload" onClick={() => setError(null)}>Reintentar</button>
                                    </div>
                                )}
                            </div>
                        </>
                    )}

                    {activeTab === 'audio' && (
                        <>
                            <div className="content-header">
                                <h1 className="content-title">Detección de Audio Sintético</h1>
                                <p className="content-description">
                                    Detecte voces generadas por IA (ElevenLabs, RVC, TTS) usando análisis espectral avanzado.
                                </p>
                            </div>

                            <div className="analysis-workflow">
                                {!analyzing && (
                                    <UploadAudio onUpload={handleAudioUpload} disabled={analyzing} />
                                )}

                                {analyzing && <AnalysisProgress />}

                                {audioResult && !analyzing && (
                                    <div className="results-wrapper">
                                        <button
                                            className="btn-upload"
                                            onClick={() => { setAudioResult(null); setAudioPreview(null); }}
                                            style={{ marginBottom: '2rem', background: 'var(--color-bg-tertiary)', border: '1px solid var(--color-border)' }}
                                        >
                                            ← Analizar otro audio
                                        </button>
                                        <AudioResultCard result={audioResult} />
                                    </div>
                                )}

                                {error && activeTab === 'audio' && (
                                    <div className="error-box" style={{ marginTop: '2rem', padding: '2rem', background: 'rgba(239,68,68,0.1)', borderRadius: '8px' }}>
                                        <h3 style={{ color: 'var(--color-error)' }}>Error en el análisis</h3>
                                        <p>{error}</p>
                                        <button className="btn-upload" onClick={() => setError(null)}>Reintentar</button>
                                    </div>
                                )}
                            </div>
                        </>
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
