import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API credentials - try to use environment variable if available
OPENROUTER_API_KEY = "sk-or-v1-8fc3f5774abc44bd8c85e65acf0584d3"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def test_api():
    print("Testing OpenRouter API connection...")
    print(f"Using API key: {OPENROUTER_API_KEY[:10]}...{OPENROUTER_API_KEY[-5:]}")
    
    # Simple test prompt
    prompt = "Say hello in Spanish"
    
    # OpenRouter required headers
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://skillshub.app",
        "X-Title": "Skills Hub Course Generator Test"
    }
    
    # Test multiple models
    models_to_test = [
        "openai/gpt-3.5-turbo",
        "anthropic/claude-instant-v1",
        "mistralai/mistral-7b-instruct"
    ]
    
    for model in models_to_test:
        print(f"\n--- Testing model: {model} ---")
        
        data = {
            "model": model,
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        try:
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Model {model} connection successful!")
                result = response.json()
                if "choices" in result and result["choices"] and "message" in result["choices"][0]:
                    content = result["choices"][0]["message"]["content"]
                    print(f"Response content: {content}")
                else:
                    print(f"Unexpected response structure: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Model {model} error. Status: {response.status_code}")
                print(f"Response: {response.text}")
        
        except Exception as e:
            print(f"Error testing model {model}: {str(e)}")
    
    print("\nTesting complete!")

if __name__ == "__main__":
    test_api() 