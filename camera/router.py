from fastapi import APIRouter, Response, HTTPException, Query, UploadFile, File, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse
import cv2
import numpy as np
from typing import Dict
import uuid

from camera import service
from camera.buffer import FrameBufferManager

router = APIRouter(prefix="/camera", tags=["camera"])
buffer_manager = FrameBufferManager.get_instance()

@router.get("/stream")
def video_stream():
    """
    Stream video from the camera.
    This endpoint returns a multipart response containing JPEG frames.
    """
    try:
        return StreamingResponse(
            service.generate_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/snapshot")
def take_snapshot():
    """
    Take a single snapshot from the camera.
    Returns a JPEG image.
    """
    try:
        with service.VideoStream() as camera:
            frame = camera.get_frame()
            return Response(content=frame, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings/{setting}")
def update_camera_setting(
    setting: str,
    value: int = Query(..., ge=0, le=100)
) -> Dict[str, str]:
    """
    Update camera settings (brightness, contrast, saturation, exposure).
    """
    try:
        with service.VideoStream() as camera:
            if camera.update_setting(setting, value):
                return {"message": f"Successfully updated {setting}"}
            return {"message": f"Failed to update {setting}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-frame")
async def process_frame(
    image: UploadFile = File(...),
    session_id: str = Query(None)
) -> Dict:
    """
    Process a frame from the client's camera.
    Returns face detection results.
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Read image file
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        # Get or create buffer for this session
        buffer = buffer_manager.get_buffer(session_id)
        buffer.add_frame(frame, session_id)

        # For now, return simple response
        # Later we'll add face detection processing
        return {
            "success": True,
            "session_id": session_id,
            "faces_detected": 0,
            "message": "Frame processed successfully",
            "buffer_status": buffer.get_buffer_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/buffer-status/{session_id}")
async def get_buffer_status(session_id: str) -> Dict:
    """Get status of a specific buffer"""
    buffer = buffer_manager.get_buffer(session_id, create_if_missing=False)
    if not buffer:
        raise HTTPException(status_code=404, detail="Buffer not found")
    return buffer.get_buffer_status()

@router.delete("/buffer/{session_id}")
async def clear_buffer(session_id: str) -> Dict:
    """Clear a specific buffer"""
    buffer = buffer_manager.get_buffer(session_id, create_if_missing=False)
    if not buffer:
        raise HTTPException(status_code=404, detail="Buffer not found")
    buffer.clear_buffer()
    return {"message": "Buffer cleared successfully"} 