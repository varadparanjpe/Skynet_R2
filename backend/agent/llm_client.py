import requests
import json

class OllamaClient:
    """
    Dedicated client to talk to local Llama3 instance for the Reasoning Engine.
    """
    def __init__(self, model="llama3", url="http://localhost:11434/api/generate"):
        self.model = model
        self.url = url

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "{}")
        except Exception as e:
            print(f"Ollama Request Failed: {e}")
            return "{}"

    def parse_json(self, response_text: str) -> dict:
        import re
        try:
            # 1. Try to slice out markdown JSON block
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            # 2. Try to find first { and last }
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(response_text[start:end+1])
                
            # 3. Fallback to raw load
            return json.loads(response_text)
        except Exception as e:
            print(f"Failed to parse LLM JSON: {e}")
            return {}
