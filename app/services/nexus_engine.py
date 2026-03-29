import json
from app.agents.solo_agent import process_solo
from app.agents.moderator_agents import get_gatekeeper_res
from app.agents.groq_agents import get_core_res, get_ghost_res, get_void_res
from app.agents.cohere_agents import get_yargic_res 

def run_nexus_protocol_stream(soru: str, mode: str = "nexus"):
    def emit(event_type, data):
        payload = json.dumps({"event": event_type, "data": data})
        print(f"DEBUG: Event={event_type} | Data={data}")
        return f"data: {payload}\n\n"

    # 1. GATEKEEPER
    yield emit("status", "gatekeeper")
    niyet = get_gatekeeper_res(soru)

    if niyet == "ONAY":
        kisa_json = {
            "karar": "BEKLE",
            "risk_skoru": 0,
            "gerekce": "Kullanıcı onayı alındı.",
            "nihai_rapor": "Mevzu anlaşıldı, yeni komut bekleniyor.",
            "vizyon_onerisi": "Konu kapandıysa yeni bir başlık açalım mı?"
        }
        yield emit("done", {
            "rota": "SHORT",
            "analiz": "Onay modu aktif.",
            "denetim": "Pas.",
            "vizyon": "Pas.",
            "yargic": json.dumps(kisa_json)
        })
        return

    # 2. SOLO MODU
    if mode == "solo":
        yield emit("status", "solo")
        try:
            solo_result = process_solo(soru)
            answer = solo_result.get("answer", "Solo bir cevap üretemedi.")
        except Exception as e:
            answer = f"Solo motoru çöktü: {str(e)}"

        kisa_json = {
            "karar": "BİLGİ",
            "risk_skoru": 0,
            "gerekce": "Solo Modu",
            "nihai_rapor": answer,
            "vizyon_onerisi": "Daha derin bir analiz için Nexus moduna geçebilirsin."
        }
        yield emit("done", {
            "rota": "SHORT", 
            "analiz": "Solo modunda analizci pas geçildi.", 
            "denetim": "Pas.", 
            "vizyon": "Pas.",
            "yargic": json.dumps(kisa_json)
        })
        return

    # 3. NEXUS MODU
    rota = "COMPLEX"

    yield emit("status", "core")
    core_ilk_taslak = get_core_res(soru)

    yield emit("status", "ghost")
    ghost_bulgulari = get_ghost_res(core_ilk_taslak)

    yield emit("status", "void")
    void_elestirisi = get_void_res(core_ilk_taslak, ghost_bulgulari)

    yield emit("status", "core_refine")
    core_final = get_core_res(soru, context=void_elestirisi)

    yield emit("status", "prime")
    try:
        yargic_karari = get_yargic_res(soru, core_final, ghost_bulgulari, "Vizyon Prime'a entegre edildi.")
    except Exception as e:
        yargic_karari = json.dumps({
            "karar": "HATA", "risk_skoru": -1, "gerekce": "Sistem hatası.",
            "nihai_rapor": "Mühür basılamadı, teknik arıza mevcut.",
            "vizyon_onerisi": "Sistemi resetleyip tekrar deneyelim."
        })

    yield emit("done", {
        "rota": rota,
        "analiz": core_final, 
        "denetim": ghost_bulgulari, 
        "vizyon": void_elestirisi, 
        "yargic": yargic_karari
    })
