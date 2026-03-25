# app/agents/moderator_agents.py
import requests
from openai import OpenAI
from app.core.config import OPENROUTER_KEY, PUTER_APP_ID
from app.prompts.nexus_prompts import MODERATOR_SYSTEM

def call_openrouter(soru, sme, arastirma, denetci):
    # Ana Motor: OpenRouter (openrouter/free joker rotası)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_KEY,
    )
    
    prompt = f"SORU: {soru}\nSME: {sme}\nARAŞTIRMACI: {arastirma}\nDENETÇİ: {denetci}"
    
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {"role": "system", "content": MODERATOR_SYSTEM},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def call_puter(soru, sme, arastirma, denetci):
    # Yedek Lastik: Puter API
    url = "https://api.puter.com/ai/chat" 
    headers = {
        "Authorization": f"Bearer {PUTER_APP_ID}",
        "Content-Type": "application/json"
    }
    prompt = f"SORU: {soru}\nSME: {sme}\nARAŞTIRMACI: {arastirma}\nDENETÇİ: {denetci}"
    
    data = {
        "messages": [
            {"role": "system", "content": MODERATOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        "model": "gpt-4o-mini" # Puter'ın varsayılan bedava modellerinden biri
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    # Puter'ın dönüş formatından içeriği çek
    return response.json().get("message", {}).get("content", "Puter yanıt veremedi.")

def get_moderator_res(soru, sme, arastirma, denetci):
    # Hibrit Geçiş (Fallback) Mantığı
    try:
        # Önce OpenRouter'ın kapısını kır
        return call_openrouter(soru, sme, arastirma, denetci)
    except Exception as e:
        print(f"OpenRouter Tıkandı/Limit Doldu: {e}. Puter yedek motoru ateşleniyor...")
        
        try:
            # OpenRouter patlarsa sessizce Puter'ı devreye sok
            return call_puter(soru, sme, arastirma, denetci)
        except Exception as puter_e:
            # İkisi de patlarsa yapacak bir şey yok, dükkanı kapatıyoruz
            return f"Moderatör hata verdi: İki sistem de çöktü. OpenRouter: {e} | Puter: {puter_e}"
