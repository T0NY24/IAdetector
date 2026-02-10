import { useState, useEffect } from 'react';
import { Brain, Scan, Layers, ShieldCheck, Database, Loader2, CheckCircle2 } from 'lucide-react';
import './AnalysisProgress.css';

const steps = [
    { id: 'multilid', label: 'Análisis Dimensional (MultiLID)', icon: Layers },
    { id: 'ufd', label: 'Detector Universal (UFD)', icon: Scan },
    { id: 'semantic', label: 'Análisis Semántico (Asistente Forense)', icon: Brain },
    { id: 'final', label: 'Generando Informe Final', icon: ShieldCheck },
];

function AnalysisProgress() {
    const [activeStep, setActiveStep] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setActiveStep(prev => {
                if (prev < steps.length - 1) return prev + 1;
                return prev;
            });
        }, 2000); // Simulate progress every 2s

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="analysis-progress">
            <div className="progress-header">
                <Loader2 className="spinner-icon" size={48} />
                <h3>Procesando Evidencia</h3>
                <p>Ejecutando pipeline forense...</p>
            </div>

            <div className="progress-steps-list">
                {steps.map((step, index) => {
                    const isActive = index === activeStep;
                    const isCompleted = index < activeStep;
                    const Icon = step.icon;

                    return (
                        <div key={step.id} className={`step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
                            <div className="step-icon-wrapper">
                                {isCompleted ? <CheckCircle2 size={20} /> : <Icon size={20} />}
                            </div>
                            <div className="step-content">
                                <span className="step-label">{step.label}</span>
                                {isActive && <div className="skeleton-line"></div>}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default AnalysisProgress;
