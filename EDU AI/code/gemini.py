import os
from dotenv import load_dotenv
import joblib

# Define base URL for Gemini API
# Replace with your actual API key
load_dotenv()
api_key = os.getenv("API_KEY")
#database_url = os.getenv("DATABASE_URL")

base_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + api_key

# Function to make requests to Gemini API
def make_gemini_request(prompt, method='POST'):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    url = base_url

    try:
        import requests
        response = requests.request(method, url, json=data, headers=headers)
        candidates = response.json().get('candidates', [])
        for candidate in candidates:
            content = candidate.get('content', {})
            parts = content.get('parts', [])
    
    # Iterate over each part to find the 'text' content
        for part in parts:
            text = part.get('text', '')
            if text:
                return text
    except requests.exceptions.RequestException as e:
        print(f"Error making Gemini API request: {e}")
        return None


# Iterate over each candidat

