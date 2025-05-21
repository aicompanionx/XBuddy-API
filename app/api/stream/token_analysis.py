import json

from agno.run.response import RunResponse
from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect

from app.services.agent.token_analysis import TokenAnalysisAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/token-analysis", tags=["Token Analysis Service"])


@router.websocket(
    "/ws",
)
async def token_analysis_websocket(websocket: WebSocket):
    """
    WebSocket interface, supports multiple message types:
    - token_analysis: Analyze token
    - ping: Heartbeat detection
    - close: Close connection
    - chat: Normal chat message
    """
    await websocket.accept()
    agent = TokenAnalysisAgent()
    connection_active = True

    async def safe_send(data):
        """Send message safely, check connection status"""
        nonlocal connection_active
        if not connection_active:
            return False
        try:
            await websocket.send_json(data)
            return True
        except WebSocketDisconnect:
            connection_active = False
            logger.info("WebSocket connection closed")
            return False
        except Exception as e:
            connection_active = False
            logger.error(f"Send message failed: {str(e)}")
            return False

    try:
        while connection_active:
            try:
                # Receive message
                raw_data = await websocket.receive_text()
                logger.info(f"Received message: {raw_data}")

                data = json.loads(raw_data)
                msg_type = data.get("type")
                msg_data = data.get("data")

                # Handle different types of messages
                if msg_type == "ping":
                    # Heartbeat detection
                    await safe_send(
                        {
                            "data": {"message": "pong", "code": 0},
                            "type": "ping",
                        }
                    )

                elif msg_type == "close":
                    # Close connection
                    await websocket.close()
                    connection_active = False
                    logger.info("Client requested to close connection")
                    break

                elif msg_type == "chat":
                    # Chat message
                    if not msg_data or not all(
                        k in msg_data for k in ["content", "lang"]
                    ):
                        await safe_send(
                            {
                                "data": {"message": "Invalid parameters", "code": 1},
                                "type": "error",
                            }
                        )
                        continue

                    # Get parameters
                    lang = msg_data.get("lang")
                    content = (
                        msg_data.get("content") + f"\n\n[setting: language: {lang}]"
                    )

                    # Run chat dialogue
                    try:
                        response: list[RunResponse] = agent.agent.run(
                            content, stream=True
                        )

                        all_response = ""
                        for chunk in response:
                            if not connection_active:
                                logger.info("Connection closed, stop sending messages")
                                break
                            if chunk.content:
                                all_response += chunk.content
                                success = await safe_send(
                                    {
                                        "data": {
                                            "message": chunk.content,
                                            "code": 0,
                                        },
                                        "type": "chat",
                                    }
                                )
                                if not success:
                                    logger.info(
                                        "Message sending failed, possible connection closed"
                                    )
                                    break
                        if all_response:
                            await safe_send(
                                {
                                    "data": {"message": "EOF", "code": 2},
                                    "type": "EOF",
                                }
                            )

                    except Exception as e:
                        if connection_active:
                            logger.error(f"Chat process error: {str(e)}", exc_info=True)
                            await safe_send(
                                {
                                    "data": {
                                        "message": f"Chat process error: {str(e)}",
                                        "code": 1,
                                    },
                                    "type": "error",
                                }
                            )

                else:
                    # Unhandled message type
                    await safe_send(
                        {
                            "data": {
                                "message": f"Unhandled message type: {msg_type}",
                                "code": 1,
                            },
                            "type": "error",
                        }
                    )

            except json.JSONDecodeError:
                if connection_active:
                    await safe_send(
                        {
                            "data": {"message": "Invalid JSON format", "code": 1},
                            "type": "error",
                        }
                    )
                    logger.error("Invalid JSON format")
            except WebSocketDisconnect:
                connection_active = False
                logger.info("WebSocket connection closed")
                break
            except Exception as e:
                if connection_active:
                    logger.error(f"Handle message error: {str(e)}", exc_info=True)
                    await safe_send(
                        {
                            "data": {
                                "message": f"Handle message error: {str(e)}",
                                "code": 1,
                            },
                            "type": "error",
                        }
                    )

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
