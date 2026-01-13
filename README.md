# 🕵️‍♀️ UIDE Forense AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/🤗_Hugging_Face-Models-FFD21E?style=for-the-badge)
![License](https://img.shields.io/badge/License-Academic-00ADD8?style=for-the-badge)

### Sistema Multimodal de Detección de Deepfakes y Contenido Sintético

**Plataforma basada en Inteligencia Artificial y Arquitectura Modular para análisis forense de Imagen, Video y Audio**

---

[📋 Características](#-características-principales) • [⚙️ Instalación](#️-instalación) • [🚀 Uso](#-guía-de-uso) • [🏗️ Arquitectura](#️-arquitectura-del-sistema) • [📚 Documentación](#-documentación-técnica)

</div>

---

## 📋 Características Principales

### 🖼️ **Análisis Forense de Imágenes**
Sistema de detección híbrida basado en ensamble de modelos especializados:

- **Motor de Detección GAN**: Análisis de artefactos generados por StyleGAN, ProGAN y FaceApp mediante arquitectura ResNet50
- **Motor de Detección por Difusión**: Identificación de contenido generado por Stable Diffusion, DALL-E 3 y Midjourney usando Vision Transformers (ViT)
- **Sistema de Ensamble Inteligente**: Combinación ponderada de ambos motores para máxima precisión y cobertura
- **Reportes Detallados**: Identificación del origen probable y visualización de mapas de calor de manipulación

### 🔊 **Detección de Audio Sintético**
Análisis espectral avanzado para identificar voces artificiales:

- Detección de voces clonadas generadas por ElevenLabs, RVC, Coqui TTS y similares
- Análisis de características espectrales mediante procesamiento con Librosa
- Clasificación binaria: Audio Humano vs Audio Sintético
- Generación de espectrogramas Mel para visualización de anomalías
- Soporte para múltiples formatos: WAV, MP3, FLAC, OGG

### 🎥 **Detección de Deepfakes en Video**
Sistema de análisis temporal para manipulaciones faciales:

- Análisis frame-por-frame mediante arquitectura XceptionNet
- Detección de Face Swap y reenactment facial
- Extracción y seguimiento de rostros mediante MTCNN
- Muestreo inteligente optimizado para rendimiento
- Generación de gráficos de confianza temporal

### 🎨 **Arquitectura y Experiencia de Usuario**
Diseño modular profesional con interfaz intuitiva:

- **Clean Architecture**: Separación de responsabilidades (Core, Modules, Utils)
- **Gestión Eficiente de Recursos**: Carga diferida (Lazy Loading) de modelos
- **Interfaz Gradio Interactiva**: Reportes visuales en tiempo real
- **Sistema de Logs**: Trazabilidad completa de operaciones
- **Manejo Robusto de Errores**: Validaciones y recuperación automática

---

## 💻 Requisitos del Sistema

### Requisitos de Hardware

| Componente | Mínimo | Recomendado | Óptimo |
|------------|--------|-------------|--------|
| **RAM** | 8 GB | 16 GB | 32 GB |
| **CPU** | Intel i5 / Ryzen 5 | Intel i7 / Ryzen 7 | Intel i9 / Ryzen 9 |
| **GPU** | Integrada | NVIDIA GTX 1060 (6GB) | NVIDIA RTX 3060+ |
| **Almacenamiento** | 5 GB libres | 10 GB libres | SSD con 20 GB |
| **Conexión** | Internet (primera ejecución) | Banda ancha | - |

### Requisitos de Software

- **Sistema Operativo**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: Versión 3.9, 3.10 o 3.11 (recomendado 3.10)
- **FFmpeg**: Requerido para procesamiento de audio/video
  - Windows: Descargar desde [ffmpeg.org](https://ffmpeg.org) y agregar al PATH
  - Linux: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`

---

## ⚙️ Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/T0NY24/ProyectoForenseUIDE.git
cd ProyectoForenseUIDE
```

### Paso 2: Crear Entorno Virtual

**Windows:**
```bash
py -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
py -m pip install -r requirements.txt
```

> **Nota**: La instalación puede tardar varios minutos dependiendo de la velocidad de conexión. Se descargarán aproximadamente 2-3 GB de dependencias.

### Paso 4: Verificar Instalación de FFmpeg

```bash
ffmpeg -version
```

Si el comando no es reconocido, consulte la [guía de instalación de FFmpeg](https://ffmpeg.org/download.html).

### Paso 5: Configuración de Modelos

Los modelos de Hugging Face se descargarán automáticamente en la primera ejecución. Asegúrese de tener:

- Conexión a internet estable
- Espacio suficiente en disco (~2 GB adicionales)
- El archivo `blur_jpg_prob0.1.pth` en la carpeta `weights/`

---

## 🚀 Guía de Uso

### Iniciar la Aplicación

```bash
py app.py
```

**Primera ejecución:**
- El sistema descargará los modelos necesarios (~1-2 GB)
- Este proceso puede tardar 5-10 minutos
- Los modelos se almacenan en caché para ejecuciones futuras

**Acceso a la interfaz:**

La aplicación se abrirá automáticamente en tu navegador en:
```
http://localhost:7860
```

Si no se abre automáticamente, copia y pega la URL en tu navegador.

---

### 📸 Módulo de Análisis de Imágenes

**Proceso de análisis:**

1. **Cargar imagen**: Haz clic en "Upload" o arrastra una imagen (JPG, PNG, WebP)
2. **Ejecutar análisis**: El sistema procesará la imagen con ambos motores
3. **Revisar resultados**:
   - Probabilidad de manipulación (0-100%)
   - Técnica de generación detectada (GAN vs Difusión)
   - Visualización de áreas sospechosas
   - Origen probable (StyleGAN, Midjourney, etc.)

**Formatos soportados**: JPG, JPEG, PNG, WebP, BMP  
**Tamaño máximo**: 10 MB  
**Resolución recomendada**: 512x512 a 2048x2048 píxeles

---

### 🎵 Módulo de Análisis de Audio

**Opciones de entrada:**

1. **Subir archivo**: Arrastra o selecciona un archivo de audio
2. **Grabar en vivo**: Usa el micrófono para grabar directamente

**Proceso de análisis:**

1. Haz clic en **"Analizar Audio"**
2. El sistema generará:
   - Espectrograma Mel del audio
   - Clasificación (Humano / Sintético)
   - Nivel de confianza (0-100%)
   - Características espectrales detectadas

**Formatos soportados**: WAV, MP3, FLAC, OGG, M4A  
**Duración máxima**: 60 segundos (recomendado: 10-30 segundos)  
**Calidad recomendada**: 16-bit, 44.1 kHz o superior

---

### 🎬 Módulo de Análisis de Video

**Proceso de análisis:**

1. **Cargar video**: Sube un archivo de video (MP4, AVI, MOV)
2. **Configurar parámetros** (opcional):
   - Frames a analizar
   - Umbral de detección
3. **Ejecutar análisis**: El sistema procesará el video frame por frame
4. **Revisar resultados**:
   - Gráfico de confianza temporal
   - Frames sospechosos identificados
   - Porcentaje de frames manipulados

**Formatos soportados**: MP4, AVI, MOV, MKV  
**Duración máxima**: 5 minutos  
**Resolución recomendada**: 720p o superior

---

## 🏗️ Arquitectura del Sistema

### Estructura de Directorios

```
ProyectoForenseUIDE/
│
├── 📁 core/                      # Núcleo del sistema
│   ├── model_manager.py          # Gestor centralizado de modelos (Singleton)
│   └── processor.py              # Pipelines de preprocesamiento
│
├── 📁 modules/                   # Módulos de detección independientes
│   ├── image_forensics.py        # Ensamble GAN + Difusión
│   ├── audio_forensics.py        # Detector de audio sintético
│   └── video_forensics.py        # Detector de deepfakes XceptionNet
│
├── 📁 utils/                     # Utilidades transversales
│   ├── file_handlers.py          # Validación y manejo de archivos
│   ├── plotting.py               # Generación de visualizaciones
│   └── logger.py                 # Sistema de logging
│
├── 📁 weights/                   # Pesos de modelos locales
│   └── blur_jpg_prob0.1.pth      # Modelo GAN ResNet50
│
├── 📁 cache/                     # Caché de modelos HuggingFace
├── 📁 temp/                      # Archivos temporales
│
├── 📄 app.py                     # Interfaz Gradio (Capa de presentación)
├── 📄 config.py                  # Configuración global del sistema
├── 📄 requirements.txt           # Dependencias Python
└── 📄 README.md                  # Este archivo
```

### Flujo de Procesamiento

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT DEL USUARIO                        │
│              (Imagen / Audio / Video)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  ROUTER DE TIPO                             │
│            (Detector automático de formato)                 │
└──────┬─────────────────┬─────────────────┬──────────────────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   IMAGEN    │   │    AUDIO    │   │    VIDEO    │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Motor GAN   │   │  Librosa    │   │   MTCNN     │
│ (ResNet50)  │   │ Extracción  │   │  Extracción │
└──────┬──────┘   │ Espectral   │   │  de Rostros │
       │          └──────┬──────┘   └──────┬──────┘
       │                 │                 │
┌──────┴──────┐          ▼                 ▼
│ Motor Dif.  │   ┌─────────────┐   ┌─────────────┐
│   (ViT)     │   │ Transformer │   │ XceptionNet │
└──────┬──────┘   │    Audio    │   │   Frame x   │
       │          └──────┬──────┘   │    Frame    │
       │                 │          └──────┬──────┘
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Lógica de  │   │ Clasificador│   │  Agregación │
│  Ensamble   │   │   Binario   │   │  Temporal   │
│    (MAX)    │   └──────┬──────┘   └──────┬──────┘
└──────┬──────┘          │                 │
       │                 │                 │
       └────────┬────────┴────────┬────────┘
                │                 │
                ▼                 ▼
        ┌───────────────────────────────┐
        │    GENERACIÓN DE REPORTES     │
        │  (Visualizaciones + Métricas) │
        └───────────────┬───────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  OUTPUT USUARIO │
              │  (Interfaz Web) │
              └─────────────────┘
```

### Patrones de Diseño Implementados

- **Singleton**: Gestor de modelos (evita duplicación en memoria)
- **Strategy**: Diferentes estrategias de detección por modalidad
- **Factory**: Creación dinámica de procesadores según tipo de archivo
- **Observer**: Sistema de logging y eventos
- **Facade**: Interfaz simplificada para operaciones complejas

---

## 📚 Documentación Técnica

### Modelos de IA Utilizados

#### 1️⃣ **Detección de Imágenes: Estrategia de Ensamble**

**Motor GAN (Generación Antigua)**
- **Arquitectura**: CNNDetection basada en ResNet50
- **Especialidad**: StyleGAN, ProGAN, FaceApp
- **Técnica**: Análisis de patrones de tablero de ajedrez
- **Referencia**: Wang et al. - "CNN-generated images are surprisingly easy to spot... for now"

**Motor Difusión (Generación Moderna)**
- **Arquitectura**: Vision Transformer (ViT-B/16)
- **Especialidad**: Stable Diffusion, DALL-E 3, Midjourney
- **Técnica**: Detección de ruido latente gaussiano
- **Fine-tuning**: Dataset propietario de 100K imágenes sintéticas

**Lógica de Ensamble**
```python
prediccion_final = max(score_gan, score_difusion)
origen = "GAN" if score_gan > score_difusion else "Difusión"
```

#### 2️⃣ **Detección de Audio Sintético**

**Modelo Base**
- **Arquitectura**: Wav2Vec 2.0 / HuBERT
- **Especialidad**: TTS (Text-to-Speech) y Voice Cloning
- **Técnica**: Análisis de coeficientes MFCC y espectrograma Mel

**Características Analizadas**
- Discontinuidades espectrales
- Artefactos de síntesis en altas frecuencias
- Patrones de pitch antinaturales
- Ausencia de microfonía ambiental

#### 3️⃣ **Detección de Deepfakes en Video**

**Modelo Principal**
- **Arquitectura**: XceptionNet (Depthwise Separable Convolutions)
- **Dataset de Entrenamiento**: FaceForensics++ (1.8M frames)
- **Métodos Detectados**: Face2Face, FaceSwap, NeuralTextures, Deepfakes

**Pipeline de Procesamiento**
1. Extracción de rostros (MTCNN)
2. Normalización y aumento de datos
3. Inferencia por frame
4. Agregación temporal con ventana deslizante

---

## ⚠️ Limitaciones Conocidas

### Limitaciones Técnicas

1. **Procesamiento de Audio**
   - El ruido de fondo intenso puede afectar la precisión
   - Música de fondo reduce la efectividad del análisis
   - Audios de menos de 3 segundos pueden dar falsos positivos

2. **Análisis de Imágenes**
   - Imágenes con post-procesamiento intenso (filtros de Instagram) pueden confundir al modelo ViT
   - Compresión JPEG agresiva puede generar falsos positivos
   - Imágenes de resolución muy baja (<256x256) tienen menor precisión

3. **Detección de Video**
   - Videos con mala iluminación reducen la precisión
   - Múltiples rostros simultáneos requieren más recursos
   - Videos de más de 5 minutos requieren tiempo considerable de procesamiento

4. **Recursos del Sistema**
   - La primera ejecución requiere conexión a internet
   - El uso simultáneo de los tres módulos consume ~12 GB de RAM
   - Sin GPU, el procesamiento puede ser 5-10x más lento

### Limitaciones Metodológicas

- Los resultados son **probabilísticos**, no determinísticos
- La precisión varía según la calidad del contenido sintético
- Nuevas técnicas de generación pueden no ser detectadas hasta actualización del modelo
- No garantiza detección de técnicas de evasión adversarial

---

## ⚖️ Consideraciones Éticas y Legales

### Uso Responsable

Esta herramienta ha sido desarrollada exclusivamente con fines **académicos y de investigación** como trabajo de titulación en Ingeniería en Tecnologías de la Información.

**IMPORTANTE:**
- ❌ Los resultados **NO constituyen prueba pericial legal**
- ❌ No debe usarse como única evidencia en procesos judiciales
- ❌ No reemplaza la opinión de peritos forenses certificados
- ✅ Es una herramienta de apoyo para análisis preliminar
- ✅ Puede usarse en contextos educativos y de investigación

### Privacidad y Datos

- Los archivos procesados **NO se almacenan** en servidores externos
- Todo el procesamiento ocurre **localmente** en su máquina
- No se recopilan datos personales ni estadísticas de uso
- Los archivos temporales se eliminan automáticamente

### Transparencia Algorítmica

Los modelos de IA pueden presentar sesgos inherentes:
- Mejor rendimiento en rostros con buena iluminación
- Posible sesgo racial en datasets de entrenamiento
- Mayor precisión en contenido en inglés/español

---




## 🤝 Contribuciones

Este proyecto es de código cerrado durante el período de evaluación académica. Después de la sustentación, se evaluará la posibilidad de liberar el código bajo licencia académica.

### Reporte de Bugs

Si encuentras un error, por favor contacta al equipo de desarrollo con:
- Descripción detallada del problema
- Pasos para reproducir el error
- Archivos de log (si están disponibles)

---

## 📞 Contacto y Soporte

### Equipo de Desarrollo

**Universidad Internacional del Ecuador (UIDE)**  
Facultad de Ingeniería en Tecnologías de la Información

| Integrante | Rol | Email |
|------------|-----|-------|
| **Anthony Pérez** |
| **Bruno Ortega** | 
| **Manuel Pacheco** | 


---

## 📖 Referencias Académicas

1. Wang, S. Y., et al. (2020). "CNN-generated images are surprisingly easy to spot... for now." *CVPR 2020*.

2. Rossler, A., et al. (2019). "FaceForensics++: Learning to Detect Manipulated Facial Images." *ICCV 2019*.

3. Chollet, F. (2017). "Xception: Deep Learning with Depthwise Separable Convolutions." *CVPR 2017*.

4. Dosovitskiy, A., et al. (2021). "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale." *ICLR 2021*.

5. Baevski, A., et al. (2020). "wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations." *NeurIPS 2020*.

---

## 📄 Licencia

**Licencia Académica**

© 2025 Universidad Internacional del Ecuador (UIDE)

---

<div align="center">


</div>