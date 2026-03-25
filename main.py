from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from groq import Groq
from openai import OpenAI

# Synapse API - Nexus V1
app = FastAPI(title="Synapse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render Environment Variables
GROQ_KEY = os.getenv("GROQ_API_KEY")
COHERE_KEY = os.getenv("COHERE_API_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
HF_KEY = os.getenv("HF_API_KEY")

# ─────────────────────────────────────────────
# AJAN PROMPT'LARI
# ─────────────────────────────────────────────

SME_SYSTEM = "Sen teknik veri kaynağısın. Konuyu ham, donuk ve teknik verilerle özetle. Max 40 kelime."

ARASTIRMACI_SYSTEM = """
Sen duygusuz bir SAHA ARAŞTIRMACISI'sın. SME verilerini deşip sarsıcı gerçekleri bul.
KURALLAR: 3 madde, madde başı max 20 kelime.
"""

DENETCI_SYSTEM = """
Sen acımasız bir 'Siyah Kuğu' avcısısın. Araştırmacı'nın verilerindeki kırılganlığı bul.
KURALLAR: Max 15 kelimelik 3 risk.
"""

MODERATOR_SYSTEM = """
Sen Nexus Konseyi Başkanı ve Karar Merciisin. Masadaki kavgayı analiz edip son hükmü ver.
KURALLAR: Nezaket yok, selamlama yok. Doğrudan buyurgan karar. Max 50 kelime.
"""

BASDANISMAN_PREAMBLE = """
Sen sokağın nabzını tutan elit bir sentezleyicisin. Moderatör hükmünü kendi fikrin gibi sahiplen.
KURALLAR: Tek paragraf, max 4 cümle, devrik cümleler, sokağın jargonuyla elit zeka sentezi.
"""

class Soru(BaseModel):
    text: str

# ─────────────────────────────────────────────
# AJAN FONKSİYONLARI
# ─────────────────────────────────────────────

def ajan_sme_hf(soru):
    url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {"Authorization": f"Bearer {HF_KEY}"}
    payload = {"inputs": f"Sistem: {SME_SYSTEM}\nSoru: {soru}", "parameters": {"max_new_tokens": 80}}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        return r.json()[0].get("generated_text", "Veri yok.")
    except: return "SME sessiz."

def ajan_arastirmaci(soru, sme, client):
    p = f"Konu: {soru}\nSME Verisi: {sme}"
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": ARASTIRMACI_SYSTEM}, {"role": "user", "content": p}])
    return res.choices[0].message.content

def ajan_denetci(arastirma, client):
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": DENETCI_SYSTEM}, {"role": "user", "content": arastirma}])
    return res.choices[0].message.content

def ajan_moderator_deepseek(soru, sme, arastirma, denetci, ds_client):
    p = f"Soru: {soru}\nVeriler: SME: {sme}, Araştırma: {arastirma}, Denetçi: {denetci}"
    res = ds_client.chat.completions.create(
        model="deepseek-chat", # OpenAI SDK ile DeepSeek V3 kullanımı
        messages=[{"role": "system", "content": MODERATOR_SYSTEM}, {"role": "user", "content": p}]
    )
    return res.choices[0].message.content

def ajan_basdanisman(moderator_hukmu):
    url = "https://api.cohere.com/v1/chat"
    headers = {"Authorization": f"Bearer {COHERE_KEY}"}
    data = {"model": "command-r-plus-08-2024", "message": moderator_hukmu, "preamble": BASDANISMAN_PREAMBLE}
    r = requests.post(url, headers=headers, json=data, timeout=15)
    return r.json().get("text", "Sentez başarısız.")

# ─────────────────────────────────────────────
# ANA MOTOR
# ─────────────────────────────────────────────

@app.post("/analyze")
async def analyze(soru: Soru):
    if not all([GROQ_KEY, COHERE_KEY, DEEPSEEK_KEY, HF_KEY]):
        raise HTTPException(status_code=500, detail="API Anahtarları eksik.")
    
    try:
        groq_client = Groq(api_key=GROQ_KEY)
        ds_client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com/v1") # DeepSeek Endpoint
        
        sme = ajan_sme_hf(soru.text)
        ara = ajan_arastirmaci(soru.text, sme, groq_client)
        den = ajan_denetci(ara, groq_client)
        mod = ajan_moderator_deepseek(soru.text, sme, ara, den, ds_client)
        final = ajan_basdanisman(mod)
        
        return {"final_karar": final, "sme": sme, "arastirma": ara, "denetleme": den, "moderator": mod}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
