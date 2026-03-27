import requests
from app.core.config import PUTER_APP_ID
from app.prompts.nexus_prompts import PUTER_SYSTEM

def call_puter(soru, analizci_veri, denetci_veri):
    url = "https://api.puter.com/ai/chat" 
    headers = {
        "Authorization": f"Bearer {PUTER_APP_ID}",
        "Content-Type": "application/json"
    }
    
    # Sadece soruyu, analizi ve riskleri verip vizyon istiyoruz
    prompt = f"SORU: {soru}\nANALİZ: {analizci_veri}\nRİSKLER: {denetci_veri}"
    
    data = {
        "messages": [
            {"role": "system", "content": PUTER_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        "model": "gpt-4o-mini"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "Vizyoner ufku göremedi.")
    except Exception as e:
        print(f"Puter Hatası: {str(e)}")
        return "Vizyoner hatta düştü."
