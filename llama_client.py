import os
import requests
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv


class LlamaClient:
    """Simple client for interacting with Llama API"""

    def __init__(
        self, api_key: Optional[str] = None, base_url: str = "https://api.llama.com/v1"
    ):
        self.base_url = base_url.rstrip("/")

        if api_key is None:
            # Load environment variables from .env file
            load_dotenv()
            api_key = os.getenv("LLAMA_API_KEY")

            if not api_key:
                raise ValueError(
                    "LLAMA_API_KEY not found in environment variables or .env file"
                )

        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "Llama-3.3-8B-Instruct",
        max_tokens: int = 256,
        stream: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"

        payload = {
            "messages": messages,
            "model": model,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling Llama API: {str(e)}")

    def send_message(
        self,
        message: str,
        model: str = "Llama-3.3-8B-Instruct",
        max_tokens: int = 256,
    ) -> Dict[str, Any]:
        messages = [{"role": "user", "content": message}]
        return self.chat_completion(messages, model, max_tokens)


def create_client(api_key: Optional[str] = None) -> LlamaClient:
    return LlamaClient(api_key=api_key)


# Example usage
if __name__ == "__main__":
    client = create_client()

    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides concise answers.",
            },
            {"role": "user", "content": "What is the capital of France?"},
        ]

        response = client.chat_completion(messages)
        print(f"Conversation response: {json.dumps(response, indent=2)}")

    except Exception as e:
        print(f"Error: {e}")
