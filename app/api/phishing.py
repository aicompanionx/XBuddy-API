from fastapi import APIRouter, Body

from app.schemas.phishing import PhishingRequest, PhishingResponse
from app.services.phishing import check_phishing
from app.utils.custom_exceptions import BadRequestException, ServerException

router = APIRouter(prefix="/check-phishing", tags=["Phishing Detection"])


@router.post(
    "",
    response_model=PhishingResponse,
    summary="Check if a URL is a phishing website",
    description="Analyze the provided URL and determine if it is a potential phishing or fraudulent website",
)
async def api_check_phishing(
    req: PhishingRequest = Body(
        ..., example={"url": "http://suspicious-banking-site.com/login", "lang": "en"}
    ),
):
    """
    Check if a URL is a phishing website

    Parameters:
        req: Request containing the URL to check and the language of the response

    Returns:
        Phishing detection result, including whether it is a phishing website and an explanation

    Exceptions:
        BadRequestException: URL format is invalid or not supported
        ServerException: Phishing detection service is temporarily unavailable
    """
    try:
        # Add more URL format validation logic here if needed
        if not req.url.startswith(("http://", "https://")):
            raise BadRequestException("URL must start with http:// or https://")

        result = await check_phishing(req.url, req.lang)
        return PhishingResponse(data=result)
    except BadRequestException:
        # Re-raise BadRequestException for global exception handler
        raise
    except Exception as e:
        # Convert other exceptions to ServerException
        raise ServerException(f"Phishing detection service error: {str(e)}")
