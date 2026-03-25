# app/agents/sme_agents.py (Hugging Face terk edildi, SME artık Groq'ta)
import groq
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import SME_SYSTEM

def get_sme_res(soru):
    # SME için hızlı ve bedava olan Gemma modelini seçiyoruz
    client = groq.Client(api_key=GROQ_KEY)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Groq üzerindeki hızlı ve iyi bir bedava model
            messages=[
                {"role": "system", "content": SME_SYSTEM},
                {"role": "user", "content": soru}
            ],
            max_tokens=150 # SME teknik veri verir, çok uzatmasına gerek yok
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Eğer Groq bile patlarsa (ki çok zor), hata detayını loglara ve frontend'e verelim
        hata_mesaji = f"SME (Groq) API Hatası: {type(e).__name__} - {str(e)}"
        print(f"KRİTİK HATA [SME]: {hata_mesaji}") 
        return hata_mesaji
