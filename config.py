import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root directory
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    
    # Provider & Model selection ("gemini", "openai", or "auto")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").strip().lower()
    MODEL_NAME = os.getenv("MODEL_NAME", "").strip()
    
    # Hotkey string (pynput format)
    HOTKEY = os.getenv("HOTKEY", "<ctrl>+<alt>+x").strip()
    
    # Prompt for Vision AI
    PROMPT = os.getenv(
        "PROMPT", 
        "Analiza el contenido de esta captura de pantalla y responde de forma breve, clara y concisa en español."
    ).strip()
    
    # Stealth Notification Settings
    NOTIFICATION_TITLE = os.getenv("NOTIFICATION_TITLE", "Windows Software Update").strip()
    NOTIFICATION_DURATION = int(os.getenv("NOTIFICATION_DURATION", "2"))

    @classmethod
    def validate(cls):
        """
        Validates configured keys and sets active provider & model defaults.
        Returns active provider name ('gemini' or 'openai').
        Raises ValueError if no valid API key is present.
        """
        provider = cls.AI_PROVIDER
        
        if provider == "auto":
            if cls.GEMINI_API_KEY:
                provider = "gemini"
            elif cls.OPENAI_API_KEY:
                provider = "openai"
            else:
                raise ValueError("No API Key configured. Please set GEMINI_API_KEY or OPENAI_API_KEY in .env")

        if provider == "gemini":
            if not cls.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is missing in .env")
            if not cls.MODEL_NAME:
                cls.MODEL_NAME = "gemini-3.6-flash"
        elif provider == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is missing in .env")
            if not cls.MODEL_NAME:
                cls.MODEL_NAME = "gpt-4o-mini"
        else:
            raise ValueError(f"Unsupported AI_PROVIDER: {provider}. Use 'gemini' or 'openai'.")

        return provider
