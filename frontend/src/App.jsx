import { useState, useEffect } from 'react';
import {
    Image as ImageIcon,
    Video as VideoIcon,
    Mic as MicIcon,
    Clock,
    ShieldCheck,
    Activity,
    FileText,
    Brain,
    Layout
} from 'lucide-react';
import UploadImage from './components/UploadImage';
import UploadVideo from './components/UploadVideo';
import UploadAudio from './components/UploadAudio';
import ResultCard from './components/ResultCard';
import VideoResultCard from './components/VideoResultCard';
import AudioResultCard from './components/AudioResultCard';
import AnalysisProgress from './components/AnalysisProgress';
import ResultsPanel from './components/ResultsPanel';
import { analyzeImage, analyzeVideo, analyzeAudio } from './services/api';
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

    // History State
    const [history, setHistory] = useState([]);

    // Load history on mount
    useEffect(() => {
        fetch('/api/history')
            .then(res => {
                if (!res.ok) throw new Error('Failed to load history');
                return res.json();
            })
            .then(data => {
                // Ensure we only keep the last 20 and valid items
                if (Array.isArray(data)) {
                    setHistory(data.slice(0, 20));
                }
            })
            .catch(err => console.error("History fetch error:", err));
    }, []);

    const loadHistoryItem = (item) => {
        // Assuming item structure: { type, result, filename, timestamp, ... }
        // We need to handle potential missing preview URLs (since blobs are local)
        // We will switch tab and set result.

        if (item.type === 'image' || !item.type) { // Default to image if type missing
            setActiveTab('image');
            setResult(item.result);
            setShowResults(true);
            // We can't restore the blob URL, so preview might be null or a stored URL
            setImagePreview(item.imageUrl || null);
        } else if (item.type === 'video') {
            setActiveTab('video');
            setVideoResult(item.result);
            setVideoPreview(null);
        } else if (item.type === 'audio') {
            setActiveTab('audio');
            setAudioResult(item.result);
            setAudioPreview(null);
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

            // Refresh history after new analysis
             fetch('/api/history')
                .then(res => res.json())
                .then(data => setHistory(data.slice(0, 20)))
                .catch(e => console.error(e));

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

            // Refresh history
             fetch('/api/history')
                .then(res => res.json())
                .then(data => setHistory(data.slice(0, 20)))
                .catch(e => console.error(e));

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

             // Refresh history
             fetch('/api/history')
                .then(res => res.json())
                .then(data => setHistory(data.slice(0, 20)))
                .catch(e => console.error(e));

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
                            <ShieldCheck size={24} color="white" />
                        </div>
                        <span className="logo-text">UIDE Forense AI</span>
                    </div>
                    <ul className="nav-menu">
                        <li><a href="#analisis">Análisis</a></li>
                        <li><a href="#documentacion">Documentación</a></li>
                        <li><a href="#api">API</a></li>
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
                                <ImageIcon size={20} />
                                Imágenes
                            </button>
                            <button
                                className={`tab-button ${activeTab === 'video' ? 'active' : ''}`}
                                onClick={() => setActiveTab('video')}
                            >
                                <VideoIcon size={20} />
                                Videos
                            </button>
                            <button
                                className={`tab-button ${activeTab === 'audio' ? 'active' : ''}`}
                                onClick={() => setActiveTab('audio')}
                            >
                                <MicIcon size={20} />
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
                        <div className="history-list" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {history.length === 0 ? (
                                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>No hay análisis recientes.</p>
                            ) : (
                                history.map((item, idx) => (
                                    <div
                                        key={idx}
                                        onClick={() => loadHistoryItem(item)}
                                        className="history-item"
                                        style={{
                                            padding: '0.75rem',
                                            background: 'var(--color-bg-secondary)',
                                            border: '1px solid var(--color-border)',
                                            borderRadius: '8px',
                                            cursor: 'pointer',
                                            fontSize: '0.85rem',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.5rem',
                                            transition: 'all 0.2s'
                                        }}
                                        onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--color-accent)'}
                                        onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--color-border)'}
                                    >
                                        <Clock size={14} color="var(--color-text-secondary)" />
                                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                            {item.filename || `Análisis #${history.length - idx}`}
                                        </span>
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
                                                <Brain size={24} />
                                            </div>
                                            <h3 className="feature-title">Razonamiento Semántico</h3>
                                            <p className="feature-description">
                                                Asistente Forense analiza la plausibilidad de la escena, buscando inconsistencias semánticas que los modelos de píxeles ignoran.
                                            </p>
                                        </div>
                                        <div className="feature-card">
                                            <div className="feature-icon">
                                                <Activity size={24} />
                                            </div>
                                            <h3 className="feature-title">Fusión de Expertos</h3>
                                            <p className="feature-description">
                                                Combina MultiLID, detectores de frecuencias y análisis semántico para un veredicto robusto.
                                            </p>
                                        </div>
                                        <div className="feature-card">
                                            <div className="feature-icon">
                                                <ShieldCheck size={24} />
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
