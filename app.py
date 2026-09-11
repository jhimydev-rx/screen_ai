import sys
import threading
from datetime import datetime
import pystray
from PIL import Image, ImageDraw
from pynput import keyboard

from config import Config
from capture import capture_screen_bytes, CaptureError
from ai_client import (
    analyze_image, 
    ApiKeyMissingError, 
    NoConnectionError, 
    ApiResponseError, 
    AIClientError
)
from notifier import show_notification, NotifierError

# Global flag to prevent concurrent execution of hotkey actions
_processing_lock = threading.Lock()

def create_tray_icon() -> Image.Image:
    """
    Creates a simple, clean 64x64 PIL Image icon for the System Tray.
    """
    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Outer circle (Dark blue / metallic look)
    draw.ellipse((4, 4, size - 4, size - 4), fill=(30, 41, 59, 255), outline=(71, 85, 105, 255), width=2)
    # Inner lens accent (Cyan / AI glow)
    draw.ellipse((20, 20, size - 20, size - 20), fill=(14, 165, 233, 255))
    # Center dot
    draw.ellipse((28, 28, size - 28, size - 28), fill=(255, 255, 255, 255))
    
    return image

def process_screen_ai_task():
    """
    Background worker thread function triggered by global hotkey or tray menu.
    Flow: Capture -> AI Analysis -> Disguised Toast Notification.
    Zero focus theft throughout execution.
    """
    if not _processing_lock.acquire(blocking=False):
        print("[!] Proceso en marcha. Ignorando solicitud duplicada.")
        return

    timestamp = datetime.now().strftime("%H:%M:%S")

    try:
        print(f"\n[{timestamp}] [ATAJO DETECTADO] Iniciando captura de pantalla...")

        # Step 1: Capture current screen
        try:
            image_bytes = capture_screen_bytes()
            print(f"[{timestamp}] [CAPTURA] Pantalla capturada en memoria ({len(image_bytes)} bytes).")
        except Exception as e:
            err_msg = f"Captura fallida: {e}"
            print(f"[{timestamp}] [CAPTURA ERROR] {err_msg}")
            show_notification(message=err_msg)
            return

        # Step 2: Send image to AI Vision API
        provider_info = f"{Config.AI_PROVIDER} ({Config.MODEL_NAME})"
        print(f"[{timestamp}] [IA] Enviando imagen a API {provider_info}...")

        try:
            ai_response = analyze_image(image_bytes)
            print(f"[{timestamp}] [RESPUESTA IA] {ai_response}")
        except ApiKeyMissingError as e:
            err_msg = f"Configuracion: {e}"
            print(f"[{timestamp}] [CONFIG ERROR] {err_msg}")
            show_notification(message=err_msg)
            return
        except NoConnectionError as e:
            err_msg = f"Red: {e}"
            print(f"[{timestamp}] [RED ERROR] {err_msg}")
            show_notification(message=err_msg)
            return
        except ApiResponseError as e:
            err_msg = f"API Error: {e}"
            print(f"[{timestamp}] [API ERROR] {err_msg}")
            show_notification(message=err_msg)
            return
        except AIClientError as e:
            err_msg = f"Error IA: {e}"
            print(f"[{timestamp}] [IA ERROR] {err_msg}")
            show_notification(message=err_msg)
            return
        except Exception as e:
            err_msg = f"Error inesperado de IA: {e}"
            print(f"[{timestamp}] [ERROR] {err_msg}")
            show_notification(message=err_msg)
            return

        # Step 3: Display AI response via disguised Toast Notification
        print(f"[{timestamp}] [NOTIFICACION] Mostrando notificacion sigilosa '{Config.NOTIFICATION_TITLE}'...")
        show_notification(message=ai_response)
        print(f"[{timestamp}] [EXITO] Notificacion enviada. Desaparecera en {Config.NOTIFICATION_DURATION}s.")

    except NotifierError as e:
        print(f"[{timestamp}] [NOTIFIER ERROR] {e}", file=sys.stderr)
    except Exception as e:
        print(f"[{timestamp}] [ERROR GENERAL] {e}", file=sys.stderr)
    finally:
        _processing_lock.release()

def on_hotkey_triggered():
    """
    Callback when global hotkey is detected.
    Spawns background thread so hotkey listener remains responsive.
    """
    worker = threading.Thread(target=process_screen_ai_task, daemon=True)
    worker.start()

def main():
    print("=" * 65)
    print("  Screen AI - Windows Background Assistant")
    print(f"  Atajo registrado : {Config.HOTKEY}")
    print(f"  Proveedor de IA  : {Config.AI_PROVIDER} ({Config.MODEL_NAME})")
    print(f"  Disfraz Notificacion : '{Config.NOTIFICATION_TITLE}'")
    print("  Minimizado en System Tray. Presione Ctrl+Alt+X para procesar.")
    print("=" * 65)

    # Initialize hotkey listener
    hotkey_str = Config.HOTKEY
    try:
        hotkeys_dict = {hotkey_str: on_hotkey_triggered}
        listener = keyboard.GlobalHotKeys(hotkeys_dict)
        listener.start()
        print(f"[OK] Atajo global {hotkey_str} registrado correctamente.")
    except Exception as e:
        print(f"[WARNING] No se pudo registrar el atajo '{hotkey_str}': {e}")
        print("Continuando solo con menu de System Tray...")
        listener = None

    # Define Tray Menu
    def on_quit(icon_item, item):
        if listener:
            listener.stop()
        icon_item.stop()
        print("Aplicacion finalizada.")

    def on_manual_capture(icon_item, item):
        on_hotkey_triggered()

    menu = pystray.Menu(
        pystray.MenuItem("Screen AI Assistant", None, enabled=False),
        pystray.MenuItem(f"Capturar ({Config.HOTKEY})", on_manual_capture),
        pystray.MenuItem("Estado: Ejecutando en segundo plano", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Salir", on_quit)
    )

    icon_img = create_tray_icon()
    icon = pystray.Icon("screen_ai", icon_img, "Windows Software Update", menu)
    
    try:
        icon.run()
    except KeyboardInterrupt:
        if listener:
            listener.stop()
        icon.stop()

if __name__ == "__main__":
    main()
