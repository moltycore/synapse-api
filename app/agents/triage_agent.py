import groq
from app.core.config import GROQ_KEY
from app.prompts.nexus_prompts import TRIAGE_SYSTEM

client = groq.Client(api_key=GROQ_KEY)

# 🔥 ANA FONKSİYON
def check_complexity(soru):
    text = soru.lower().strip()

    # =========================
    # 1. HARD RULES (LLM YOK)
    # =========================
    
    # kısa soru = SHORT
    if len(text.split()) <= 3:
        return {"route": "SHORT", "answer": "Kısa kes, net sor 😏"}

    # kesin COMPLEX tetikleyiciler
    complex_keywords = [
        "ne yapmalıyım", "nasıl kurarım", "strateji", "risk",
        "yatırım", "gelecek", "plan", "sistem", "optimiz"
    ]
    
    if any(k in text for k in complex_keywords):
        return {"route": "COMPLEX"}

    # =========================
    # 2. LLM (SADECE GEREKİRSE)
    # =========================
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM},
                {"role": "user", "content": soru}
            ],
            max_tokens=5,  # 🔥 DÜŞÜRDÜK
            temperature=0  # 🔥 STABİL
        )

        res = response.choices[0].message.content.strip().upper()

        if "COMPLEX" in res:
            return {"route": "COMPLEX"}
        elif "MEDIUM" in res:
            return {"route": "MEDIUM"}
        else:
            return {"route": "SHORT", "answer": "Basit soru bu 😌"}

    except Exception as e:
        print(f"Triage Hatası: {e}")
        return {"route": "COMPLEX"}
