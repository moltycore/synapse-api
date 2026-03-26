from app.agents.sme_agents import get_sme_res
from app.agents.groq_agents import get_arastirmaci_res, get_denetci_res
from app.agents.moderator_agents import get_moderator_res
from app.agents.cohere_agents import get_basdanisman_res

MAX_ITERATION = 2

def run_nexus_protocol(soru: str):
    # 1. Masaya ilk veriyi SME fırlatır
    sme_veri = get_sme_res(soru)
    
    arastirma_cevap = ""
    denetci_cevap = ""
    
    # 2. Yuvarlak Masa Kavgası
    for i in range(1, MAX_ITERATION + 1):
        if i == 1:
            arastirma_cevap = get_arastirmaci_res(soru, sme_veri)
        else:
            revize_soru = f"{soru}\nÖnceki hataların ve denetçi fırçası: {denetci_cevap}\nŞimdi egonu ez ve veriyi düzelt!"
            arastirma_cevap = get_arastirmaci_res(revize_soru, sme_veri)
        
        denetci_cevap = get_denetci_res(arastirma_cevap)

    # 3. Moderatör (OpenRouter/Puter Hibrit) masaya yumruğunu vurur.
    moderator_hukmu = get_moderator_res(soru, sme_veri, arastirma_cevap, denetci_cevap)
    
    # 4. Başdanışman (Cohere) hem soruyu hem hükmü alır, sokağa satar.
    final_sentez = get_basdanisman_res(soru, moderator_hukmu)
    
    return {
        "final_karar": final_sentez,
        "sme": sme_veri,
        "arastirma": arastirma_cevap,
        "denetleme": denetci_cevap,
        "moderator": moderator_hukmu
    }
