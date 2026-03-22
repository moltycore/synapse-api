from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from groq import Groq

# Colab kum havuzuna veda, gerçek sunucuya merhaba.
app = FastAPI(title="Synapse API")

# Lovable arayüzü buraya istek atarken tarayıcı engeline takılmasın diye CORS ayarı:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Anahtarları artık Colab'dan değil, Render'ın güvenli kasasından (Environment Variables) gelecek.
GROQ_KEY = os.getenv("GROQ_API_KEY")
COHERE_KEY = os.getenv("COHERE_API_KEY")

# ─────────────────────────────────────────────
# AJAN PROMPT'LARI
# ─────────────────────────────────────────────

ARASTIRMACI_SYSTEM = """
Sen duygusuz, robotik ve sadece saf gerçeğe odaklı bir SAHA ARAŞTIRMACISI'sın.
Görevin, konuyu deşip masaya sadece en çıplak ve sarsıcı verileri bırakıp çekilmek.
KESİN KURALLAR: 3 madde, madde başı max 20 kelime, yorum yasak.
"""

ARASTIRMACI_REVIZE_SYSTEM = """
Sen bir SAHA ARAŞTIRMACISI'sın. Az önce sunduğun veriler Acımasız Denetçi tarafından paramparça edildi.
Egonu tamamen eziyorsun. Savunma yapmak, özür dilemek veya açıklama yapmak KESİNLİKLE YASAK.
Görevin: Denetçinin bulduğu riskleri ve açıkları kapatan, kurşungeçirmez YENİ bir veri seti (V2) sunmak.
KESİN KURALLAR: Sadece güncellenmiş 3 maddeyi ver. Her madde max 20 kelime olacak.
"""

DENETCI_SYSTEM = """
Sen Nassim Taleb zekasına sahip, aşırı şüpheci ve risk odaklı acımasız bir 'Siyah Kuğu' avcısısın.
Araştırma verilerinin altındaki gizli kırılganlığı ve felaket senaryosunu bulmak tek amacın.
KESİN KURALLAR: Max 15 kelimelik 3 risk. "Neden", "Açıklama" gibi başlıklar kullanma.
"""

VIZYONER_SYSTEM = """
Sen kuralları yıkan, 10x büyüme hedefleyen, sınırları zorlayan bir Silikon Vadisi dâhisisin.
Görevin: Denetçinin bulduğu riskten piyasayı domine edecek radikal bir B planı çıkarmak.
KESİN KURALLAR: Sadece 2 cümle ve max 30 kelime.
"""

BASDANISMAN_PREAMBLE = """
Sen elit bir zekaya sahip, sokağın nabzını tutan acımasız bir sentezleyicisin.
Sana sunulan verileri oku ama ASLA "Araştırmacı", "Denetçi", "Vizyoner", "uyarılar" veya "öngörüler" gibi atıflarda bulunma. Kimin ne dediği umrunda değil.
Verileri çal, sanki en başından beri kendi dahiyane fikrinmiş gibi sahiplen ve mutlak gerçek olarak kus.
Kati Kurallar: Tek paragraf, max 4 cümle, devrik cümle yapısı, sokağın jargonuyla elit zekayı harmanla.
"""

# ─────────────────────────────────────────────
# API VERİ YAPISI
# ─────────────────────────────────────────────
class Soru(BaseModel):
    text: str

# ─────────────────────────────────────────────
# AJAN FONKSİYONLARI
# ─────────────────────────────────────────────

def ajan_arastirmaci(soru, client):
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": ARASTIRMACI_SYSTEM}, {"role": "user", "content": soru}], max_tokens=150, temperature=0.1)
    return res.choices[0].message.content

def ajan_denetci(soru, arastirma_cevap, client):
    prompt = f"Konu: {soru}\n\nVeriler:\n{arastirma_cevap}"
    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": DENETCI_SYSTEM}, {"role": "user", "content": prompt}], max_tokens=100, temperature=0.1)
    return res.choices[0].message.content

def ajan_arastirmaci_revize(soru, eski_veri, elestiri, client):
    prompt = f"Konu: {soru}\n\nEski Verilerin:\n{eski_veri}\n\nAldığın Tokat (Eleştiri):\n{elestiri}\n\nŞimdi egonu ezip kurşungeçirmez yeni verilerini sun:"
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": ARASTIRMACI_REVIZE_SYSTEM}, {"role": "user", "content": prompt}], max_tokens=150, temperature=0.1)
    return res.choices[0].message.content

def ajan_vizyoner(soru, denetci_cevap, client):
    prompt = f"Konu: {soru}\n\nRiskler:\n{denetci_cevap}"
    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": VIZYONER_SYSTEM}, {"role": "user", "content": prompt}], max_tokens=100, temperature=0.1)
    return res.choices[0].message.content

def ajan_basdanisman(soru, arastirma, denetci, vizyoner):
    url = "https://api.cohere.com/v1/chat"
    headers = {"Authorization": f"Bearer {COHERE_KEY}", "Content-Type": "application/json"}
    mesaj = f"Konu: {soru}\n\nToplanan İstihbarat:\n- {arastirma}\n- {denetci}\n- {vizyoner}"
    data = {"model": "command-r-plus-08-2024", "message": mesaj, "preamble": BASDANISMAN_PREAMBLE, "max_tokens": 150, "temperature": 0.1}
    r = requests.post(url, headers=headers, json=data, timeout=20)
    return r.json().get("text", "Yanıt alınamadı.")

# ─────────────────────────────────────────────
# ANA MOTOR (API ENDPOINT)
# ─────────────────────────────────────────────

@app.post("/analyze")
async def analyze(soru: Soru):
    if not soru.text or not soru.text.strip():
        raise HTTPException(status_code=400, detail="Soru boş aga, neyi analiz edeyim?")
    if not GROQ_KEY or not COHERE_KEY:
        raise HTTPException(status_code=500, detail="Sunucuda API Anahtarları eksik.")

    try:
        client = Groq(api_key=GROQ_KEY)
        
        # Olaylar silsilesi başlıyor (Sokaktaki meydan savaşı)
        arastirma_v1 = ajan_arastirmaci(soru.text, client)
        denetci_v1 = ajan_denetci(soru.text, arastirma_v1, client)
        arastirma_v2 = ajan_arastirmaci_revize(soru.text, arastirma_v1, denetci_v1, client)
        denetci_v2 = ajan_denetci(soru.text, arastirma_v2, client)
        vizyoner = ajan_vizyoner(soru.text, denetci_v2, client)
        karar = ajan_basdanisman(soru.text, arastirma_v2, denetci_v2, vizyoner)
        
        # Gradio'nun markdown çöplüğü yerine vitrine saf JSON verisi fırlatıyoruz.
        return {
            "final_karar": karar,
            "arastirma": arastirma_v2,
            "denetleme": denetci_v2,
            "vizyon": vizyoner
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

