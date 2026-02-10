/**
 * API Service - Cliente para Flask Backend
 * 
 * Consumo de todos los endpoints REST.
 */

const API_BASE_URL = '/api';

/**
 * Analiza una imagen usando el pipeline completo.
 * 
 * @param {File} imageFile - Archivo de imagen
 * @param {boolean} useDeepseek - Si usar DeepSeek-R1 (default: true)
 * @returns {Promise<Object>} - Resultado del análisis
 */
export const analyzeImage = async (imageFile, useDeepseek = true) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('use_deepseek', useDeepseek.toString());

    const response = await fetch(`${API_BASE_URL}/analyze_image`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Analysis failed');
    }

    return await response.json();
};

/**
 * Obtiene el historial de análisis.
 *
 * @param {number} limit - Límite de resultados (default: 20)
 * @returns {Promise<Object>} - Historial de análisis
 */
export const getHistory = async (limit = 20) => {
    const response = await fetch(`${API_BASE_URL}/history?limit=${limit}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch history');
    }

    return await response.json();
};

/**
 * Análisis semántico con DeepSeek-R1.
 * 
 * @param {string} description - Descripción de la imagen
 * @returns {Promise<Object>} - Scores semánticos
 */
export const analyzeSemanticDeepseek = async (description) => {
    const response = await fetch(`${API_BASE_URL}/semantic/deepseek`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ description })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'DeepSeek analysis failed');
    }

    return await response.json();
};

/**
 * Análisis semántico con CLIP (fallback).
 * 
 * @param {string} imagePath - Ruta de la imagen
 * @returns {Promise<Object>} - Scores semánticos
 */
export const analyzeSemanticClip = async (imagePath) => {
    const response = await fetch(`${API_BASE_URL}/semantic/clip`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image_path: imagePath })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'CLIP analysis failed');
    }

    return await response.json();
};

/**
 * Fusiona resultados de expertos.
 * 
 * @param {Object} results - Resultados de expertos
 * @returns {Promise<Object>} - Resultado de fusión
 */
export const fuseResults = async (results) => {
    const response = await fetch(`${API_BASE_URL}/fusion`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(results)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Fusion failed');
    }

    return await response.json();
};

/**
 * Sube una imagen.
 * 
 * @param {File} imageFile - Archivo de imagen
 * @returns {Promise<Object>} - Info de la imagen subida
 */
export const uploadImage = async (imageFile) => {
    const formData = new FormData();
    formData.append('file', imageFile);

    const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
    }

    return await response.json();
};

/**
 * Health check del backend.
 * 
 * @returns {Promise<Object>} - Estado de servicios
 */
export const checkHealth = async () => {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
        throw new Error('Health check failed');
    }

    return await response.json();
};

/**
 * Analiza un video para detectar deepfakes.
 * 
 * @param {File} videoFile - Archivo de video
 * @returns {Promise<Object>} - Resultado del análisis
 */
export const analyzeVideo = async (videoFile) => {
    const formData = new FormData();
    formData.append('video', videoFile);

    const response = await fetch(`${API_BASE_URL}/analyze_video`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Video analysis failed');
    }

    return await response.json();
};

/**
 * Analiza un archivo de audio para detectar si es sintético.
 * 
 * @param {File} audioFile - Archivo de audio
 * @returns {Promise<Object>} - Resultado del análisis
 */
export const analyzeAudio = async (audioFile) => {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const response = await fetch(`${API_BASE_URL}/analyze_audio`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Audio analysis failed');
    }

    return await response.json();
};
