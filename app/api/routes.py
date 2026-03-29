from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.schemas.models import Soru
from app.services.nexus_engine import run_nexus_protocol_stream
from app.agents.solo_agent import process_solo 

router = APIRouter()

@router.post("/analyze")
async def analyze_endpoint(soru: Soru):
    # Boş soru kontrolü
    if not soru.text or not soru.text.strip():
        raise HTTPException(status_code=400, detail="Soru boş aga, neyi analiz edeyim?")

    try:
        # SOLO MODU: Eski Triage'ın tüm izleri silindi.
        if soru.mode == "solo":
            result = process_solo(soru.text)
            
            async def generate_solo_response():
                # Frontend (Index.tsx) SSE akışı beklediği için yapıyı koruyoruz.
                payload = {
                    "event": "done",
                    "data": {
                        "analiz": result.get("answer"),
                        "racon": result.get("answer"), 
                        "denetim": "Pas geçildi.",
                        "vizyon": "Pas geçildi.",
                        "yargic": None
                    }
                }
                yield f"data: {json.dumps(payload)}\n\n"

            return StreamingResponse(
                generate_solo_response(), 
                media_type="text/event-stream"
            )

        # NEXUS MODU: Çoklu ajan simülasyonu ve canlı akış.
        return StreamingResponse(
            run_nexus_protocol_stream(soru.text, soru.mode), 
            media_type="text/event-stream"
        )
        
    except Exception as e:
        # Hata yönetimi
        raise HTTPException(status_code=500, detail=f"Motor patladı: {str(e)}")
