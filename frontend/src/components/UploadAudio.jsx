import { useState, useRef } from 'react';
import './UploadAudio.css';

/**
 * Componente para subir archivos de audio (Synthetic Audio Detection).
 */
function UploadAudio({ onUpload, disabled }) {
    const [preview, setPreview] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileChange = (file) => {
        if (!file) return;

        // Validar tipo
        const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/ogg', 'audio/flac'];
        if (!validTypes.includes(file.type)) {
            alert('Formato no soportado. Usa MP3, WAV, M4A, OGG o FLAC.');
            return;
        }

        // Validar tamaño (20MB max)
        const maxSize = 20 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('Archivo demasiado grande. Máximo 20MB.');
            return;
        }

        // Preview
        const reader = new FileReader();
        reader.onloadend = () => {
            setPreview(reader.result);
        };
        reader.readAsDataURL(file);

        // Callback
        onUpload(file);
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (!disabled && e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileChange(e.dataTransfer.files[0]);
        }
    };

    const handleClick = () => {
        if (!disabled) fileInputRef.current?.click();
    };

    return (
        <div
            className={`upload-container ${dragActive ? 'drag-active' : ''} ${disabled ? 'disabled' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={handleClick}
        >
            {preview ? (
                <div className="preview-container">
                    <audio src={preview} controls className="preview-audio" />
                    <p className="preview-text">Haga clic o arrastre para cambiar el audio</p>
                </div>
            ) : (
                <>
                    <svg className="upload-icon" viewBox="0 0 24 24">
                        <path d="M9 18V5l12-2v13" />
                        <circle cx="6" cy="18" r="3" />
                        <circle cx="18" cy="16" r="3" />
                    </svg>
                    <h3 className="upload-title">Cargar audio para análisis</h3>
                    <p className="upload-subtitle">Arrastre un archivo o haga clic para seleccionar</p>
                    <button className="btn-upload" type="button">Seleccionar archivo</button>
                    <div className="upload-formats">
                        <span className="format-badge">MP3</span>
                        <span className="format-badge">WAV</span>
                        <span className="format-badge">M4A</span>
                        <span className="format-badge">OGG</span>
                        <span className="format-badge">Máx. 20MB</span>
                    </div>
                </>
            )}

            <input
                ref={fileInputRef}
                type="file"
                accept="audio/mpeg,audio/wav,audio/mp4,audio/ogg,audio/flac"
                onChange={(e) => handleFileChange(e.target.files?.[0])}
                style={{ display: 'none' }}
                disabled={disabled}
            />
        </div>
    );
}

export default UploadAudio;
