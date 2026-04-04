 from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.models import AnalysisRequest
from app.services.nexus_engine import run_nexus_protocol_stream
from app.utils.blackbox_logger import BlackboxLogger

router = APIRouter()
logger = BlackboxLogger()

@router.post("/analyze")
async def analyze_endpoint(request: AnalysisRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Null input detected.")

    # TELEMETRY: Log incoming request to Puter Dashboard
    logger.log_event("API_GATEWAY", 0, "REQUEST_RECEIVED", f"Mode: {request.mode} | Query_Size: {len(request.text)}")

    try:
        return StreamingResponse(
            run_nexus_protocol_stream(request.text, request.mode), 
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.log_event("API_GATEWAY", 0, "RUNTIME_ERROR", str(e))
        raise HTTPException(status_code=500, detail=f"Runtime Error: {str(e)}")
