from groq import Groq
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import CORE_SYSTEM, GHOST_SYSTEM, VOID_SYSTEM

client = Groq(api_key=GROQ_KEY)

def get_core_res(soru, context=""):
    # Context, VOID'den gelen revize talebi olabilir
    prompt = f"Girdi: {soru}\nEk Bilgi/Revize Talebi: {context}"
    
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": CORE_SYSTEM}, 
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content

def get_ghost_res(core_cevap):
    # CORE'un açığını bulur
    prompt = f"CORE Taslağı:\n{core_cevap}"
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": GHOST_SYSTEM}, 
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content

def get_void_res(core_cevap, ghost_cevap):
    # GHOST'un bulduklarıyla CORE'u eleştirir
    prompt = f"CORE Taslağı: {core_cevap}\nGHOST Bulguları: {ghost_cevap}"
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": VOID_SYSTEM}, 
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content
