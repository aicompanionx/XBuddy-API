import logging
from typing import Optional

import httpx
from agno.agent.agent import Agent
from agno.models.openai.like import OpenAILike

from app.config import get_config
from app.schemas.tts import TtsOptimizeData

logger = logging.getLogger(__name__)


async def optimize_text_for_tts(text: str) -> TtsOptimizeData:
    """
    Optimize the text for better TTS results using AI
    """
    config = get_config()
    tts_ai_config = config["external_apis"]["tts_ai"]

    model = OpenAILike(
        id=tts_ai_config["model"],
        api_key=tts_ai_config["key"],
        base_url=tts_ai_config["base_url"],
    )

    agent = Agent(
        model=model,
        response_model=TtsOptimizeData,
        instructions="""
        You are a TTS expert, optimize the text for TTS, you can insert (break) / (long-break) / (breath) / (laugh) to control the speech.
        """,
    )

    response = agent.run(text)

    return TtsOptimizeData(
        optimized_text=response.content.optimized_text,
    )


async def text_to_speech(
    text: str,
    temperature: float = 0.7,
    top_p: float = 0.7,
    chunk_length: int = 200,
    format: str = "mp3",
    sample_rate: Optional[int] = None,
    mp3_bitrate: int = 128,
    opus_bitrate: int = 32,
    latency: str = "normal",
) -> bytes:
    """
    Call Fish Audio's TTS API
    """
    config = get_config()
    fish_audio_config = config["external_apis"]["fish_audio"]

    url = fish_audio_config["base_url"]
    api_key = fish_audio_config["key"]
    model = fish_audio_config["model"]
    reference_id = fish_audio_config["reference_id"]

    headers = {"Authorization": f"Bearer {api_key}", "model": model}

    logger.info(f"TTS request parameters: {text}")

    payload = {
        "text": text,
        "temperature": temperature,
        "top_p": top_p,
        "normalize": False,
        "format": format,
        "latency": latency,
        "chunk_length": chunk_length,
        "sample_rate": sample_rate,
        "mp3_bitrate": mp3_bitrate,
        "opus_bitrate": opus_bitrate,
        "reference_id": reference_id,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            logger.info(f"TTS succeeded, text length: {len(text)}")
            return response.content
    except httpx.ConnectTimeout:
        logger.error("TTS API connection timed out")
        raise Exception(
            "TTS failed: Connection timed out, please check the network connection or if the API service is available"
        )
    except httpx.HTTPStatusError as e:
        logger.error(
            f"TTS API call failed: {e.response.status_code} - {e.response.text}"
        )
        raise Exception(f"TTS failed: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Error occurred during TTS: {str(e)}")
        raise Exception(f"TTS error: {str(e)}")
