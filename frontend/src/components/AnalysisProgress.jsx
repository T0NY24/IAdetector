import { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, Circle, Brain, Scan, Eye, Activity } from 'lucide-react';
import './AnalysisProgress.css';

/**
 * Componente para mostrar progreso del análisis con pasos secuenciales.
 */
function AnalysisProgress() {
    const [currentStep, setCurrentStep] = useState(0);

    const steps = [
        { id: 0, label: 'Inicializando motores forenses...', icon: <Activity size={18} /> },
        { id: 1, label: 'Extracción de características (CLIP)', icon: <Scan size={18} /> },
        { id: 2, label: 'Análisis de artefactos (MultiLID)', icon: <Eye size={18} /> },
        { id: 3, label: 'Detección de inconsistencias (UFD)', icon: <Activity size={18} /> },
        { id: 4, label: 'Razonamiento Semántico', icon: <Brain size={18} /> },
        { id: 5, label: 'Generando informe final...', icon: <CheckCircle2 size={18} /> },
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentStep((prev) => {
                if (prev < steps.length - 1) return prev + 1;
                return prev;
            });
        }, 800); // Advance every 800ms for demo effect

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="analysis-progress">
            <div className="progress-header">
                <Loader2 className="spinner-icon" size={48} />
                <h3>Analizando evidencia...</h3>
                <p>Por favor espere mientras nuestros agentes procesan los datos.</p>
            </div>

            <div className="progress-steps-container">
                {steps.map((step, index) => {
                    const isActive = index === currentStep;
                    const isCompleted = index < currentStep;
                    const isPending = index > currentStep;

                    return (
                        <div
                            key={step.id}
                            className={`progress-step ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isPending ? 'pending' : ''}`}
                        >
                            <div className="step-icon">
                                {isCompleted ? <CheckCircle2 size={20} /> : (isActive ? <Loader2 className="step-spinner" size={20} /> : <Circle size={20} />)}
                            </div>
                            <div className="step-label">
                                {step.label}
                            </div>
                            {isPending && <div className="skeleton-line"></div>}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default AnalysisProgress;
