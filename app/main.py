from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.ai import router as ai_router
from app.api.phishing import router as phishing_router
from app.api.stream.chat import router as chat_router
from app.api.stream.news import router as news_router
from app.api.stream.token_analysis import router as token_analysis_router
from app.api.token import router as token_router
from app.api.tts import router as tts_router
from app.api.twitter import router as twitter_analysis_router
from app.api.twitter_raid import router as twitter_raid_router
from app.utils.error_handler import (
    general_exception_handler,
    http_exception_handler,
    pydantic_validation_handler,
    validation_exception_handler,
)
from app.utils.logger import get_logger, setup_logger

# Initialize logging system
setup_logger()

# Get logger instance
logger = get_logger(__name__)

app = FastAPI(
    title="XBuddy API",
    description="XBuddy V0.1 Backend API Service",
    version="0.1.0",
    docs_url="/",
)


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("=== XBuddy API service started ===")
    logger.info("Logging system initialized")


# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # : Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Custom Swagger UI
@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


# API prefix
api_prefix = "/api/v1"

# Register routers
app.include_router(news_router, prefix=api_prefix)
app.include_router(phishing_router, prefix=api_prefix)
app.include_router(twitter_analysis_router, prefix=api_prefix)
app.include_router(token_router, prefix=api_prefix)
app.include_router(tts_router, prefix=api_prefix)
app.include_router(ai_router, prefix=api_prefix)
app.include_router(token_analysis_router, prefix=api_prefix)
app.include_router(twitter_raid_router, prefix=api_prefix)
app.include_router(chat_router, prefix=api_prefix)

logger.info("Routers registered successfully")
