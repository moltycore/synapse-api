from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.schemas.models import Soru
from app.services.nexus_engine import run_nexus_protocol_stream
from app.agents.solo_agent import process_solo 

router = APIRouter()

@router.post("/analyze")
async def analyze_endpoint(request: Soru):
    # Validation
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Null input detected.")

    try:
        # Solo Mode Execution
        if request.mode == "solo":
            result = process_solo(request.text)
            
            async def generate_solo_response():
                # Enforce response schema for Index.tsx compatibility
                payload = {
                    "event": "done",
                    "data": {
                        "prime_result": result.get("answer")
                    }
                }
                yield f"data: {json.dumps(payload)}\n\n"

            return StreamingResponse(
                generate_solo_response(), 
                media_type="text/event-stream"
            )

        # Nexus Mode: Multi-agent stream
        return StreamingResponse(
            run_nexus_protocol_stream(request.text, request.mode), 
            media_type="text/event-stream"
        )
        
    except Exception as e:
        # Internal error logging
        raise HTTPException(status_code=500, detail=f"Runtime Error: {str(e)}")
