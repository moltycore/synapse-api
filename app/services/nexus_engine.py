import json
from app.agents.triage_agent import check_complexity
from app.agents.groq_agents import get_analizci_res, get_denetci_res
from app.agents.moderator_agents import call_puter
from app.agents.cohere_agents import get_yargic_res

def run_nexus_protocol_stream(soru: str):
    def emit(event_type, data):
        payload = json.dumps({"event": event_type, "data": data})
        print(f"DEBUG: Event={event_type} | Data={data}") 
        return f"data: {payload}\n\n"

    # 0. ADIM: Kapıdaki koruma (Triage)
    yield emit("status", "triage")
    try:
        triage = check_complexity(soru)
        rota = triage.get("route", "COMPLEX")
        answer = triage.get("answer", "")
    except Exception as e:
        print(f"ERROR Triage: {e}")
        rota = "COMPLEX"
        answer = ""

    # --- 1. VİTES: SHORT ---
    if rota == "SHORT":
        yield emit("status", "yargic")
        kisa_json = {
            "karar": "BİLGİ",
            "risk_skoru": "0",
            "gerekce": "Basit Sohbet",
            "racon": answer if answer else "Kısa cevap üretilemedi."
        }
        yield emit("done", {
            "rota": "SHORT", "analiz": "Pas.", "denetim": "Pas.", "vizyon": "Pas.",
            "yargic": json.dumps(kisa_json) 
        })
        return

    # --- 2. VİTES: MEDIUM / COMPLEX ---
    
    # Adım 1: Analizci
    yield emit("status", "analizci")
    try:
        analizci_veri = get_analizci_res(soru)
    except Exception as e:
        print(f"ERROR Analizci: {e}")
        analizci_veri = "Analiz motoru şu an uykuda, veri çekilemedi."

    # Adım 2: Denetçi
    yield emit("status", "denetci")
    try:
        denetci_veri = get_denetci_res(analizci_veri)
    except Exception as e:
        print(f"ERROR Denetci: {e}")
        denetci_veri = "Risk denetimi yapılamadı, sistem meşgul."

    # --- 3. VİTES: COMPLEX ÖZEL ---
    puter_vizyon = "Gerekli görülmedi (MEDIUM Rota)."
    if rota == "COMPLEX":
        yield emit("status", "vizyoner")
        try:
            puter_vizyon = call_puter(soru, analizci_veri, denetci_veri)
        except Exception as e:
            print(f"ERROR Vizyoner: {e}")
            puter_vizyon = "Vizyoner şu an ufku göremiyor."

    # Adım 3: Yargıç
    yield emit("status", "yargic")
    try:
        yargic_karari = get_yargic_res(soru, analizci_veri, denetci_veri, puter_vizyon)
    except Exception as e:
        print(f"ERROR Yargıç: {e}")
        yargic_karari = json.dumps({
            "karar": "HATA", "risk_skoru": "-", "gerekce": "Sistem hatası.",
            "racon": "Mühür basılamadı, teknik arıza mevcut."
        })

    yield emit("done", {
        "rota": rota,
        "analiz": analizci_veri,
        "denetim": denetci_veri,
        "vizyon": puter_vizyon,
        "yargic": yargic_karari
    })
