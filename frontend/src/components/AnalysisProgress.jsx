import { useState, useEffect } from 'react';
import {
    Search,
    Zap,
    Box,
    Brain,
    Activity,
    CheckCircle2,
    Loader2
} from 'lucide-react';
import './AnalysisProgress.css';

/**
 * Componente para mostrar progreso del análisis.
 */
function AnalysisProgress() {
    const [currentStep, setCurrentStep] = useState(0);

    const steps = [
        { icon: <Search size={20} />, label: "Extracción de features (CLIP)" },
        { icon: <Box size={20} />, label: "Análisis Dimensional (multiLID)" },
        { icon: <Zap size={20} />, label: "Detector Universal (UFD)" },
        { icon: <Brain size={20} />, label: "Análisis Semántico (Asistente Forense)" },
        { icon: <Activity size={20} />, label: "Fusión de Resultados" }
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentStep((prev) => {
                if (prev < steps.length - 1) return prev + 1;
                return prev;
            });
        }, 1500); // Advance every 1.5 seconds

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="analysis-progress">
            <div className="progress-header">
                <Loader2 size={48} className="spinner" color="var(--color-accent)" />
                <h3>Analizando evidencia...</h3>
                <p>Ejecutando pipeline forense v3.0</p>
            </div>

            <ul className="progress-steps">
                {steps.map((step, index) => {
                    const isActive = index === currentStep;
                    const isCompleted = index < currentStep;

                    return (
                        <li
                            key={index}
                            className={`step ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                        >
                            <div className="step-icon">
                                {isCompleted ? <CheckCircle2 size={20} color="var(--color-success)" /> : step.icon}
                            </div>
                            <span className="step-label">{step.label}</span>
                        </li>
                    );
                })}
            </ul>

            {/* Skeleton Loader Result Card Preview */}
            <div className="skeleton-loader">
                <div className="skeleton-header"></div>
                <div className="skeleton-image"></div>
                <div className="skeleton-text"></div>
                <div className="skeleton-text short"></div>
                <div className="skeleton-text"></div>
            </div>
        </div>
    );
}

export default AnalysisProgress;
