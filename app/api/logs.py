import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse

from app.utils.logger import FILTERED_MODULES, register_websocket, unregister_websocket

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
    responses={404: {"description": "Not Found"}},
)

# Get log file path
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
STATIC_DIR = Path(__file__).parent.parent.parent / "static"


@router.get("/", response_class=HTMLResponse)
async def get_logs_page():
    """Get log viewer page"""
    return FileResponse(STATIC_DIR / "log-viewer.html")


# Store all active WebSocket connections
active_connections: List[WebSocket] = []

# Store recent log entries in memory
recent_logs: List[Dict[str, Any]] = []
max_recent_logs = 1000


class WebSocketLogHandler(logging.Handler):
    """Log handler that sends logs to WebSocket clients"""

    async def emit_log(self, record):
        # Filter out logs that don't need to be displayed
        if any(record.name.startswith(module) for module in FILTERED_MODULES):
            return

        log_entry = self.format_log_record(record)

        # Add to recent logs
        recent_logs.append(log_entry)
        if len(recent_logs) > max_recent_logs:
            recent_logs.pop(0)

        # Broadcast to all WebSocket connections
        if active_connections:
            message = json.dumps({"action": "new_log", "log": log_entry})
            await asyncio.gather(
                *[connection.send_text(message) for connection in active_connections],
                return_exceptions=True,
            )

    def emit(self, record):
        """Override emit method to send logs to WebSocket"""
        try:
            # Check if there is a running event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.emit_log(record))
            else:
                # If there is no running event loop, ignore
                pass
        except RuntimeError:
            # Catch "no event loop running" exception
            pass

    @staticmethod
    def format_log_record(record):
        """Format log record as a dictionary"""
        return {
            "asctime": datetime.fromtimestamp(record.created).strftime(
                "%Y-%m-%d %H:%M:%S,%f"
            )[:-3],
            "name": record.name,
            "levelname": record.levelname,
            "level": record.levelname,  # Add level field for filtering
            "message": record.getMessage(),
            "timestamp": datetime.fromtimestamp(record.created).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "module": record.name,
            "emoji": "✅"
            if record.levelname == "INFO"
            else "🔍"
            if record.levelname == "DEBUG"
            else "⚠️"
            if record.levelname == "WARNING"
            else "❌"
            if record.levelname == "ERROR"
            else "🔥"
            if record.levelname == "CRITICAL"
            else "📄",
        }


# Initialize WebSocket log handler
websocket_handler = WebSocketLogHandler()
websocket_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(websocket_handler)


@router.websocket("/ws")
async def logs_websocket(websocket: WebSocket):
    """
    WebSocket endpoint, used to receive logs in real-time
    """
    await websocket.accept()
    try:
        # Register WebSocket connection
        register_websocket(websocket)
        active_connections.append(websocket)

        # Send recent log entries to new connection
        if recent_logs:
            await websocket.send_json({"action": "history", "logs": recent_logs})

        # Keep connection open until client disconnects
        while True:
            # Wait for message (ping or command)
            data = await websocket.receive_text()

            # Handle different types of messages
            if data == "ping":
                # Send JSON format ping response
                await websocket.send_json(
                    {"action": "pong", "timestamp": datetime.now().isoformat()}
                )
            else:
                # Try to parse JSON command
                try:
                    cmd = json.loads(data)
                    if isinstance(cmd, dict) and cmd.get("action") == "get_history":
                        # Client requests history logs
                        await websocket.send_json(
                            {"action": "history", "logs": recent_logs}
                        )
                except json.JSONDecodeError:
                    # Non-JSON format message, ignore
                    pass
    except WebSocketDisconnect:
        # When WebSocket connection is closed, unregister
        unregister_websocket(websocket)
        if websocket in active_connections:
            active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"Log WebSocket handler exception: {str(e)}")
        unregister_websocket(websocket)
        if websocket in active_connections:
            active_connections.remove(websocket)


@router.get("/files")
async def get_log_files():
    """Get all log files"""
    try:
        if not LOGS_DIR.exists():
            return {"files": []}

        files = [
            {
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            }
            for f in LOGS_DIR.glob("*.log*")
            if f.is_file()
        ]

        # Sort by modified time (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)

        return {"files": files}
    except Exception as e:
        logger.error(f"Get log files failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get log files failed: {str(e)}")


@router.get("/content/{filename}")
async def get_log_content(filename: str, limit: Optional[int] = None):
    """Get log file content"""
    try:
        file_path = LOGS_DIR / filename

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(
                status_code=404, detail=f"Log file {filename} does not exist"
            )

        # Validate file name (prevent path traversal attack)
        if not filename.endswith(
            (".log", ".log.1", ".log.2", ".log.3", ".log.4", ".log.5")
        ):
            raise HTTPException(status_code=400, detail="Invalid log file name")

        # Get file content
        with open(file_path, "r", encoding="utf-8") as f:
            if limit:
                lines = []
                for i, line in enumerate(f):
                    if i >= limit:
                        break
                    lines.append(line)
                content = "".join(lines)
            else:
                content = f.read()

        return {"content": content}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Read log file {filename} failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Read log file failed: {str(e)}")


# Load recent logs from file
def load_recent_logs_from_file():
    """Load recent logs from file"""
    global recent_logs

    try:
        log_file = LOGS_DIR / "app.log"
        if not log_file.exists():
            return

        lines = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                lines.append(line.strip())
                if len(lines) > max_recent_logs:
                    lines.pop(0)

        # Parse log lines
        for line in lines:
            try:
                # Try to parse log line format
                # E.g. 2023-08-01 12:34:56,789 - app.main - INFO - 服务器启动成功
                parts = line.split(" - ", 3)
                if len(parts) == 4:
                    timestamp, name, level, message = parts

                    # Apply same filtering rules
                    if any(name.startswith(module) for module in FILTERED_MODULES):
                        continue

                    recent_logs.append(
                        {
                            "asctime": timestamp,
                            "name": name,
                            "levelname": level,
                            "level": level,
                            "message": message,
                            "timestamp": timestamp,
                            "module": name,
                            "emoji": "✅"
                            if level == "INFO"
                            else "🔍"
                            if level == "DEBUG"
                            else "⚠️"
                            if level == "WARNING"
                            else "❌"
                            if level == "ERROR"
                            else "🔥"
                            if level == "CRITICAL"
                            else "📄",
                        }
                    )
            except Exception:
                # Ignore parse failed lines
                continue

    except Exception as e:
        logger.error(f"Load recent logs from file failed: {str(e)}")


# Load recent logs from file when starting
load_recent_logs_from_file()
