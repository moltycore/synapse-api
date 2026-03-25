from groq import Groq
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import ARASTIRMACI_SYSTEM, DENETCI_SYSTEM

client = Groq(api_key=GROQ_KEY)

def get_arastirmaci_res(soru, sme_veri):
    prompt = f"Konu: {soru}\nSME Verisi: {sme_veri}"
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[
            {"role": "system", "content": ARASTIRMACI_SYSTEM}, 
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content

def get_denetci_res(arastirma_cevap):
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant", 
        messages=[
            {"role": "system", "content": DENETCI_SYSTEM}, 
            {"role": "user", "content": arastirma_cevap}
        ]
    )
    return res.choices[0].message.content
