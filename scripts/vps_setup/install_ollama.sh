#!/bin/bash

###############################################################################
# Ollama + DeepSeek-R1:7b Installation Script
# UIDE Forense AI 3.0+ - VPS Setup
# 
# Target: Ubuntu 22.04, 24GB RAM, 200GB NVMe
# Purpose: Install Ollama and DeepSeek-R1:7b model for local LLM inference
###############################################################################

set -e  # Exit on error

echo "=========================================="
echo "🚀 UIDE Forense AI - Ollama Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# System requirements check
echo "📊 Checking system requirements..."
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM" -lt 20 ]; then
    echo "⚠️  Warning: System has ${TOTAL_RAM}GB RAM. Recommended: 24GB+"
fi

AVAILABLE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -lt 50 ]; then
    echo "⚠️  Warning: Only ${AVAILABLE_SPACE}GB available. Model requires ~10GB."
fi

echo "✅ RAM: ${TOTAL_RAM}GB, Disk: ${AVAILABLE_SPACE}GB available"
echo ""

# Update system
echo "📦 Updating system packages..."
apt-get update -qq
apt-get install -y curl wget git

# Install Ollama
echo ""
echo "🔧 Installing Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama already installed ($(ollama --version))"
else
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installed successfully"
fi

# Start Ollama service
echo ""
echo "🔄 Starting Ollama service..."
systemctl enable ollama
systemctl start ollama
sleep 3

# Verify Ollama is running
if systemctl is-active --quiet ollama; then
    echo "✅ Ollama service is running"
else
    echo "❌ Failed to start Ollama service"
    exit 1
fi

# Download DeepSeek-R1:7b model
echo ""
echo "📥 Downloading DeepSeek-R1:7b model..."
echo "⚠️  This may take 10-15 minutes (model size: ~4.7GB)"
echo ""

ollama pull deepseek-r1:7b

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ DeepSeek-R1:7b model downloaded successfully"
else
    echo "❌ Failed to download model"
    exit 1
fi

# Test the model
echo ""
echo "🧪 Testing DeepSeek-R1:7b model..."
TEST_RESPONSE=$(ollama run deepseek-r1:7b "Say 'OK' if you are ready" --verbose=false 2>&1 | head -n 1)

if [[ "$TEST_RESPONSE" == *"OK"* ]] || [[ "$TEST_RESPONSE" == *"ok"* ]]; then
    echo "✅ Model test successful: $TEST_RESPONSE"
else
    echo "⚠️  Model loaded but response unclear: $TEST_RESPONSE"
fi

# Configure Ollama to listen on localhost only (security)
echo ""
echo "🔒 Configuring Ollama security settings..."

# Create Ollama environment file
cat > /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_ORIGINS=http://localhost:*,http://127.0.0.1:*"
EOF

# Reload systemd and restart Ollama
systemctl daemon-reload
systemctl restart ollama
sleep 2

# Verify API endpoint
echo ""
echo "🔍 Verifying API endpoint..."
API_RESPONSE=$(curl -s http://localhost:11434/api/tags 2>&1)

if [[ "$API_RESPONSE" == *"deepseek-r1"* ]]; then
    echo "✅ API endpoint responding correctly"
else
    echo "⚠️  API endpoint check inconclusive"
fi

# Display system status
echo ""
echo "=========================================="
echo "✅ INSTALLATION COMPLETE"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "  • Ollama service: $(systemctl is-active ollama)"
echo "  • API endpoint: http://localhost:11434"
echo "  • Model: DeepSeek-R1:7b"
echo "  • Service starts on boot: enabled"
echo ""
echo "🔧 Useful commands:"
echo "  • Check service status: systemctl status ollama"
echo "  • View logs: journalctl -u ollama -f"
echo "  • Test model: ollama run deepseek-r1:7b"
echo "  • List models: ollama list"
echo ""
echo "🚀 Next step: Deploy semantic_llm_server.py microservice"
echo ""
