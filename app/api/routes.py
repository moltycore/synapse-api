from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.schemas.models import AnalysisRequest
from app.services.nexus_engine import run_nexus_protocol_stream
from app.utils.blackbox_logger import BlackboxLogger
from evaluate_nexus import fire_eval_sequence

router = APIRouter()
logger = BlackboxLogger()

@router.post("/analyze")
async def analyze_endpoint(request: AnalysisRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Null input detected.")

    # TELEMETRY: Log incoming request
    logger.log_event("API_GATEWAY", 0, "REQUEST_RECEIVED", f"Mode: {request.mode} | Query_Size: {len(request.text)}")

    try:
        return StreamingResponse(
            run_nexus_protocol_stream(request.text, request.mode), 
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.log_event("API_GATEWAY", 0, "RUNTIME_ERROR", str(e))
        raise HTTPException(status_code=500, detail=f"Runtime Error: {str(e)}")

@router.get("/sys/fire-eval")
def trigger_langsmith_eval(bg_tasks: BackgroundTasks):
    # TELEMETRY: Log manual trigger
    logger.log_event("EVAL_SYSTEM", 0, "TEST_TRIGGERED", "LangSmith evaluation sequence initiated.")
    
    bg_tasks.add_task(fire_eval_sequence)
    return {"status": "SUCCESS", "message": "Evaluation sequence injected into background tasks."}
