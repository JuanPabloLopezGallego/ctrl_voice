import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Voice Control · MQTT",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# ESTILOS — VOICE ASSISTANT
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    :root {
        --bg:         #0B0914;
        --surface:    #151124;
        --border:     #312B4B;
        --text:       #F8FAFC;
        --muted:      #94A3B8;
        --pulse:      #8B5CF6; /* Violeta */
        --pulse-glow: rgba(139, 92, 246, 0.4);
        --success:    #10B981;
    }

    html, body, [class*="css"], .stApp, button, input, textarea {
        font-family: 'Inter', sans-serif !important;
        color: var(--text) !important;
    }

    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    /* ═══ FONDO ═══ */
    .stApp {
        background-color: var(--bg) !important;
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(139, 92, 246, 0.15) 0%, transparent 60%),
            radial-gradient(circle at 50% 100%, rgba(56, 189, 248, 0.05) 0%, transparent 50%);
        background-attachment: fixed;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 4rem !important;
        max-width: 800px !important;
    }

    /* ═══ HERO ═══ */
    .hero {
        text-align: center;
        margin-bottom: 3rem;
    }
    .hero-kicker {
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--pulse);
        font-weight: 600;
        margin-bottom: 0.8rem;
        display: inline-block;
    }
    .hero h1 {
        font-size: 3.2rem !important;
        margin: 0 0 0.5rem 0 !important;
        background: linear-gradient(135deg, #ffffff 30%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p {
        font-size: 1.1rem;
        color: var(--muted);
        margin: 0;
    }

    /* ═══ CONTENEDOR DEL MICRÓFONO ═══ */
    .voice-container {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 3rem 2rem;
        text-align: center;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
        position: relative;
        overflow: hidden;
        margin-bottom: 2rem;
    }
    
    /* Efecto de aura de fondo */
    .voice-container::before {
        content: '';
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 200px; height: 200px;
        background: var(--pulse);
        filter: blur(80px);
        opacity: 0.15;
        z-index: 0;
        border-radius: 50%;
    }

    .voice-container > * {
        position: relative;
        z-index: 1;
    }

    /* Imagen del micrófono */
    [data-testid="stImage"] img {
        border-radius: 50% !important;
        border: 3px solid var(--border);
        box-shadow: 0 0 30px var(--pulse-glow);
        object-fit: cover;
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }
    [data-testid="stImage"] img:hover {
        border-color: var(--pulse);
        box-shadow: 0 0 50px var(--pulse-glow);
    }

    /* Instrucción */
    .instruction {
        font-size: 1.05rem;
        color: var(--text);
        font-weight: 500;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    /* Estilo del botón Bokeh (Aplicado al iframe contenedor) */
    iframe[title="bokeh"] {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2);
        border: 1px solid var(--border);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    iframe[title="bokeh"]:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
        border-color: var(--pulse);
    }

    /* ═══ RESULTADOS DE LA TRANSCRIPCIÓN ═══ */
    .result-box {
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 4px solid var(--success);
        border-radius: 0 12px 12px 0;
        padding: 1.5rem;
        margin-top: 1rem;
        animation: slideIn 0.4s ease-out;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .result-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--success);
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .result-text {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 1rem;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(16, 185, 129, 0.1);
        color: var(--success);
        padding: 0.4rem 0.8rem;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .status-badge svg {
        width: 14px; height: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# LÓGICA MQTT (Intacta)
# ═══════════════════════════════════════════════════════════════
def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message


# ═══════════════════════════════════════════════════════════════
# INTERFAZ DE USUARIO
# ═══════════════════════════════════════════════════════════════

# Hero Header
st.markdown("""
    <div class="hero">
        <span class="hero-kicker">Interfaces Multimodales</span>
        <h1>Control por Voz</h1>
        <p>Habla y deja que la magia suceda</p>
    </div>
""", unsafe_allow_html=True)

# Contenedor Central (Micrófono y Botón)
st.markdown('<div class="voice-container">', unsafe_allow_html=True)

try:
    image = Image.open('voice_ctrl.jpg')
    # Reducimos un poco el tamaño para que no ocupe toda la pantalla
    st.image(image, width=180)
except Exception:
    # Fallback por si no encuentran la imagen
    st.markdown('<div style="font-size: 5rem; margin-bottom: 1rem;">🎙️</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="instruction">
        <span>👉</span> Toca el botón y comienza a hablar
    </div>
""", unsafe_allow_html=True)

# Botón de Bokeh (Lógica intacta)
stt_button = Button(label="🎤 Iniciar Escucha", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

st.markdown('</div>', unsafe_allow_html=True) # Cierre voice-container


# ═══════════════════════════════════════════════════════════════
# RESULTADOS Y PUBLICACIÓN MQTT
# ═══════════════════════════════════════════════════════════════
if result:
    if "GET_TEXT" in result:
        texto_capturado = result.get("GET_TEXT").strip()
        
        # 1. Conectar y publicar en MQTT
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": texto_capturado})
        ret = client1.publish("voice_ctrl", message)
        
        # 2. Mostrar el resultado en la interfaz con diseño
        st.markdown(f"""
            <div class="result-box">
                <div class="result-label">Texto Reconocido</div>
                <div class="result-text">"{texto_capturado}"</div>
                <div class="status-badge">
                    <svg fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path></svg>
                    Enviado por MQTT
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Mantener la lógica original de creación de carpetas por si acaso se usa luego
    try:
        os.mkdir("temp")
    except:
        pass
