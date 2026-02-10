# Deployment Guide - UIDE Forense AI 3.0+
## Flask + React + DeepSeek-R1 en VPS

---

## 🎯 Objetivo

Desplegar el sistema completo en VPS Ubuntu 22.04:
- **Backend Flask** (Gunicorn) → Puerto 5000
- **Frontend React** (build estático) → /var/www/html
- **Nginx** (reverse proxy) → Puerto 80/443
- **Ollama + DeepSeek-R1** → Puerto 11434 (localhost only)

---

## 📋 Prerrequisitos

- VPS Ubuntu 22.04 con 24GB RAM
- Acceso root/sudo
- Python 3.8+
- Node.js 18+
- Nginx
- Ollama instalado (ver scripts/vps_setup/install_ollama.sh)

---

## 🚀 Paso 1: Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3-venv python3-pip nginx git

# Instalar Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar instalaciones
python3 --version
node --version
npm --version
nginx -v
```

---

## 🔧 Paso 2: Desplegar Backend Flask

### 2.1. Clonar Proyecto

```bash
# Crear directorio
sudo mkdir -p /opt/uide-forense
sudo chown -R $USER:$USER /opt/uide-forense

# Copiar archivos (desde local)
# Opción 1: Git
cd /opt/uide-forense
git clone <tu-repo-url> .

# Opción 2: SCP desde tu máquina local
# scp -r C:\Users\anper\Downloads\ProyectoForenseUIDE/* user@vps-ip:/opt/uide-forense/
```

### 2.2. Configurar Python Virtual Environment

```bash
cd /opt/uide-forense

# Crear venv
python3 -m venv venv

# Activar
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3. Configurar Variables de Entorno

```bash
# Crear archivo .env
nano /opt/uide-forense/.env
```

Contenido:
```env
# Flask
FLASK_SECRET_KEY=tu-secret-key-muy-segura-aqui
FLASK_DEBUG=False

# DeepSeek
DEEPSEEK_ENABLED=true
DEEPSEEK_API_URL=http://localhost:11434/api/generate
DEEPSEEK_MODEL=deepseek-r1:7b
DEEPSEEK_TIMEOUT=60
DEEPSEEK_MAX_RETRIES=3

# CORS
CORS_ORIGINS=http://your-domain.com,https://your-domain.com

# Device
DEVICE=cpu
```

### 2.4. Probar Backend Manualmente

```bash
cd /opt/uide-forense/backend
source ../venv/bin/activate

# Probar app
python app.py

# Debería iniciar en http://0.0.0.0:5000
# Ctrl+C para detener
```

### 2.5. Configurar Servicio Systemd

```bash
# Copiar archivo de servicio
sudo cp /opt/uide-forense/backend/uide-backend.service /etc/systemd/system/

# Crear directorio de logs
sudo mkdir -p /var/log/uide-forense
sudo chown www-data:www-data /var/log/uide-forense

# Reload systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable uide-backend

# Iniciar servicio
sudo systemctl start uide-backend

# Verificar status
sudo systemctl status uide-backend

# Ver logs
sudo journalctl -u uide-backend -f
```

---

## ⚛️ Paso 3: Desplegar Frontend React

### 3.1. Build del Frontend

```bash
cd /opt/uide-forense/frontend

# Instalar dependencias
npm install

# Build para producción
npm run build

# El build estará en: frontend/dist/
```

### 3.2. Copiar Build a Nginx

```bash
# Crear directorio
sudo mkdir -p /var/www/html/uide-forense

# Copiar archivos
sudo cp -r /opt/uide-forense/frontend/dist/* /var/www/html/uide-forense/

# Permisos
sudo chown -R www-data:www-data /var/www/html/uide-forense
sudo chmod -R 755 /var/www/html/uide-forense
```

---

## 🌐 Paso 4: Configurar Nginx

### 4.1. Instalar Configuración

