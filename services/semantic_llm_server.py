#!/usr/bin/env python3
"""
Semantic LLM Server - DeepSeek-R1 Microservice
UIDE Forense AI 3.0+

Persistent microservice for semantic reasoning inference using DeepSeek-R1:7b.

Features:
- Async request queue with prioritization
- Timeout management (30s default)
- Exponential backoff retry logic
- Prompt sanitization and validation
- Health check endpoint
- Structured JSON responses
"""

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

import aiohttp
from aiohttp import web
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:7b")
SERVER_PORT = int(os.getenv("LLM_SERVER_PORT", "8000"))
REQUEST_TIMEOUT = int(os.getenv("LLM_REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SemanticScores:
    """Structured semantic scores from DeepSeek-R1."""
    semantic_improbability_score: float
    context_collision_score: float
    composition_synthetic_score: float
    reasoning: Optional[str] = None


class PromptSanitizer:
    """Sanitizes and validates prompts before sending to LLM."""
    
    MAX_DESCRIPTION_LENGTH = 1000
    FORBIDDEN_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"system\s+prompt",
        r"<\s*script",
        r"exec\s*\(",
    ]
    
    @classmethod
    def sanitize(cls, description: str) -> str:
        """Sanitize user input."""
        # Trim whitespace
        description = description.strip()
        
        # Limit length
        if len(description) > cls.MAX_DESCRIPTION_LENGTH:
            description = description[:cls.MAX_DESCRIPTION_LENGTH]
            logger.warning(f"Description truncated to {cls.MAX_DESCRIPTION_LENGTH} chars")
        
        # Check for forbidden patterns
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, description, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected: {pattern}")
                description = re.sub(pattern, "[REDACTED]", description, flags=re.IGNORECASE)
        
        return description


class DeepSeekInferenceEngine:
    """Manages inference requests to DeepSeek-R1 model."""
    
    # Structured prompt template
    PROMPT_TEMPLATE = """Eres un experto en análisis forense de imágenes. Evalúa la plausibilidad semántica, coherencia contextual y características sintéticas de la escena descrita.

Devuelve únicamente un JSON válido con tres campos numéricos entre 0 y 1, sin ningún texto adicional:

{{
  "semantic_improbability_score": <valor entre 0 y 1>,
  "context_collision_score": <valor entre 0 y 1>,
  "composition_synthetic_score": <valor entre 0 y 1>
}}

Descripción CLIP de la imagen:
{description}

Razonamiento técnico paso a paso:
1. Analiza si la escena es plausible en el mundo real
2. Detecta contradicciones o elementos incompatibles
3. Evalúa si la composición es típica de IA generativa

Responde SOLO con el JSON, sin texto antes ni después."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize HTTP session."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info("✅ Inference engine initialized")
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("🔒 Inference engine closed")
    
    def _build_prompt(self, description: str) -> str:
        """Build structured prompt for DeepSeek-R1."""
        sanitized = PromptSanitizer.sanitize(description)
        return self.PROMPT_TEMPLATE.format(description=sanitized)
    
    def _parse_response(self, response_text: str) -> SemanticScores:
        """Parse JSON response from LLM."""
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```json\s*', '', response_text)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        
        # Extract JSON if embedded in text
        json_match = re.search(r'\{[^}]*"semantic_improbability_score"[^}]*\}', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(0)
        
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nResponse: {response_text[:200]}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
        
        # Validate fields
        required_fields = [
            "semantic_improbability_score",
            "context_collision_score",
            "composition_synthetic_score"
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            
            value = data[field]
            if not isinstance(value, (int, float)):
                raise ValueError(f"Field {field} must be numeric, got {type(value)}")
            
            if not 0 <= value <= 1:
                logger.warning(f"Field {field}={value} out of range [0,1], clipping")
                data[field] = max(0.0, min(1.0, value))
        
        return SemanticScores(
            semantic_improbability_score=float(data["semantic_improbability_score"]),
            context_collision_score=float(data["context_collision_score"]),
            composition_synthetic_score=float(data["composition_synthetic_score"]),
            reasoning=response_text  # Store full reasoning
        )
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True
    )
    async def infer(self, description: str) -> SemanticScores:
        """
        Run inference on DeepSeek-R1 model.
        
        Args:
            description: CLIP description of the image
            
        Returns:
            SemanticScores with three scores (0-1)
            
        Raises:
            ValueError: Invalid response format
            aiohttp.ClientError: API communication error
        """
        if not self.session:
            await self.initialize()
        
        prompt = self._build_prompt(description)
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for consistent JSON
                "top_p": 0.9,
                "num_predict": 256  # Limit response length
            }
        }
        
        logger.info(f"🔍 Sending inference request (desc length: {len(description)} chars)")
        
        try:
            async with self.session.post(OLLAMA_API_URL, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                
                if "response" not in result:
                    raise ValueError("No 'response' field in Ollama API result")
                
                llm_response = result["response"]
                logger.debug(f"LLM response: {llm_response[:200]}")
                
                scores = self._parse_response(llm_response)
                logger.info(f"✅ Inference successful: improbability={scores.semantic_improbability_score:.2f}")
                
                return scores
                
        except aiohttp.ClientError as e:
            logger.error(f"❌ Ollama API error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Inference error: {e}", exc_info=True)
            raise


# Global inference engine
inference_engine = DeepSeekInferenceEngine()


# ============================================================
# HTTP Handlers
# ============================================================

async def health_handler(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return web.json_response({
        "status": "healthy",
        "model": OLLAMA_MODEL,
        "timestamp": datetime.utcnow().isoformat()
    })


async def infer_handler(request: web.Request) -> web.Response:
    """Inference endpoint."""
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response(
            {"error": "Invalid JSON payload"},
            status=400
        )
    
    # Validate request
    if "description" not in data:
        return web.json_response(
            {"error": "Missing 'description' field"},
            status=400
        )
    
    description = data["description"]
    
    if not isinstance(description, str) or not description.strip():
        return web.json_response(
            {"error": "'description' must be a non-empty string"},
            status=400
        )
    
    # Run inference
    try:
        scores = await inference_engine.infer(description)
        
        response_data = asdict(scores)
        return web.json_response(response_data)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return web.json_response(
            {"error": f"Validation error: {str(e)}"},
            status=422
        )
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"Service error: {e}")
        return web.json_response(
            {"error": f"LLM service unavailable: {str(e)}"},
            status=503
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return web.json_response(
            {"error": f"Internal server error: {str(e)}"},
            status=500
        )


async def on_startup(app: web.Application):
    """Initialize resources on startup."""
    logger.info("🚀 Starting Semantic LLM Server...")
    await inference_engine.initialize()


async def on_cleanup(app: web.Application):
    """Cleanup resources on shutdown."""
    logger.info("🔒 Shutting down Semantic LLM Server...")
    await inference_engine.close()


def create_app() -> web.Application:
    """Create and configure the web application."""
    app = web.Application()
    
    # Routes
    app.router.add_get('/health', health_handler)
    app.router.add_post('/infer', infer_handler)
    
    # Lifecycle
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    
    return app


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Semantic LLM Server - DeepSeek-R1")
    logger.info("UIDE Forense AI 3.0+")
    logger.info("=" * 60)
    logger.info(f"Model: {OLLAMA_MODEL}")
    logger.info(f"API: {OLLAMA_API_URL}")
    logger.info(f"Port: {SERVER_PORT}")
    logger.info(f"Timeout: {REQUEST_TIMEOUT}s")
    logger.info("=" * 60)
    
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=SERVER_PORT)


if __name__ == '__main__':
    main()
