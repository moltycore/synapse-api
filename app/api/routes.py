import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.models import AnalysisRequest
from app.services.nexus_engine import run_nexus_protocol_stream
from app.utils.blackbox_logger import BlackboxLogger

router = APIRouter()
logger = BlackboxLogger()


def safe_stream(generator):
    try:
        yield from generator
    except Exception as e:
        logger.log_event("API_GATEWAY", 0, "STREAM_ERROR", str(e))
        error_payload = json.dumps({"event": "error", "data": str(e)})
        yield f"data: {error_payload}\n\n"


@router.post("/analyze")
async def analyze_endpoint(request: AnalysisRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Null input detected.")

    file_count = len(request.fileContext) if request.fileContext else 0
    logger.log_event(
        "API_GATEWAY", 0, "REQUEST_RECEIVED",
        f"Mode: {request.mode} | Query_Size: {len(request.text)} | Files: {file_count}"
    )

    return StreamingResponse(
        safe_stream(
            run_nexus_protocol_stream(
                request.text,
                request.mode,
                request.fileContext
            )
        ),
        media_type="text/event-stream"
               )
