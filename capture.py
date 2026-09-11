import io
import mss
import mss.tools
from PIL import Image

class CaptureError(Exception):
    """Custom exception raised when screen capture fails."""
    pass

def capture_screen_bytes(max_dimension: int = 1600) -> bytes:
    """
    Captures the primary monitor directly into memory.
    Tries mss first, and falls back to PIL ImageGrab.
    Resizes image optionally if max_dimension is exceeded to keep request payload light.
    Returns PNG formatted image bytes.
    
    Zero focus theft: Does not open any window or change active foreground application.
    """
    img = None
    
    # Primary Method: mss
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    except Exception as mss_err:
        # Fallback Method: PIL ImageGrab
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab(all_screens=True)
            if img:
                img = img.convert("RGB")
        except Exception as grab_err:
            raise CaptureError(
                f"No se pudo capturar la pantalla (mss: {mss_err}, ImageGrab: {grab_err}). "
                "Asegúrese de estar ejecutando la aplicación en una sesión gráfica interactiva de Windows."
            ) from grab_err

    if img is None:
        raise CaptureError("Captura vacía. Asegúrese de que la pantalla esté activa.")

    try:
        # Resize if necessary to save bandwidth and speed up AI inference
        width, height = img.size
        if max(width, height) > max_dimension:
            scale = max_dimension / float(max(width, height))
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()
    except Exception as e:
        raise CaptureError(f"Error procesando la captura: {str(e)}") from e

