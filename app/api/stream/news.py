from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect

from app.services.news import connection_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/news", tags=["News Service"])


@router.websocket(
    "/ws",
)
async def news_websocket(websocket: WebSocket):
    """
    News WebSocket interface
    """

    await connection_manager.connect(websocket)
    try:
        logger.info("WebSocket connection established")
        # Keep the connection until the client disconnects
        while True:
            # Wait for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        connection_manager.disconnect(websocket)
