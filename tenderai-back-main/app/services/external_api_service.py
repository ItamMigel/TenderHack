import httpx
from fastapi import HTTPException
from app.app_config import settings

async def call_external_api(prompt: str, settings: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.EXTERNAL_API_URL,
                json={
                    "prompt": prompt,
                    "settings": settings
                },
                timeout=30.0  # Таймаут 30 секунд
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="External API request timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))