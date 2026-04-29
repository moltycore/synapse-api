import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.schemas.models import AnalysisRequest
from app.services.nexus_engine import run_nexus_protocol_stream
from app.utils.blackbox_logger import BlackboxLogger
from limiter import limiter

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
@limiter.limit("10/minute")
async def analyze_endpoint(request: Request, body: AnalysisRequest):
    file_count = len(body.fileContext) if body.fileContext else 0
    logger.log_event(
        "API_GATEWAY", 0, "REQUEST_RECEIVED",
        f"Mode: {body.mode} | Query_Size: {len(body.text)} | Files: {file_count}"
    )

    return StreamingResponse(
        safe_stream(
            run_nexus_protocol_stream(
                body.text,
                body.mode,
                body.fileContext
            )
        ),
        media_type="text/event-stream"
    )
