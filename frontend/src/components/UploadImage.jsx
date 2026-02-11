import { useState, useRef } from 'react';
import { UploadCloud } from 'lucide-react';
import './UploadImage.css';

/**
 * Componente para subir imágenes (Adaptado al nuevo diseño).
 */
function UploadImage({ onUpload, disabled }) {
    const [preview, setPreview] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileChange = (file) => {
        if (!file) return;

        // Validar tipo
        const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/bmp'];
        if (!validTypes.includes(file.type)) {
            alert('Formato no soportado. Usa PNG, JPG, JPEG, WEBP o BMP.');
            return;
        }

        // Validar tamaño (50MB max como en mockup)
        const maxSize = 50 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('Archivo demasiado grande. Máximo 50MB.');
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
                    <img src={preview} alt="Preview" className="preview-image" />
                    <p className="preview-text">Haga clic o arrastre para cambiar la imagen</p>
                </div>
            ) : (
                <>
                    <div className="upload-icon-wrapper">
                         <UploadCloud size={48} color="var(--color-accent)" />
                    </div>
                    <h3 className="upload-title">Cargar imagen para análisis</h3>
                    <p className="upload-subtitle">Arrastre un archivo o haga clic para seleccionar</p>
                    <button className="btn-upload" type="button">Seleccionar archivo</button>
                    <div className="upload-formats">
                        <span className="format-badge">PNG</span>
                        <span className="format-badge">JPG</span>
                        <span className="format-badge">WEBP</span>
                        <span className="format-badge">BMP</span>
                        <span className="format-badge">Máx. 50MB</span>
                    </div>
                </>
            )}

            <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/jpg,image/webp,image/bmp"
                onChange={(e) => handleFileChange(e.target.files?.[0])}
                style={{ display: 'none' }}
                disabled={disabled}
            />
        </div>
    );
}

export default UploadImage;
