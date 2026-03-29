from groq import Groq
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import CORE_SYSTEM, GHOST_SYSTEM, VOID_SYSTEM

client = Groq(api_key=GROQ_KEY)

def get_core_res(soru, context=""):
    # CORE (Mimar): Teknik iskeleti ve ana mantığı kurar.
    prompt = f"Girdi: {soru}\nEk Bilgi/Revize Talebi: {context}"
    
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": CORE_SYSTEM}, 
            {"role": "user", "content": prompt}
        ],
        max_tokens=300, # İskeletin derinliği için optimize edildi
        temperature=0.3
    )
    return res.choices[0].message.content

def get_ghost_res(core_cevap):
    # GHOST (Sızıcı): Taslaktaki siber açıkları ve mantık hatalarını bulur.
    prompt = f"CORE Taslağı:\n{core_cevap}"
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": GHOST_SYSTEM}, 
            {"role": "user", "content": prompt}
        ],
        max_tokens=150, # Hızlı ve vurucu analiz için kısıtlandı
        temperature=0.4
    )
    return res.choices[0].message.content

def get_void_res(core_cevap, ghost_cevap):
    # VOID (Protokol): GHOST verilerini direktiflere dönüştürür.
    prompt = f"CORE Taslağı: {core_cevap}\nGHOST Bulguları: {ghost_cevap}"
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": VOID_SYSTEM}, 
            {"role": "user", "content": prompt}
        ],
        max_tokens=150, # Net komut seti için sınırlandırıldı
        temperature=0.3
    )
    return res.choices[0].message.content
