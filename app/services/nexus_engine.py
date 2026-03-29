import json
from app.agents.solo_agent import process_solo
from app.agents.groq_agents import get_analizci_res, get_denetci_res
from app.agents.moderator_agents import call_puter
from app.agents.cohere_agents import get_yargic_res

def run_nexus_protocol_stream(soru: str, mode: str = "nexus"):
    def emit(event_type, data):
        payload = json.dumps({"event": event_type, "data": data})
        print(f"DEBUG: Event={event_type} | Data={data}")
        return f"data: {payload}\n\n"

    # ---------------------------------------------------------
    # 1. SOLO MODU: Sadece tekil uzman çalışır, işi bitirir.
    # ---------------------------------------------------------
    if mode == "solo":
        yield emit("status", "solo")
        try:
            solo_result = process_solo(soru)
            answer = solo_result.get("answer", "Solo bir cevap üretemedi.")
        except Exception as e:
            print(f"ERROR Solo: {e}")
            answer = "Solo motoru çöktü."

        kisa_json = {
            "karar": "BİLGİ",
            "risk_skoru": 0,
            "gerekce": "Solo Modu",
            "racon": answer
        }
        yield emit("done", {
            "rota": "SHORT", 
            "analiz": "Solo modunda analizci pas geçildi.", 
            "denetim": "Pas.", 
            "vizyon": "Pas.",
            "yargic": json.dumps(kisa_json)
        })
        return

    # ---------------------------------------------------------
    # 2. NEXUS MODU: Solo uzmanı bypass et, direkt masaya geç.
    # ---------------------------------------------------------
    rota = "COMPLEX" # Nexus modunda her şey ağır abilere gider.

    yield emit("status", "analizci")
    try:
        analizci_veri = get_analizci_res(soru)
    except Exception as e:
        print(f"ERROR Analizci: {e}")
        analizci_veri = "Analiz motoru şu an uykuda."

    yield emit("status", "denetci")
    try:
        denetci_veri = get_denetci_res(analizci_veri)
    except Exception as e:
        print(f"ERROR Denetci: {e}")
        denetci_veri = "Risk denetimi yapılamadı."

    # Nexus modunda olduğumuz için Vizyoner direkt devreye girer.
    yield emit("status", "vizyoner")
    try:
        puter_vizyon = call_puter(soru, analizci_veri, denetci_veri)
    except Exception as e:
        print(f"ERROR Vizyoner: {e}")
        puter_vizyon = "Vizyoner şu an ufku göremiyor."

    yield emit("status", "yargic")
    try:
        yargic_karari = get_yargic_res(soru, analizci_veri, denetci_veri, puter_vizyon)
    except Exception as e:
        print(f"ERROR Yargıç: {e}")
        yargic_karari = json.dumps({
            "karar": "HATA", "risk_skoru": -1, "gerekce": "Sistem hatası.",
            "racon": "Mühür basılamadı, teknik arıza mevcut."
        })

    yield emit("done", {
        "rota": rota,
        "analiz": analizci_veri,
        "denetim": denetci_veri,
        "vizyon": puter_vizyon,
        "yargic": yargic_karari
    })
