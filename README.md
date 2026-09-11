# Screen AI - Windows Background Assistant 🚀

Aplicación ligera de escritorio para Windows desarrollada en Python. Se ejecuta silenciosamente en segundo plano (System Tray) y permite capturar la pantalla actual con un atajo global (`Ctrl + Alt + X`), analizarla con una API de IA con visión (Google Gemini u OpenAI) y mostrar el análisis mediante una notificación nativa de Windows disfrazada de actualización del sistema que desaparece en **2 segundos** sin robar el foco de la ventana activa ("sin rastro").

---

## 🎯 Características Principales

- **Segundo Plano (System Tray)**: Icono discreto en la bandeja del sistema usando `pystray`.
- **Atajo Global (`Ctrl + Alt + X`)**: Funciona desde cualquier aplicación activa sin necesidad de foco.
- **Sin Robo de Foco**: Captura directa en memoria mediante `mss` y notificación nativa Windows. No abre ventanas, no activa Alt+Tab ni interrumpe lo que estés haciendo.
- **Notificación Disfrazada & Efímera ("Sin Rastro")**:
  - Título predeterminado: **`Windows Software Update`**.
  - Duración automática: **Máximo 2 segundos** antes de desaparecer de la pantalla y del centro de actividades.
- **Visión Multimodal (Gemini / OpenAI)**: Soporta Google Gemini (gratis/rápido) u OpenAI (GPT-4o / GPT-4o-mini).
- **Manejo de Errores Integrado**: Notifica problemas de conexión, API keys faltantes o fallos de captura sin interrumpir el flujo.

---

## 📁 Estructura del Proyecto

```
screen_ai/
├── app.py              # Punto de entrada principal y System Tray (pystray + pynput)
├── capture.py          # Captura de pantalla en memoria con mss
├── ai_client.py        # Cliente HTTP para Gemini u OpenAI Vision API
├── notifier.py         # Notificaciones nativas sigilosas de Windows (auto-cierre en 2s)
├── config.py           # Carga y validación de variables de entorno (.env)
├── requirements.txt    # Dependencias de Python
├── .env.example        # Plantilla de variables de entorno
├── .env                # Configuración local (API Keys)
└── README.md           # Instrucciones de uso
```

---

## 🛠️ Requisitos Previos

- Windows 10 o Windows 11.
- Python 3.9 o superior instalado.

---

## 🚀 Guía de Instalación y Configuración

### 1. Clonar / Navegar a la carpeta del proyecto

```bash
cd screen_ai
```

### 2. Crear el Entorno Virtual (venv)

```powershell
python -m venv venv
```

### 3. Activar el Entorno Virtual

En PowerShell:
```powershell
.\venv\Scripts\activate
```

En CMD:
```cmd
venv\Scripts\activate.bat
```

### 4. Instalar las Dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar la API Key (.env)

Abre el archivo `.env` en tu editor de código o bloc de notas y añade tu clave API:

#### Opción A: Google Gemini (Recomendado / Gratuito)
1. Consigue tu clave API en [Google AI Studio](https://aistudio.google.com/).
2. Edita `.env`:
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
MODEL_NAME=gemini-2.0-flash
```

#### Opción B: OpenAI
1. Consigue tu clave API en [OpenAI Platform](https://platform.openai.com/api-keys).
2. Edita `.env`:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=tu_api_key_de_openai_aqui
MODEL_NAME=gpt-4o-mini
```

---

## 💻 Ejecución de la Aplicación

Para iniciar la aplicación en segundo plano:

```bash
python app.py
```

Al iniciar:
1. Verás una confirmación en la consola y la aplicación se minimizará al System Tray (bandeja de entrada al lado del reloj de Windows).
2. Mantén activa cualquier ventana (navegador, código, documentos).
3. Presiona el atajo **`Ctrl + Alt + X`**.
4. La captura se procesará e instantáneamente recibirás una notificación titulada **`Windows Software Update`** con la respuesta breve de la IA.
5. La notificación desaparecerá automáticamente en **2 segundos**.

---

## ⚙️ Personalización Adicional en `.env`

- **Cambiar Atajo de Teclado**: `HOTKEY=<ctrl>+<alt>+s`
- **Cambiar Prompt de la IA**: `PROMPT=Resume el texto visible en la pantalla`
- **Cambiar Título de Notificación**: `NOTIFICATION_TITLE=Windows Security Update`
- **Cambiar Duración de Notificación**: `NOTIFICATION_DURATION=2`

---

## 🛑 Salir de la Aplicación

Haz clic derecho sobre el icono en la bandeja del sistema (System Tray) y selecciona **Salir**.
