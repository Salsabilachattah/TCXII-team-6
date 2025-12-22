# app/utils/llm.py
from mistralai import Mistral
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the app directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Initialize Mistral client with API key from environment
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in environment variables")

client = Mistral(api_key=api_key)

def call_llm(system_prompt: str, user_prompt: str, temperature=0.3):
    """
    Calls Mistral model and returns the output text.
    """
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling Mistral API: {e}")
        raise
