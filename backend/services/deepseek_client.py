import requests

class DeepSeekClient:
    def __init__(self, url="http://localhost:11434/api/generate", model="deepseek-r1:7b"):
        self.url = url
        self.model = model

    def ask(self, prompt: str):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            print(f"DEBUG: Connecting to Ollama at {self.url} with model {self.model}")
            response = requests.post(self.url, json=payload)
            print(f"DEBUG: Ollama status code: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "response": data.get("response", "")
            }

        except Exception as e:
            print(f"DEBUG: DeepSeekClient Error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
