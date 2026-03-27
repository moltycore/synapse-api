import json
from app.agents.triage_agent import check_complexity
from app.agents.groq_agents import get_analizci_res, get_denetci_res
from app.agents.moderator_agents import call_puter
from app.agents.cohere_agents import get_yargic_res

def run_nexus_protocol_stream(soru: str):
    def emit(event_type, data):
        payload = json.dumps({"event": event_type, "data": data})
        # LOGLARI GÖRMEK İÇİN BURAYI EKLEDİK:
        print(f"DEBUG: Event={event_type} | Data={data}") 
        return f"data: {payload}\n\n"

    # 0. ADIM: Kapıdaki koruma (Triage)
    yield emit("status", "triage")
    triage = check_complexity(soru)
    rota = triage.get("route", "COMPLEX") # Hata olursa en ağır rotadan devam

    # --- 1. VİTES: SHORT (Hızlı ve Alaycı Yol) ---
    if rota == "SHORT":
        yield emit("status", "yargic")
        # Lovable arayüzü JSON beklediği için kısa cevabı formata uyduruyoruz
        kisa_json = {
            "karar": "BİLGİ",
            "risk_skoru": "0",
            "gerekce": "Basit Sohbet",
            "racon": triage.get("answer", "Kısa cevap verilemedi.")
        }
        yield emit("done", {
            "rota": "SHORT",
            "analiz": "Pas geçildi.",
            "denetim": "Pas geçildi.",
            "vizyon": "Uykuda.",
            "yargic": json.dumps(kisa_json) 
        })
        return

    # --- 2. VİTES: MEDIUM ve COMPLEX İÇİN ORTAK YOL ---
    
    # Adım 1: Analizci (Eski SME + Araştırmacı birleşimi)
    yield emit("status", "analizci")
    analizci_veri = get_analizci_res(soru)

    # Adım 2: Denetçi (Siyah Kuğu)
    yield emit("status", "denetci")
    denetci_veri = get_denetci_res(analizci_veri)

    # --- 3. VİTES: SADECE COMPLEX ROTAYA ÖZEL ---
    puter_vizyon = "Gerekli görülmedi (MEDIUM Rota)."
    if rota == "COMPLEX":
        yield emit("status", "vizyoner")
        puter_vizyon = call_puter(soru, analizci_veri, denetci_veri)

    # Adım 3: Yargıç (Tüm veriyi toplayıp JSON basan son otorite)
    yield emit("status", "yargic")
    yargic_karari = get_yargic_res(soru, analizci_veri, denetci_veri, puter_vizyon)

    # Tüm akış bitti, final paketini yolla
    yield emit("done", {
        "rota": rota,
        "analiz": analizci_veri,
        "denetim": denetci_veri,
        "vizyon": puter_vizyon,
        "yargic": yargic_karari
    })
