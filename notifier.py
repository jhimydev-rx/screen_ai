import time
import threading
import subprocess
from winotify import Notification
from config import Config

class NotifierError(Exception):
    """Custom exception for notification failures."""
    pass

def _auto_dismiss_toast(app_id: str):
    """
    Clears the notification from screen and Action Center after duration using WinRT.
    Leaves no trace in the notification history ("sin rastro").
    """
    try:
        ps_script = (
            f'[void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]; '
            f'[Windows.UI.Notifications.ToastNotificationManager]::History.Clear("{app_id}")'
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
    except Exception:
        pass  # Non-critical background cleanup task

def show_notification(
    title: str = None, 
    message: str = "", 
    duration: int = None,
    icon: str = ""
):
    """
    Displays a native Windows Toast notification.
    - Zero focus theft: Appears in bottom right corner without activating or stealing window focus.
    - Disguised title: Defaults to 'Windows Software Update' (stealth).
    - Auto-dismissal: Auto-dismisses after 2 seconds ("sin rastro").
    """
    if title is None:
        title = Config.NOTIFICATION_TITLE
    if duration is None:
        duration = Config.NOTIFICATION_DURATION

    # Clean message text
    message_text = str(message).strip()
    if len(message_text) > 300:
        message_text = message_text[:297] + "..."

    try:
        toast = Notification(
            app_id=title,
            title=title,
            msg=message_text,
            duration="short"
        )
        
        if icon:
            toast.set_audio(Notification.AUDIO_NONE, loop=False)

        # Show notification (non-blocking, zero focus theft)
        toast.show()

        # Schedule auto-dismissal after `duration` seconds
        if duration > 0:
            dismiss_timer = threading.Timer(duration, _auto_dismiss_toast, args=(title,))
            dismiss_timer.daemon = True
            dismiss_timer.start()

    except Exception as e:
        raise NotifierError(f"Error al mostrar la notificación: {str(e)}") from e
