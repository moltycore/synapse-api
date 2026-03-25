from app.agents.hf_agents import get_sme_res
from app.agents.groq_agents import get_arastirmaci_res, get_denetci_res
from app.agents.deepseek_agents import get_moderator_res
from app.agents.cohere_agents import get_basdanisman_res

# Savaşın kaç el süreceğini belirleyen o meşhur limit.
MAX_ITERATION = 2

def run_nexus_protocol(soru: str):
    # 1. Masaya ilk veriyi SME fırlatır (Değişmez ham veri)
    sme_veri = get_sme_res(soru)
    
    arastirma_cevap = ""
    denetci_cevap = ""
    
    # 2. Yuvarlak Masa Kavgası (İterasyon Döngüsü)
    for i in range(1, MAX_ITERATION + 1):
        if i == 1:
            # İlk kan: Araştırmacı sadece SME verisine bakar
            arastirma_cevap = get_arastirmaci_res(soru, sme_veri)
        else:
            # İkinci raunt: Araştırmacı yediği tokatla (denetçi eleştirisiyle) veriyi düzeltmek zorunda
            revize_soru = f"{soru}\nÖnceki hataların ve yediğin fırça: {denetci_cevap}\nŞimdi egonu ez ve veriyi düzelt!"
            arastirma_cevap = get_arastirmaci_res(revize_soru, sme_veri)
        
        # Denetçi acımaz, her turda sunulan yeni veriyi tekrar paramparça eder
        denetci_cevap = get_denetci_res(arastirma_cevap)

    # 3. Moderatör (DeepSeek) masaya yumruğunu vurur. Kavga biter, kesin hüküm çıkar.
    moderator_hukmu = get_moderator_res(soru, sme_veri, arastirma_cevap, denetci_cevap)
    
    # 4. Başdanışman (Cohere) hükmü alır, sokağa/kullanıcıya kendi fikriymiş gibi satar.
    final_sentez = get_basdanisman_res(moderator_hukmu)
    
    # 5. Lovable / Vercel (Frontend) tarafına fırlatılacak olan o jilet gibi JSON paketi
    return {
        "final_karar": final_sentez,
        "sme": sme_veri,
        "arastirma": arastirma_cevap,
        "denetleme": denetci_cevap,
        "moderator": moderator_hukmu
    }
