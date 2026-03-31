from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.models import AnalysisRequest
from app.services.nexus_engine import run_nexus_protocol_stream

router = APIRouter()

@router.post("/analyze")
async def analyze_endpoint(request: AnalysisRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Null input detected.")

    try:
        # Delegation to nexus_engine for all modes (solo/nexus)
        return StreamingResponse(
            run_nexus_protocol_stream(request.text, request.mode), 
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Runtime Error: {str(e)}")
