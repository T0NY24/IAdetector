"""
LLM Client - Communication layer for DeepSeek-R1 microservice
UIDE Forense AI 3.0+

Client library for communicating with semantic_llm_server.py.
Handles retry logic, timeout management, and response validation.
"""

import logging
import requests
from typing import Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class SemanticLLMClient:
    """Client for DeepSeek-R1 semantic reasoning microservice."""
    
    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize LLM client.
        
        Args:
            api_url: Base URL of the LLM microservice
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        logger.info(f"🔗 LLM Client initialized: {self.api_url}")
    
    def check_health(self) -> bool:
        """
        Check if the LLM service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.api_url}/health",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            is_healthy = data.get("status") == "healthy"
            if is_healthy:
                logger.info(f"✅ LLM service healthy: {data.get('model')}")
            else:
                logger.warning(f"⚠️  LLM service unhealthy: {data}")
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),  # Will use instance max_retries in practice
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout)),
        reraise=True
    )
    def infer_semantic_scores(
        self,
        description: str,
        clip_features: Optional[list] = None
    ) -> Dict[str, float]:
        """
        Request semantic scores from DeepSeek-R1.
        
        Args:
            description: CLIP text description of the image
            clip_features: Optional CLIP features (not currently used by LLM)
            
        Returns:
            Dict with three scores:
                - semantic_improbability_score (0-1)
                - context_collision_score (0-1)
                - composition_synthetic_score (0-1)
                
        Raises:
            requests.RequestException: Network or API error
            ValueError: Invalid response format
        """
        if not description or not isinstance(description, str):
            raise ValueError("Description must be a non-empty string")
        
        payload = {
            "description": description,
            "clip_features": clip_features or []
        }
        
        logger.info(f"🔍 Requesting semantic scores (desc: {len(description)} chars)")
        
        try:
            response = self.session.post(
                f"{self.api_url}/infer",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response
            required_fields = [
                "semantic_improbability_score",
                "context_collision_score",
                "composition_synthetic_score"
            ]
            
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing field in response: {field}")
                
                value = data[field]
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Field {field} must be numeric")
                
                if not 0 <= value <= 1:
                    raise ValueError(f"Field {field}={value} out of range [0,1]")
            
            logger.info(
                f"✅ Semantic scores: "
                f"improbability={data['semantic_improbability_score']:.2f}, "
                f"collision={data['context_collision_score']:.2f}, "
                f"composition={data['composition_synthetic_score']:.2f}"
            )
            
            return {
                "semantic_improbability_score": float(data["semantic_improbability_score"]),
                "context_collision_score": float(data["context_collision_score"]),
                "composition_synthetic_score": float(data["composition_synthetic_score"]),
                "reasoning": data.get("reasoning", "")
            }
            
        except requests.Timeout as e:
            logger.error(f"❌ Request timeout after {self.timeout}s")
            raise
        except requests.RequestException as e:
            logger.error(f"❌ Request failed: {e}")
            raise
        except ValueError as e:
            logger.error(f"❌ Invalid response: {e}")
            raise
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
        logger.info("🔒 LLM client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
