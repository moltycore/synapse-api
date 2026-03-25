from fastapi import APIRouter, HTTPException
from app.schemas.models import Soru
from app.services.nexus_engine import run_nexus_protocol

router = APIRouter()

@router.post("/analyze")
async def analyze_endpoint(soru: Soru):
    if not soru.text or not soru.text.strip():
        raise HTTPException(status_code=400, detail="Soru boş aga, neyi analiz edeyim?")

    try:
        # Gelen soruyu alıp 5'li konseyin ortasına, yuvarlak masaya atıyoruz.
        sonuc = run_nexus_protocol(soru.text)
        return sonuc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Motor patladı: {str(e)}")
