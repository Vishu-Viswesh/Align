import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def list_groq():
    print("--- START GROQ MODELS ---")
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("No Groq Key")
        return
    
    headers = {"Authorization": f"Bearer {key}"}
    try:
        resp = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
        if resp.status_code == 200:
            models = resp.json()['data']
            for m in models:
                print(m['id'])
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    print("--- END GROQ MODELS ---")

if __name__ == "__main__":
    list_groq()
