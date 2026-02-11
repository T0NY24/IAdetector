import { useState, useRef } from 'react';
import { FileVideo } from 'lucide-react';
import './UploadVideo.css';

/**
 * Componente para subir videos (Deepfake Detection).
 */
function UploadVideo({ onUpload, disabled }) {
    const [preview, setPreview] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileChange = (file) => {
        if (!file) return;

        // Validar tipo
        const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska'];
        if (!validTypes.includes(file.type)) {
            alert('Formato no soportado. Usa MP4, AVI, MOV o MKV.');
            return;
        }

        // Validar tamaño (100MB max)
        const maxSize = 100 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('Archivo demasiado grande. Máximo 100MB.');
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
                    <video src={preview} controls className="preview-video" />
                    <p className="preview-text">Haga clic o arrastre para cambiar el video</p>
                </div>
            ) : (
                <>
                    <div className="upload-icon-wrapper">
                        <FileVideo size={48} color="var(--color-accent)" />
                    </div>
                    <h3 className="upload-title">Cargar video para análisis</h3>
                    <p className="upload-subtitle">Arrastre un archivo o haga clic para seleccionar</p>
                    <button className="btn-upload" type="button">Seleccionar archivo</button>
                    <div className="upload-formats">
                        <span className="format-badge">MP4</span>
                        <span className="format-badge">AVI</span>
                        <span className="format-badge">MOV</span>
                        <span className="format-badge">MKV</span>
                        <span className="format-badge">Máx. 100MB</span>
                    </div>
                </>
            )}

            <input
                ref={fileInputRef}
                type="file"
                accept="video/mp4,video/avi,video/quicktime,video/x-matroska"
                onChange={(e) => handleFileChange(e.target.files?.[0])}
                style={{ display: 'none' }}
                disabled={disabled}
            />
        </div>
    );
}

export default UploadVideo;
