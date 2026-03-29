import requests
import json
from app.core.config import COHERE_KEY
from app.prompts.nexus_prompts import YARGIC_SYSTEM

def get_yargic_res(soru, core_final, ghost_bulgulari, void_elestirisi):
    url = "https://api.cohere.com/v1/chat"
    headers = {
        "Authorization": f"Bearer {COHERE_KEY}",
        "Content-Type": "application/json"
    }
    
    # GHOST'un açıklarını ve CORE'un son halini PRIME'ın önüne koyuyoruz.
    dosya = (
        f"SORU: '{soru}'\n\n"
        f"CORE (RAFİNE EDİLMİŞ TASLAK): '{core_final}'\n\n"
        f"GHOST (KÖR NOKTA ANALİZİ): '{ghost_bulgulari}'\n\n"
        f"VOID (ELEŞTİREL SÜZGEÇ): '{void_elestirisi}'\n\n"
        "TALİMAT: Sadece ham JSON dön. 'vizyon_onerisi' kısmında kullanıcıyı şaşırtacak stratejik bir soru veya öneri ekle."
    )

    data = {
        "model": "command-r-plus-08-2024",
        "message": dosya,
        "preamble": YARGIC_SYSTEM,
        "temperature": 0.2, # Biraz daha yaratıcı öneriler için tık yükselttik
        "response_format": {"type": "json_object"} 
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        r.raise_for_status()
        return r.json().get("text")
    except Exception as e:
        print(f"PRIME Hatası: {str(e)}")
        return json.dumps({
            "karar": "HATA", "risk_skoru": 100, "gerekce": "Sentez başarısız.",
            "racon": "Mühür çatladı, sistem uykuda.", "vizyon_onerisi": "Tekrar deneyelim mi?"
        })
