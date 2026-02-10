# DeepSeek-R1 Integration - Quick Start Guide

## Overview

This integration adds DeepSeek-R1:7b LLM reasoning capabilities to the UIDE Forense AI semantic analysis module. The LLM provides deep reasoning about semantic plausibility, context coherence, and AI-typical composition patterns.

## Architecture

```
┌─────────────────────────────────────────────┐
│  UIDE Forense AI (Windows Development)      │
│  ├─ semantic_expert.py                      │
│  │  ├─ DeepSeekSemanticEngine               │
│  │  └─ SemanticForensicsExpert (CLIP)       │
│  └─ services/llm_client.py                  │
│     └─ HTTP Client                          │
└──────────────┬──────────────────────────────┘
               │
               │ HTTP (localhost:8000)
               ▼
┌─────────────────────────────────────────────┐
│  VPS (Ubuntu 22.04, 24GB RAM)               │
│  ├─ semantic_llm_server.py (Port 8000)      │
│  │  ├─ Request Queue                        │
│  │  ├─ Retry Logic                          │
│  │  └─ Prompt Sanitization                  │
│  │                                           │
│  └─ Ollama Service (Port 11434)             │
│     └─ DeepSeek-R1:7b Model                 │
└─────────────────────────────────────────────┘
```

## Installation

### 1. VPS Setup (One-time)

SSH into your Contabo VPS:

```bash
ssh root@your-vps-ip
```

Upload and run the installation script:

```bash
# On your local machine:
scp scripts/vps_setup/install_ollama.sh root@your-vps-ip:/tmp/

# On VPS:
chmod +x /tmp/install_ollama.sh
sudo /tmp/install_ollama.sh
```

This script will:
- ✅ Install Ollama
- ✅ Download DeepSeek-R1:7b (~4.7GB)
- ✅ Configure systemd service
- ✅ Test the model

**Expected Duration:** 10-15 minutes

### 2. Deploy LLM Microservice

```bash
# Create directory
ssh root@your-vps-ip "mkdir -p /opt/uide-forense/services"

# Upload files
scp services/semantic_llm_server.py root@your-vps-ip:/opt/uide-forense/services/
scp services/llm_server.service root@your-vps-ip:/tmp/

# Install service
ssh root@your-vps-ip << 'EOF'
cp /tmp/llm_server.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable llm_server
systemctl start llm_server
EOF
```

Verify:
```bash
ssh root@your-vps-ip "systemctl status llm_server"
```

### 3. Local Development Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```bash
# Windows PowerShell:
$env:DEEPSEEK_ENABLED="true"
$env:DEEPSEEK_API_URL="http://your-vps-ip:8000/infer"

# Linux/Mac:
export DEEPSEEK_ENABLED=true
export DEEPSEEK_API_URL=http://your-vps-ip:8000/infer
```

## Usage

### Basic Example

```python
from modules.image_forensics.semantic_expert import SemanticForensicsExpert, DeepSeekSemanticEngine
from modules.image_forensics.feature_extractor import CLIPFeatureExtractor
from PIL import Image

# Initialize
clip_extractor = CLIPFeatureExtractor()
deepseek_engine = DeepSeekSemanticEngine(enabled=True)

semantic_expert = SemanticForensicsExpert(
    feature_extractor=clip_extractor,
    deepseek_engine=deepseek_engine,
    use_deepseek=True
)

# Analyze image
image = Image.open("test_image.jpg")
description = "A photorealistic image of a cat in a modern living room"

result = semantic_expert.analyze(
    image_input=image,
    image_description=description
)

print(f"Semantic Score: {result.score:.2f}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Evidence: {result.evidence}")
```

### With Fusion Engine

The fusion engine already has the priority logic implemented:

```python
from modules.image_forensics.fusion_engine import FusionEngine

engine = FusionEngine()

# semantic_result from above
# multilid_result, ufd_result from other experts

final_result = engine.fuse(
    multilid_result=multilid_result,
    ufd_result=ufd_result,
    semantic_result=result  # DeepSeek-powered result
)

# Priority logic:
# - If semantic score > 0.50 → "GENERADA POR IA (CONFIRMADO)"
# - Otherwise, normal fusion logic applies
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEEPSEEK_ENABLED` | `false` | Enable/disable DeepSeek |
| `DEEPSEEK_API_URL` | `http://localhost:8000/infer` | LLM microservice URL |
| `DEEPSEEK_TIMEOUT` | `30` | Request timeout (seconds) |
| `DEEPSEEK_MAX_RETRIES` | `3` | Max retry attempts |

### config.py

```python
# DeepSeek is automatically configured from environment variables
# Or you can set directly in config.py:

DEEPSEEK_ENABLED = True
DEEPSEEK_API_URL = "http://your-vps-ip:8000/infer"
DEEPSEEK_TIMEOUT = 30
DEEPSEEK_MAX_RETRIES = 3
```

## Testing

### Unit Tests

```bash
python -m pytest tests/test_deepseek_integration.py -v
```

### Connectivity Test

```bash
python tests/test_deepseek_integration.py --connectivity
```

Expected output:
```
🔍 Testing LLM server connectivity...
✅ LLM server is healthy
🧪 Testing inference...
✅ Inference successful:
   Improbability: 0.45
   Collision: 0.38
   Composition: 0.52
```

## Troubleshooting

### DeepSeek Not Being Used

**Symptoms:** Logs show "Using CLIP-based analysis" instead of "Using DeepSeek-R1"

**Solutions:**
1. Check `DEEPSEEK_ENABLED=true` is set
2. Verify LLM server is running: `systemctl status llm_server`
3. Test connectivity: `curl http://your-vps-ip:8000/health`

### Ollama Model Not Found

**Symptoms:** Error "model 'deepseek-r1:7b' not found"

**Solution:**
```bash
ssh root@your-vps-ip
ollama pull deepseek-r1:7b
systemctl restart llm_server
```

### High Latency (>30s)

**Symptoms:** Requests timing out

**Solutions:**
1. Increase timeout: `DEEPSEEK_TIMEOUT=60`
2. Check VPS resources: `htop` (ensure RAM usage < 80%)
3. Restart Ollama: `systemctl restart ollama`

### JSON Parse Errors

**Symptoms:** "Invalid JSON response from LLM"

**Solution:** The LLM sometimes returns markdown-wrapped JSON. The parser handles this automatically, but if errors persist:
- Check LLM server logs: `journalctl -u llm_server -n 50`
- Verify prompt template in `semantic_llm_server.py`

## Performance

**Expected Metrics:**
- Inference time: 5-15 seconds per image
- Memory usage: 4-6GB during inference
- Concurrent requests: 1-2 (limited by model size)

**Optimization Tips:**
- Run on VPS with GPU for 3-5x speedup
- Use smaller model (deepseek-r1:1.5b) for faster inference
- Cache results for identical descriptions

## Security

🔒 **Important Security Notes:**

1. **Firewall:** Only expose port 8000 to your development machine's IP
2. **No External Access:** Never expose Ollama port 11434 externally
3. **VPN Recommended:** Use VPN for production deployments
4 **Sanitization:** Prompts are automatically sanitized (see `PromptSanitizer`)

## Next Steps

1. ✅ Deploy to VPS using the installation script
2. ✅ Test connectivity with `--connectivity` flag
3. ⚙️ Run full image analysis pipeline
4. 📊 Monitor performance and adjust timeouts
5. 🚀 Integrate into production workflow

## Support

For issues or questions:
- Check logs: `journalctl -u llm_server -f`
- Review deployment guide: `scripts/vps_setup/deploy_vps.md`
- Test components individually using the test suite
