from openai import OpenAI
from .config import get_config

class LLM:
    def __init__(self):
        config = get_config()
        if not config:
            raise ValueError("API configuration not found.")
        
        self.client = OpenAI(
            api_key=config.get("api_key"),
            base_url=config.get("base_url"),
        )
        self.model = config.get("model", "gpt-4o")

    def get_answer(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None