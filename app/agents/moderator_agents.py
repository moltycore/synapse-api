import requests
from openai import OpenAI
from app.core.config import OPENROUTER_KEY, PUTER_APP_ID
from app.prompts.nexus_prompts import MODERATOR_SYSTEM

def call_openrouter(soru, sme, arastirma, denetci, puter_vizyon):
    # Ana Motor: OpenRouter (openrouter/free joker rotası)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_KEY,
    )
    
    # Prompt içerisine VİZYONER (Puter) verisi eklendi
    prompt = f"SORU: {soru}\nSME: {sme}\nARAŞTIRMACI: {arastirma}\nDENETÇİ: {denetci}\nVİZYONER: {puter_vizyon}"
    
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {"role": "system", "content": MODERATOR_SYSTEM},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def call_puter(soru, sme, arastirma, denetci, puter_vizyon):
    # Yedek Lastik: Puter API
    url = "https://api.puter.com/ai/chat" 
    headers = {
        "Authorization": f"Bearer {PUTER_APP_ID}",
        "Content-Type": "application/json"
    }
    # Prompt içerisine VİZYONER (Puter) verisi eklendi
    prompt = f"SORU: {soru}\nSME: {sme}\nARAŞTIRMACI: {arastirma}\nDENETÇİ: {denetci}\nVİZYONER: {puter_vizyon}"
    
    data = {
        "messages": [
            {"role": "system", "content": MODERATOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        "model": "gpt-4o-mini"
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json().get("message", {}).get("content", "Puter yanıt veremedi.")

def get_moderator_res(soru, sme, arastirma, denetci, puter_vizyon):
    # Hibrit Geçiş (Fallback) Mantığı - Artık puter_vizyon parametresini de taşıyor
    try:
        # Önce OpenRouter
        return call_openrouter(soru, sme, arastirma, denetci, puter_vizyon)
    except Exception as e:
        print(f"OpenRouter Tıkandı: {e}. Puter yedek motoru ateşleniyor...")
        
        try:
            # OpenRouter patlarsa sessizce Puter'ı devreye sok
            return call_puter(soru, sme, arastirma, denetci, puter_vizyon)
        except Exception as puter_e:
            return f"Moderatör hata verdi: İki sistem de çöktü. OpenRouter: {e} | Puter: {puter_e}"
