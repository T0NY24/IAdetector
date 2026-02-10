# Desarrollo Local - UIDE Forense AI
## Guía para desarrollo en Windows/Linux

---

## 🏠 Configuración para Desarrollo

### Backend (Flask)

```bash
# 1. Crear y activar venv
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 2. Instalar dependencias
pip install -r ../requirements.txt

# 3. Configurar variables de entorno
# Crear archivo .env en la raíz:
FLASK_DEBUG=True
DEEPSEEK_ENABLED=false  # O true si tienes Ollama local
DEEPSEEK_API_URL=http://localhost:11434/api/generate

# 4. Iniciar Flask
python app.py

# Debe correr en http://localhost:5000
```

### Frontend (React)

```bash
# 1. Instalar dependencias
cd frontend
npm install

# 2. Iniciar dev server
npm run dev

# Debe correr en http://localhost:5173
# El proxy en vite.config.js redirige /api a Flask
```

---

## 🧪 Pruebas

### Test Backend

```bash
# Health check
curl http://localhost:5000/api/health

# Upload test (con PowerShell)
$boundary = "WebKitFormBoundary$(Get-Random)"
Invoke-WebRequest -Uri http://localhost:5000/api/upload `
  -Method POST `
  -InFile "test.jpg" `
  -ContentType "multipart/form-data; boundary=$boundary"
```

### Test Frontend

```
1. Abrir http://localhost:5173
2. Subir una imagen
3. Verificar que hace request a http://localhost:5000/api/analyze_image
4. Ver resultados
```

---

## 📝 Notas

- El proxy de Vite permite que `/api` se redirija a Flask automáticamente
- Para producción, usa `npm run build` y despliega el `/dist` folder