```bash
# Copiar configuración
sudo cp /opt/uide-forense/deployment/nginx/uide-forense.conf /etc/nginx/sites-available/

# Editar dominio/IP
sudo nano /etc/nginx/sites-available/uide-forense.conf
# Cambiar "your-domain.com" por tu dominio o IP

# Crear symlink
sudo ln -s /etc/nginx/sites-available/uide-forense.conf /etc/nginx/sites-enabled/

# Eliminar default (opcional)
sudo rm /etc/nginx/sites-enabled/default

# Probar configuración
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 4.2. Verificar Nginx

```bash
sudo systemctl status nginx

# Si hay errores
sudo journalctl -u nginx -n 50
```

---

## 🤖 Paso 5: Verificar DeepSeek/Ollama

```bash
# Verificar que Ollama está corriendo
sudo systemctl status ollama

# Probar modelo
curl http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:7b", "prompt":"hola", "stream":false}'

# Debería responder con JSON
```

---

## ✅ Paso 6: Verificación End-to-End

### 6.1. Health Check Backend

```bash
curl http://localhost:5000/api/health
```

Esperado:
```json
{
  "status": "healthy",
  "services": {
    "flask": "ok",
    "clip": "ok",
    "deepseek": "enabled"
  }
}
```

### 6.2. Acceder a Frontend

Abrir en navegador:
```
http://your-domain.com
```

Debería mostrar la interfaz de UIDE Forense AI 3.0+

### 6.3. Probar Upload y Análisis

1. Subir una imagen de prueba
2. Verificar que el análisis completa
3. Revisar logs del backend:

```bash
sudo journalctl -u uide-backend -f
```

---

## 🔒 Paso 7: SSL/HTTPS (Opcional)

### 7.1. Instalar Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### 7.2. Obtener Certificado

```bash
sudo certbot --nginx -d your-domain.com
```

### 7.3. Auto-Renewal

```bash
# Verificar timer
sudo systemctl status certbot.timer

# Probar renewal
sudo certbot renew --dry-run
```

---

## 🔧 Troubleshooting

### Backend No Inicia

```bash
# Ver logs detallados
sudo journalctl -u uide-backend -n 100 --no-pager

# Verificar permisos
ls -la /opt/uide-forense/backend

# Verificar Python dependencies
source /opt/uide-forense/venv/bin/activate
pip list
```

### Frontend No Carga

```bash
# Verificar archivos
ls -la /var/www/html/uide-forense/

# Ver logs Nginx
sudo tail -f /var/log/nginx/error.log
```

### DeepSeek Falla

```bash
# Verificar Ollama
sudo systemctl status ollama

# Ver logs Ollama
sudo journalctl -u ollama -f

# Reiniciar Ollama
sudo systemctl restart ollama

# Re-pull modelo
ollama pull deepseek-r1:7b
```

### CORS Errors

```bash
# Verificar configuración Flask en config.py
# O agregar headers en Nginx:

sudo nano /etc/nginx/sites-available/uide-forense.conf

# Agregar en location /api:
add_header 'Access-Control-Allow-Origin' '*';
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
```

---

## 📊 Monitoring

### Logs en Tiempo Real

```bash
# Backend
sudo journalctl -u uide-backend -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Ollama
sudo journalctl -u ollama -f
```

### Recursos del Sistema

```bash
# CPU, RAM, disco
htop

# Uso de GPU (si aplica)
nvidia-smi
```

---

## 🔄 Actualizar Aplicación

### Backend

```bash
cd /opt/uide-forense
git pull  # o copiar nuevos archivos

source venv/bin/activate
pip install -r requirements.txt

sudo systemctl restart uide-backend
```

### Frontend

```bash
cd /opt/uide-forense/frontend
npm install
npm run build

sudo cp -r dist/* /var/www/html/uide-forense/
sudo systemctl reload nginx
```

---

## ✨ Resultado Final

Después de completar todos los pasos:

✅ Frontend React en `http://your-domain.com`  
✅ Backend Flask en `http://your-domain.com/api`  
✅ DeepSeek-R1 integrado y funcionando  
✅ Análisis forense end-to-end operativo  
✅ Sistema completo en producción  

**¡Tu migración de Gradio a Flask + React está completa!** 🚀
