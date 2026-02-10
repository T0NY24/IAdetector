# 🕵️‍♀️ UIDE Forense AI

Sistema de análisis forense digital para detección de imágenes, videos y audio sintéticos.

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/T0NY24/ProyectoForenseUIDE.git
cd ProyectoForenseUIDE
```

### 2. Crear entorno virtual

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

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar CLIP (requerido para análisis de imágenes)

```bash
pip install git+https://github.com/openai/CLIP.git
```

### 5. Verificar FFmpeg (requerido para audio/video)

```bash
ffmpeg -version
```

---

## 🚀 Ejecución

### Ejecutar la aplicación completa

```bash
python app.py
```

Acceder en: http://localhost:7860

### Probar solo el módulo de imágenes

```bash
python test_image_forensics.py
```

---

## 📁 Estructura del Proyecto

```
ProyectoForenseUIDE/
├── app.py                    # Interfaz Gradio
├── config.py                 # Configuración
├── modules/
│   ├── image_forensics/      # Detector de imágenes v3.0+
│   │   ├── detector.py       # Orquestador
│   │   ├── multilid_expert.py
│   │   ├── ufd_expert.py
│   │   ├── semantic_expert.py  # NUEVO
│   │   └── fusion_engine.py
│   ├── video_forensics.py
│   └── audio_forensics.py
├── weights/
└── samples/
```

---

## 📞 Contacto

**Universidad Internacional del Ecuador (UIDE)**  
Equipo: Anthony Pérez, Bruno Ortega, Manuel Pacheco

---

© 2026 UIDE - Licencia Académica