from app.agents.triage_agent import check_complexity
from app.agents.sme_agents import get_sme_res
from app.agents.groq_agents import get_arastirmaci_res, get_denetci_res
from app.agents.moderator_agents import get_moderator_res, call_puter
from app.agents.cohere_agents import get_basdanisman_res

MAX_ITERATION = 2

def run_nexus_protocol(soru: str):
    # 0. ADIM: Kapıdaki koruma (Groq) sınıflandırma ve dalga geçme
    triage = check_complexity(soru)

    if not triage["is_complex"]:
        # HIZLI YOL: Diğer ajanları uyandırmıyoruz
        final_sentez = get_basdanisman_res(soru, triage["short_answer"])
        return {
            "final_karar": final_sentez,
            "sme": "Gerek görülmedi.",
            "arastirma": "Pas geçildi.",
            "denetleme": "Gerek yok.",
            "vizyoner_puter": "Uykuda.",
            "moderator": triage["short_answer"]
        }

    # 1. ADIM: SME (Teknik Temel)
    sme_veri = get_sme_res(soru)
    
    # 2. ADIM: Kaos Döngüsü (Groq Ekibi)
    arastirma_cevap = ""
    denetci_cevap = ""
    for i in range(1, MAX_ITERATION + 1):
        if i == 1:
            arastirma_cevap = get_arastirmaci_res(soru, sme_veri)
        else:
            revize_soru = f"Denetçi fırçasıyla veriyi düzelt: {denetci_cevap}"
            arastirma_cevap = get_arastirmaci_res(revize_soru, sme_veri)
        denetci_cevap = get_denetci_res(arastirma_cevap)

    # 3. ADIM: Puter (Stratejik Vizyoner) - ARTIK AKTİF
    puter_vizyon = call_puter(soru, sme_veri, arastirma_cevap, denetci_cevap)

    # 4. ADIM: Moderatör (Hibrit) - Puter vizyonuyla besleniyor
    moderator_hukmu = get_moderator_res(soru, sme_veri, arastirma_cevap, denetci_cevap, puter_vizyon)
    
    # 5. ADIM: Başdanışman (Cohere) - Son Racon
    final_sentez = get_basdanisman_res(soru, moderator_hukmu)
    
    return {
        "final_karar": final_sentez,
        "sme": sme_veri,
        "arastirma": arastirma_cevap,
        "denetleme": denetci_cevap,
        "vizyoner_puter": puter_vizyon,
        "moderator": moderator_hukmu
    }
