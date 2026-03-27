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
    
    # Tüm veriyi masaya koyuyoruz
    dosya = f"SORU: '{soru}'\n\nANALİZ: '{analizci_veri}'\n\nDENETÇİ: '{denetci_veri}'\n\nVİZYONER: '{puter_vizyon}'\n\nTüm bu verileri sentezle ve KESİNLİKLE sadece istenen JSON formatında yanıt ver."

    data = {
        "model": "command-r-plus-08-2024",
        "message": dosya,
        "preamble": YARGIC_SYSTEM,
        "temperature": 0.1,
        "response_format": {"type": "json_object"} # Kesinlikle JSON dönmesini garanti eder
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        r.raise_for_status()
        return r.json().get("text", '{"karar": "HATA", "risk_skoru": "Bilinmiyor", "racon": "Yargıç mühür basamadı."}')
    except Exception as e:
        print(f"Yargıç Hatası: {str(e)}")
        # Sistem çökerse sahte bir JSON dönüyoruz ki frontend hata vermesin
        return json.dumps({
            "karar": "ÇÖKTÜ",
            "risk_skoru": "%100",
            "racon": "Masaya sessizlik hakim, sistem bağlantıyı kaybetti."
        })
