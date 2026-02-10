# VPS Deployment Guide - DeepSeek-R1 Integration

## Prerequisites

- **VPS**: Contabo VPS (Ubuntu 22.04, 24GB RAM, 200GB NVMe)
- **Access**: SSH root or sudo access
- **Network**: Port 11434 should be accessible locally (not exposed externally)

## Step 1: SSH into Your VPS

```bash
ssh root@your-vps-ip
```

## Step 2: Install Ollama and DeepSeek-R1

Upload the installation script to your VPS:

```bash
# On your local machine
scp scripts/vps_setup/install_ollama.sh root@your-vps-ip:/tmp/

# On your VPS
chmod +x /tmp/install_ollama.sh
sudo /tmp/install_ollama.sh
```

**Expected duration**: 10-15 minutes (model download)

## Step 3: Verify Ollama Installation

```bash
# Check service status
systemctl status ollama

# Test the model
ollama run deepseek-r1:7b "Hello, are you working?"

# Check API endpoint
curl http://localhost:11434/api/tags
```

You should see `deepseek-r1:7b` in the model list.

## Step 4: Deploy LLM Microservice

Transfer the microservice files to your VPS:

```bash
# Create directory
ssh root@your-vps-ip "mkdir -p /opt/uide-forense/services"

# Upload microservice
scp services/semantic_llm_server.py root@your-vps-ip:/opt/uide-forense/services/
scp services/llm_server.service root@your-vps-ip:/tmp/
```

Install the service:

```bash
# On your VPS
sudo cp /tmp/llm_server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable llm_server
sudo systemctl start llm_server
```

## Step 5: Verify Microservice

```bash
# Check service status
systemctl status llm_server

# Test health endpoint
curl http://localhost:8000/health

# Test inference endpoint
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{
    "description": "a photo of a cat",
    "clip_features": []
  }'
```

Expected response:
```json
{
  "semantic_improbability_score": 0.XX,
  "context_collision_score": 0.XX,
  "composition_synthetic_score": 0.XX,
  "reasoning": "..."
}
```

## Step 6: Configure Your Application

On your development machine, update your `.env` or environment:

```bash
export DEEPSEEK_ENABLED=true
export DEEPSEEK_API_URL=http://your-vps-ip:8000/infer
export DEEPSEEK_TIMEOUT=30
export DEEPSEEK_MAX_RETRIES=3
```

> **Security Note**: If exposing the microservice externally, use a VPN or configure firewall rules to restrict access.

## Troubleshooting

### Ollama Service Won't Start

```bash
# Check logs
journalctl -u ollama -n 50

# Restart service
systemctl restart ollama
```

### Model Not Found

```bash
# List installed models
ollama list

# Re-download model
ollama pull deepseek-r1:7b
```

### High Memory Usage

```bash
# Check memory
free -h

# If needed, restart Ollama to free memory
systemctl restart ollama
```

### LLM Server Not Responding

```bash
# Check logs
journalctl -u llm_server -n 50

# Restart service
systemctl restart llm_server
```

## Monitoring

### Check Resource Usage

```bash
# CPU and memory
htop

# Disk usage
df -h

# Ollama process
ps aux | grep ollama
```

### View Logs

```bash
# Ollama logs
journalctl -u ollama -f

# LLM server logs
journalctl -u llm_server -f
```

## Uninstallation

If you need to remove the setup:

```bash
# Stop services
systemctl stop llm_server ollama
systemctl disable llm_server ollama

# Remove files
rm -rf /opt/uide-forense
rm /etc/systemd/system/llm_server.service
systemctl daemon-reload

# Uninstall Ollama (optional)
/usr/bin/ollama-uninstall
```
