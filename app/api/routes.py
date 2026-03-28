from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.models import Soru

from app.services.nexus_engine import run_nexus_protocol_stream

router = APIRouter()

@router.post("/analyze")
async def analyze_endpoint(soru: Soru):
    if not soru.text or not soru.text.strip():
        raise HTTPException(status_code=400, detail="Soru boş aga, neyi analiz edeyim?")

    try:
        # Canlı veri akışını (SSE) başlatıyoruz. Yeni eklenen 'mode' bilgisini de motora veriyoruz.
        return StreamingResponse(
            run_nexus_protocol_stream(soru.text, soru.mode), 
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Motor patladı: {str(e)}")
