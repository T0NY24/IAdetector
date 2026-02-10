
import React, { useState, useEffect, useRef } from 'react';
import '../App.css';

const ResultsPanel = ({ isOpen, onClose, result, imagePreview }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // Initial greeting when result loads
    useEffect(() => {
        if (isOpen && result) {
            setMessages([
                {
                    id: 1,
                    text: `He analizado tu imagen y el veredicto es: ${result.verdict}. ¿Tienes alguna pregunta sobre los resultados?`,
                    isUser: false
                }
            ]);
        }
    }, [isOpen, result]);

    // Auto-scroll to bottom of chat
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    if (!isOpen || !result) return null;

    const sendMessage = async (text = inputMessage) => {
        if (!text.trim()) return;

        // Add user message
        const userMsg = { id: Date.now(), text, isUser: true };
        setMessages(prev => [...prev, userMsg]);
        setInputMessage('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/semantic/chat_analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    context: result
                })
            });

            const data = await response.json();

            if (data.error) throw new Error(data.error);

            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                text: data.response,
                isUser: false
            }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                text: "Lo siento, hubo un error al procesar tu pregunta. Intenta de nuevo.",
                isUser: false
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    // Determine status color
    const getStatusColor = () => {
        if (result.verdict.includes("IA")) return "warning";
        if (result.verdict.includes("REAL")) return "success";
        return "neutral"; // or error for unknown
    };

    return (
        <div className="results-panel-overlay" onClick={onClose}>
            <div className="results-container" onClick={e => e.stopPropagation()}>
                {/* Left Side: Analysis Results */}
                <div className="results-main">
                    <div className="results-header">
                        <div>
                            <h2 class="results-title">Resultados del Análisis</h2>
                            <div className={`analysis-status`}>
                                <span className={`status-indicator ${getStatusColor()}`}></span>
                                <span>{result.verdict}</span>
                            </div>
                        </div>
                        <button className="close-button" onClick={onClose}>
                            <svg viewBox="0 0 24 24" width="24" height="24">
                                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" strokeWidth="2" />
                                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" strokeWidth="2" />
                            </svg>
                        </button>
                    </div>

                    <div className="preview-section">
                        {imagePreview ? (
                            <img src={imagePreview} alt="Analyzed" className="preview-image" />
                        ) : (
                            <div className="preview-placeholder">Vista previa no disponible</div>
                        )}
                    </div>

                    <div className="metrics-grid">
                        <div className="metric-card">
                            <div className="metric-label">Probabilidad IA</div>
                            <div className={`metric-value ${result.scores?.fake_evidence > 0.5 ? 'high' : 'low'}`}>
                                {((result.scores?.fake_evidence || 0) * 100).toFixed(1)}%
                            </div>
                            <div className="metric-description">Evidencia de generación sintética</div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-label">Nivel de Confianza</div>
                            <div className="metric-value">
                                {result.confidence}
                            </div>
                            <div className="metric-description">Fiabilidad del análisis</div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-label">Probabilidad Real</div>
                            <div className={`metric-value ${result.scores?.real_evidence > 0.5 ? 'low' : 'mid'}`}>
                                {((result.scores?.real_evidence || 0) * 100).toFixed(1)}%
                            </div>
                            <div className="metric-description">Evidencia de fotografía auténtica</div>
                        </div>
                    </div>

                    <div className="findings-section">
                        <h3 className="section-title">Hallazgos Principales</h3>
                        {result.evidence && result.evidence.map((item, index) => (
                            <div key={index} className={`finding-item ${item.includes("REAL") ? 'success' : item.includes("IA") ? 'warning' : 'neutral'}`}>
                                <div className="finding-text">{item}</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right Side: Chatbot */}
                <div className="chatbot-sidebar">
                    <div className="chatbot-header">
                        <h3 className="chatbot-title">Asistente Forense</h3>
                        <p className="chatbot-subtitle">Pregunta sobre estos resultados</p>
                    </div>

                    <div className="chat-messages">
                        {messages.map(msg => (
                            <div key={msg.id} className={`message ${msg.isUser ? 'user' : 'assistant'}`}>
                                <div className={`message-avatar ${msg.isUser ? 'user' : 'assistant'}`}>
                                    {msg.isUser ? (
                                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" fill="none" strokeWidth="2">
                                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
                                        </svg>
                                    ) : (
                                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" fill="none" strokeWidth="2">
                                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                                        </svg>
                                    )}
                                </div>
                                <div className="message-text">{msg.text}</div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="message assistant">
                                <div className="message-text">Escribiendo...</div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />

                        {!isLoading && messages.length < 2 && (
                            <div className="suggested-questions">
                                <button className="suggested-question" onClick={() => sendMessage("¿Por qué crees que es este el veredicto?")}>
                                    ¿Por qué crees que es este el veredicto?
                                </button>
                                <button className="suggested-question" onClick={() => sendMessage("¿Qué indicios técnicos encontraste?")}>
                                    ¿Qué indicios técnicos encontraste?
                                </button>
                                <button className="suggested-question" onClick={() => sendMessage("Explícame el análisis semántico")}>
                                    Explícame el análisis semántico
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="chat-input-container">
                        <div className="chat-input-wrapper">
                            <input
                                type="text"
                                className="chat-input"
                                placeholder="Escribe tu pregunta..."
                                value={inputMessage}
                                onChange={e => setInputMessage(e.target.value)}
                                onKeyPress={e => e.key === 'Enter' && sendMessage()}
                                disabled={isLoading}
                            />
                            <button
                                className="send-button"
                                onClick={() => sendMessage()}
                                disabled={isLoading || !inputMessage.trim()}
                            >
                                <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" fill="none" strokeWidth="2">
                                    <line x1="22" y1="2" x2="11" y2="13" />
                                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResultsPanel;
