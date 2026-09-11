import base64
import httpx
from config import Config

class AIClientError(Exception):
    """Base exception for AI Client errors."""
    pass

class NoConnectionError(AIClientError):
    """Raised when there is no internet connection or a timeout occurs."""
    pass

class ApiKeyMissingError(AIClientError):
    """Raised when an API key is missing or empty."""
    pass

class ApiResponseError(AIClientError):
    """Raised when the AI API returns an error response."""
    pass

def analyze_image(image_bytes: bytes, prompt: str = None) -> str:
    """
    Sends the PNG image bytes to the configured AI Vision API (Gemini or OpenAI).
    Returns the textual analysis response.
    
    Raises:
        ApiKeyMissingError: If no API key is set.
        NoConnectionError: On network unreachable or timeout.
        ApiResponseError: On API HTTP errors (invalid key, rate limit, quota, etc).
    """
    try:
        provider = Config.validate()
    except ValueError as err:
        raise ApiKeyMissingError(str(err)) from err

    if not prompt:
        prompt = Config.PROMPT

    base64_img = base64.b64encode(image_bytes).decode("utf-8")

    if provider == "gemini":
        return _call_gemini_api(base64_img, prompt)
    elif provider == "openai":
        return _call_openai_api(base64_img, prompt)
    else:
        raise AIClientError(f"Proveedor no soportado: {provider}")

def _call_gemini_api(base64_img: str, prompt: str) -> str:
    api_key = Config.GEMINI_API_KEY
    model = Config.MODEL_NAME or "gemini-3.6-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": base64_img
                        }
                    }
                ]
            }
        ]
    }

    try:
        with httpx.Client(timeout=20.0) as client:
            res = client.post(url, json=payload)
    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
        raise NoConnectionError("Sin conexión a internet. Verifique su red.") from e
    except Exception as e:
        raise AIClientError(f"Error de red inesperado: {str(e)}") from e

    if res.status_code != 200:
        error_msg = f"Error de API Gemini (HTTP {res.status_code})"
        try:
            err_json = res.json()
            if "error" in err_json and "message" in err_json["error"]:
                error_msg += f": {err_json['error']['message']}"
        except Exception:
            pass
        raise ApiResponseError(error_msg)

    try:
        data = res.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return "La IA no devolvió ningún contenido."
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return "Respuesta vacía de la IA."
        return parts[0].get("text", "").strip()
    except Exception as e:
        raise ApiResponseError(f"Error procesando la respuesta de Gemini: {str(e)}") from e

def _call_openai_api(base64_img: str, prompt: str) -> str:
    api_key = Config.OPENAI_API_KEY
    model = Config.MODEL_NAME or "gpt-4o-mini"
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_img}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    try:
        with httpx.Client(timeout=20.0) as client:
            res = client.post(url, headers=headers, json=payload)
    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
        raise NoConnectionError("Sin conexión a internet. Verifique su red.") from e
    except Exception as e:
        raise AIClientError(f"Error de red inesperado: {str(e)}") from e

    if res.status_code != 200:
        error_msg = f"Error de API OpenAI (HTTP {res.status_code})"
        try:
            err_json = res.json()
            if "error" in err_json and "message" in err_json["error"]:
                error_msg += f": {err_json['error']['message']}"
        except Exception:
            pass
        raise ApiResponseError(error_msg)

    try:
        data = res.json()
        choices = data.get("choices", [])
        if not choices:
            return "La IA no devolvió ningún contenido."
        return choices[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        raise ApiResponseError(f"Error procesando la respuesta de OpenAI: {str(e)}") from e
