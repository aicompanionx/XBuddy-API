import uvicorn
from dotenv import load_dotenv

# Load logger module
from app.utils.logger import get_logger, setup_logger

# Load environment variables
load_dotenv()

# Set up logger
setup_logger()
logger = get_logger(__name__)


def run_server():
    """
    Start FastAPI server
    """
    try:
        # Start uvicorn server
        logger.info("Starting XBuddy API service...")
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="debug",
        )
    except KeyboardInterrupt:
        logger.info("Server was manually terminated by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
    finally:
        logger.info("Server has been closed")


if __name__ == "__main__":
    run_server()
