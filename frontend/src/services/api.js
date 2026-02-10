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
