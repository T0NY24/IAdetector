
import React, { useState, useEffect, useRef } from 'react';
import '../App.css';
import {
    X,
    Send,
    User,
    Bot
} from 'lucide-react';

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

    // Use consistent probability mapping
    const aiProb = result.ai_probability !== undefined && result.ai_probability !== null
        ? result.ai_probability
        : ((result.scores?.fake_evidence || 0) * 100);

    const realProb = 100 - aiProb;

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
                            <h2 className="results-title">Resultados del Análisis</h2>
                            <div className={`analysis-status`}>
                                <span className={`status-indicator ${getStatusColor()}`}></span>
                                <span>{result.verdict}</span>
                            </div>
                        </div>
                        <button className="close-button" onClick={onClose}>
                            <X size={24} />
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
                            <div className={`metric-value ${aiProb > 50 ? 'high' : 'low'}`}>
                                {aiProb.toFixed(1)}%
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
                            <div className={`metric-value ${realProb > 50 ? 'low' : 'mid'}`}>
                                {realProb.toFixed(1)}%
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
                                        <User size={16} />
                                    ) : (
                                        <Bot size={16} />
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
                                <Send size={18} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResultsPanel;
