import requests
import json
from app.core.config import COHERE_KEY
from app.prompts.nexus_prompts import YARGIC_SYSTEM

def get_yargic_res(soru, analizci_veri, denetci_veri, puter_vizyon):
    """
    Tüm ajan verilerini sentezleyip final JSON kararını basan Yargıç fonksiyonu.
    Hata durumlarında bile frontend'i patlatmamak için geçerli bir JSON string döner.
    """
    url = "https://api.cohere.com/v1/chat"
    headers = {
        "Authorization": f"Bearer {COHERE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Promptu "sıfır hata" moduna aldık. 
    # Markdown bloklarını (```json) yasakladık ki parse hatası almayalım.
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
    
    # Beklenmedik durumlarda dönecek güvenli hata objesi
    fallback_error = {
        "karar": "HATA",
        "risk_skoru": "-",
        "gerekce": "API Yanıt Vermedi veya Hatalı Döndü",
        "racon": "Yargıç şu an mühür basamıyor, teknik bir kopukluk var."
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        r.raise_for_status()
        res_json = r.json()
        
        # Cohere 'text' alanında yanıtı döner. Eğer boşsa fallback_error döner.
        yargic_metni = res_json.get("text")
        
        if yargic_metni:
            return yargic_metni
        else:
            return json.dumps(fallback_error)
            
    except Exception as e:
        print(f"DEBUG: Yargıç Hatası -> {str(e)}")
        # Sistem tamamen çökerse dönecek kritik hata objesi
        critical_error = {
            "karar": "ÇÖKTÜ",
            "risk_skoru": "%100",
            "gerekce": f"Bağlantı hatası: {str(e)}",
            "racon": "Masada sessizlik hakim, sistem mühür basamıyor."
        }
        return json.dumps(critical_error)
