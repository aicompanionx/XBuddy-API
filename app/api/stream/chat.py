import json

from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect

from app.services.agent.general_chat import GeneralChatAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)

# General chat route
router = APIRouter(prefix="/chat", tags=["General Chat Service"])


@router.websocket(
    "/ws",
)
async def general_chat_websocket(websocket: WebSocket):
    """
    WebSocket interface, supports multiple message types:
    - ping: Heartbeat detection
    - close: Close connection
    - chat: Normal chat message
    """
    await websocket.accept()
    agent = GeneralChatAgent()

    try:
        while True:
            # Receive message
            raw_data = await websocket.receive_text()
            logger.info(f"Received message: {raw_data}")

            try:
                data = json.loads(raw_data)
                msg_type = data.get("type")
                msg_data = data.get("data")

                # Handle different types of messages
                if msg_type == "ping":
                    # Heartbeat detection
                    await websocket.send_json(
                        {
                            "data": {"message": "pong", "code": 0},
                            "type": "ping",
                        }
                    )
                    continue

                elif msg_type == "close":
                    # Close connection
                    await websocket.close()
                    logger.info("Client requested to close connection")
                    break

                elif msg_type == "chat":
                    # Chat message
                    if not msg_data or not all(
                        k in msg_data for k in ["content", "lang"]
                    ):
                        await websocket.send_json(
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
                        # Get response
                        response = agent.agent.run(content, stream=True)

                        ai_response_content = ""
                        for chunk in response:
                            if chunk.content is not None:
                                ai_response_content += chunk.content
                                await websocket.send_json(
                                    {
                                        "data": {
                                            "message": chunk.content,
                                            "code": 0,
                                        },
                                        "type": "chat",
                                    }
                                )

                        if ai_response_content:
                            await websocket.send_json(
                                {
                                    "data": {"message": "EOF", "code": 2},
                                    "type": "EOF",
                                }
                            )

                    except Exception as e:
                        await websocket.send_json(
                            {
                                "data": {
                                    "message": f"Error occurred during chat: {str(e)}",
                                    "code": 1,
                                },
                                "type": "error",
                            }
                        )
                        logger.error(f"Error occurred during chat: {str(e)}")

                else:
                    # Unsupported message type
                    await websocket.send_json(
                        {
                            "data": {
                                "message": f"Unsupported message type: {msg_type}",
                                "code": 1,
                            },
                            "type": "error",
                        }
                    )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "data": {
                            "message": "Invalid JSON format, please send valid JSON",
                            "code": 1,
                        },
                        "type": "error",
                    }
                )
                logger.error("JSON decoding error")
            except Exception as e:
                await websocket.send_json(
                    {
                        "data": {
                            "message": f"Error occurred during message processing: {str(e)}",
                            "code": 1,
                        },
                        "type": "error",
                    }
                )
                logger.error(f"Error occurred during message processing: {str(e)}")

    except WebSocketDisconnect:
        logger.info("WebSocket connection disconnected")
    except Exception as e:
        logger.error(f"WebSocket processing error: {str(e)}")
        try:
            await websocket.send_json(
                {
                    "data": {"message": f"Server error: {str(e)}", "code": 1},
                    "type": "error",
                }
            )
        except Exception:
            pass
