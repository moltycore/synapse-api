import requests
import json
from app.core.config import COHERE_KEY
from app.prompts.nexus_prompts import YARGIC_SYSTEM

def get_yargic_res(soru, analizci_veri, denetci_veri, puter_vizyon):
    url = "https://api.cohere.com/v1/chat"
    headers = {
        "Authorization": f"Bearer {COHERE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Promptu "sıfır hata" moduna aldım. Markdown bloklarını (```json) yasakladım.
    dosya = (
        f"SORU: '{soru}'\n\n"
        f"ANALİZ: '{analizci_veri}'\n\n"
        f"DENETÇİ: '{denetci_veri}'\n\n"
        f"VİZYONER: '{puter_vizyon}'\n\n"
        "TALİMAT: Sadece ham JSON dön. Markdown etiketleri (```json) kullanma. "
        "Yanıtın doğrudan '{' ile başlamalı ve '}' ile bitmeli."
    )

    data = {
        "model": "command-r-plus-08-2024",
        "message": dosya,
        "preamble": YARGIC_SYSTEM,
        "temperature": 0.1,
        "response_format": {"type": "json_object"} 
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        r.raise_for_status()
        res_json = r.json()
        
        # Cohere bazen 'text' içinde temiz JSON gönderir
        return res_json.get("text", '{"karar": "HATA", "risk_skoru": "-", "racon": "Veri çekilemedi."}')
        
    except Exception as e:
        print(f"DEBUG: Yargıç Hatası -> {str(e)}")
        return json.dumps({
            "karar": "ÇÖKTÜ",
            "risk_skoru": "%100",
            "gerekce": "Bağlantı koptu.",
            "racon": "Masada sessizlik hakim, sistem mühür basamıyor."
        })
