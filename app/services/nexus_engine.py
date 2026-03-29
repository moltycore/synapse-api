import json
from app.agents.solo_agent import process_solo
from app.agents.moderator_agents import get_gatekeeper_res
from app.agents.groq_agents import get_core_res, get_ghost_res, get_void_res
from app.agents.cohere_agents import get_yargic_res # Prime rolü burada

def run_nexus_protocol_stream(soru: str, mode: str = "nexus"):
    def emit(event_type, data):
        payload = json.dumps({"event": event_type, "data": data})
        print(f"DEBUG: Event={event_type} | Data={data}")
        return f"data: {payload}\n\n"

    # ---------------------------------------------------------
    # 1. GATEKEEPER: Niyet Okuyucu (Trafik Polisi)
    # ---------------------------------------------------------
    yield emit("status", "gatekeeper")
    niyet = get_gatekeeper_res(soru)

    # Niyet ONAY ise diğer ajanları hiç uyandırma, kısa kes.
    if niyet == "ONAY":
        kisa_json = {
            "karar": "BEKLE",
            "risk_skoru": 0,
            "gerekce": "Kullanıcı onayı alındı.",
            "racon": "Mevzu anlaşıldı, yeni komut bekleniyor.",
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

    # ---------------------------------------------------------
    # 2. SOLO MODU: Niyet ONAY değilse ve mod SOLO ise
    # ---------------------------------------------------------
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
            "racon": answer,
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

    # ---------------------------------------------------------
    # 3. NEXUS MODU: AI Yargıtayı Döngüsü (CORE -> GHOST -> VOID -> CORE)
    # ---------------------------------------------------------
    rota = "COMPLEX"

    # A. CORE: İlk İskelet
    yield emit("status", "core")
    core_ilk_taslak = get_core_res(soru)

    # B. GHOST: Açık Bulma (Sızma)
    yield emit("status", "ghost")
    ghost_bulgulari = get_ghost_res(core_ilk_taslak)

    # C. VOID: Eleştiri ve Revize Talebi
    yield emit("status", "void")
    void_elestirisi = get_void_res(core_ilk_taslak, ghost_bulgulari)

    # D. CORE (REFINE): Eleştiriye göre kendini düzeltme
    yield emit("status", "core_refine")
    core_final = get_core_res(soru, context=void_elestirisi)

    # E. PRIME (YARGIÇ): Son Sentez ve Vizyon
    yield emit("status", "prime")
    try:
        # Prime'a hem Ghost'un bulduklarını hem de Core'un son halini veriyoruz.
        yargic_karari = get_yargic_res(soru, core_final, ghost_bulgulari, "Vizyon Prime'a entegre edildi.")
    except Exception as e:
        yargic_karari = json.dumps({
            "karar": "HATA", "risk_skoru": -1, "gerekce": "Sistem hatası.",
            "racon": "Mühür basılamadı, teknik arıza mevcut.",
            "vizyon_onerisi": "Sistemi resetleyip tekrar deneyelim."
        })

    # F. ÇIKIŞ
    yield emit("done", {
        "rota": rota,
        "analiz": core_final, # Artık rafine edilmiş analiz gidiyor
        "denetim": ghost_bulgulari, # Denetim kısmında Ghost'un saptamaları var
        "vizyon": void_elestirisi, # Vizyon durağında eleştiriyi göstererek süreci şeffaflaştırıyoruz
        "yargic": yargic_karari
    })
