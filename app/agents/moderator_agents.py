import requests
from app.core.config import PUTER_APP_ID
from app.prompts.nexus_prompts import GATEKEEPER_SYSTEM

def get_gatekeeper_res(user_input):
    url = "https://api.puter.com/ai/chat" 
    headers = {
        "Authorization": f"Bearer {PUTER_APP_ID}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [
            {"role": "system", "content": GATEKEEPER_SYSTEM},
            {"role": "user", "content": user_input}
        ],
        "model": "gpt-4o-mini" # Hızlı ve niyet okumada keskin
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=5)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "ANALIZ").strip().upper()
    except Exception as e:
        print(f"Gatekeeper Hatası: {str(e)}")
        return "ANALIZ" # Hata durumunda güvenli liman (Analiz)
