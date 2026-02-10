import { useState } from "react";
import { askDeepSeek } from "../services/deepseek";

export default function DeepSeekChat() {
    const [prompt, setPrompt] = useState("");
    const [response, setResponse] = useState("");
    const [loading, setLoading] = useState(false);

    async function send() {
        if (!prompt.trim()) return;

        setLoading(true);
        setResponse("Pensando...");

        try {
            const r = await askDeepSeek(prompt);
            if (r.success) {
                setResponse(r.response);
            } else {
                setResponse("Error: " + (r.error || "Unknown error"));
            }
        } catch (e) {
            setResponse("Error de conexión: " + e.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto", color: "var(--color-text-primary)" }}>
            <h2 style={{ marginBottom: "1rem" }}>🤖 DeepSeek-R1 Chat Test</h2>
            <p style={{ marginBottom: "1rem", color: "var(--color-text-secondary)" }}>
                Prueba directa de conexión con el modelo LLM local (Ollama).
            </p>

            <textarea
                style={{
                    width: "100%",
                    height: 150,
                    padding: "1rem",
                    marginBottom: "1rem",
                    background: "var(--color-bg-secondary)",
                    color: "var(--color-text-primary)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "8px"
                }}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Escribe un prompt para DeepSeek..."
            />

            <button
                onClick={send}
                className="btn-upload"
                disabled={loading}
                style={{ opacity: loading ? 0.7 : 1 }}
            >
                {loading ? "Procesando..." : "Enviar a DeepSeek"}
            </button>

            <div style={{ marginTop: "2rem" }}>
                <h3 style={{ marginBottom: "0.5rem", fontSize: "1rem" }}>Respuesta:</h3>
                <pre style={{
                    background: "var(--color-bg-secondary)",
                    padding: "1.5rem",
                    borderRadius: "8px",
                    border: "1px solid var(--color-border)",
                    whiteSpace: "pre-wrap",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.9rem",
                    lineHeight: "1.6"
                }}>
                    {response || "Esperando input..."}
                </pre>
            </div>
        </div>
    );
}
