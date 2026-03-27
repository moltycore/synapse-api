import json
from app.agents.triage_agent import check_complexity
from app.agents.sme_agents import get_sme_res
from app.agents.groq_agents import get_arastirmaci_res, get_denetci_res
from app.agents.moderator_agents import get_moderator_res, call_puter
from app.agents.cohere_agents import get_basdanisman_res

MAX_ITERATION = 2

def run_nexus_protocol_stream(soru: str):
    # Dışarıya canlı sinyal fırlatma formatımız (SSE)
    def emit(event_type, data):
        payload = json.dumps({"event": event_type, "data": data})
        return f"data: {payload}\n\n"

    # 0. ADIM: Kapıdaki koruma
    yield emit("status", "triage")
    triage = check_complexity(soru)

    if not triage["is_complex"]:
        yield emit("status", "basdanisman")
        final_sentez = get_basdanisman_res(soru, triage["short_answer"])
        
        # Hızlı yol bitişi
        yield emit("done", {
            "final_karar": final_sentez,
            "sme": "Gerek görülmedi.",
            "arastirma": "Pas geçildi.",
            "denetleme": "Gerek yok.",
            "vizyoner_puter": "Uykuda.",
            "moderator": triage["short_answer"]
        })
        return

    # 1. ADIM: SME
    yield emit("status", "sme")
    sme_veri = get_sme_res(soru)
    
    # 2. ADIM: Kaos Döngüsü
    arastirma_cevap = ""
    denetci_cevap = ""
    for i in range(1, MAX_ITERATION + 1):
        yield emit("status", "arastirmaci")
        if i == 1:
            arastirma_cevap = get_arastirmaci_res(soru, sme_veri)
        else:
            revize_soru = f"Denetçi fırçasıyla veriyi düzelt: {denetci_cevap}"
            arastirma_cevap = get_arastirmaci_res(revize_soru, sme_veri)
        
        yield emit("status", "denetci")
        denetci_cevap = get_denetci_res(arastirma_cevap)

    # 3. ADIM: Puter
    yield emit("status", "vizyoner_puter")
    puter_vizyon = call_puter(soru, sme_veri, arastirma_cevap, denetci_cevap)

    # 4. ADIM: Moderatör
    yield emit("status", "moderator")
    moderator_hukmu = get_moderator_res(soru, sme_veri, arastirma_cevap, denetci_cevap, puter_vizyon)
    
    # 5. ADIM: Başdanışman
    yield emit("status", "basdanisman")
    final_sentez = get_basdanisman_res(soru, moderator_hukmu)
    
    # Tüm kavga bitti, final paketi yolla
    yield emit("done", {
        "final_karar": final_sentez,
        "sme": sme_veri,
        "arastirma": arastirma_cevap,
        "denetleme": denetci_cevap,
        "vizyoner_puter": puter_vizyon,
        "moderator": moderator_hukmu
    })
