import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import time
import paho.mqtt.client as paho
import json

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="MQTT Voice Control",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# ESTILOS — CYBERPUNK TERMINAL
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

    :root {
        --bg:         #050505;
        --surface:    #111111;
        --border:     #333333;
        --text:       #EDEDED;
        --muted:      #888888;
        --neon:       #00FF41; /* Verde Matrix */
        --neon-glow:  rgba(0, 255, 65, 0.3);
    }

    html, body, [class*="css"], .stApp, button, input, textarea {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text) !important;
    }

    /* ═══ FONDO ═══ */
    .stApp {
        background-color: var(--bg) !important;
        background-image: 
            linear-gradient(rgba(0, 255, 65, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 65, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
        background-attachment: fixed;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        max-width: 650px !important;
    }

    /* ═══ HEADER ═══ */
    .hero {
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #fff !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.2);
    }
    .hero p {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: var(--neon);
        margin: 0;
    }

    /* ═══ TARJETA DE INSTRUCCIONES ═══ */
    .instructions {
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 3px solid var(--neon);
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin-bottom: 2rem;
        font-size: 0.9rem;
        color: var(--muted);
        line-height: 1.6;
    }
    .instructions b {
        color: var(--text);
    }

    /* ═══ CONTENEDOR DEL BOTÓN (Oculta el fondo blanco de Bokeh) ═══ */
    .button-wrapper {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        box-shadow: 0 0 40px rgba(0,0,0,0.8), inset 0 0 20px rgba(0, 255, 65, 0.05);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    /* Línea superior decorativa */
    .button-wrapper::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--neon), transparent);
    }

    /* Estilo para el iframe de Bokeh */
    iframe[title="bokeh"] {
        background-color: transparent !important;
        border: none !important;
        width: 100% !important;
        height: 80px !important;
        overflow: hidden !important;
        margin: 0 auto;
        display: block;
    }

    /* ═══ TERMINAL DE RESULTADOS ═══ */
    .terminal-box {
        background: #000000;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 1.5rem;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 2rem;
        position: relative;
    }
    .terminal-header {
        display: flex;
        gap: 6px;
        margin-bottom: 1rem;
    }
    .dot { width: 10px; height: 10px; border-radius: 50%; }
    .dot.r { background: #FF5F56; }
    .dot.y { background: #FFBD2E; }
    .dot.g { background: #27C93F; }
    
    .terminal-output {
        font-size: 1.2rem;
        color: var(--neon);
        word-wrap: break-word;
    }
    .terminal-prompt {
        color: #fff;
        margin-right: 8px;
    }

    /* ═══ FOOTER (METADATOS) ═══ */
    .footer-metadata {
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--muted);
        border-top: 1px solid var(--border);
        padding-top: 1.5rem;
        margin-top: 2rem;
        letter-spacing: 0.05em;
    }
    .footer-metadata b {
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# LÓGICA MQTT (Intacta)
# ═══════════════════════════════════════════════════════════════
def on_publish(client, userdata, result):
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
# INTERFAZ GRÁFICA
# ═══════════════════════════════════════════════════════════════

# 1. Header
st.markdown("""
    <div class="hero">
        <h1>Voice Control</h1>
        <p>SISTEMA DE RECONOCIMIENTO MULTIMODAL</p>
    </div>
""", unsafe_allow_html=True)

# 2. Instrucciones (Funcionalidad)
st.markdown("""
    <div class="instructions">
        <b>¿Cómo funciona?</b><br>
        Presiona el botón inferior, permite el acceso al micrófono y habla claramente.
        El sistema transcribirá tu voz y enviará el texto mediante el protocolo MQTT al tópico <code>voice_ctrl</code>.
    </div>
""", unsafe_allow_html=True)

# 3. Contenedor del Botón
st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)

# Creamos el botón de Bokeh con estilo nativo verde y texto oscuro
stt_button = Button(
    label="🎤 PRESIONAR PARA HABLAR", 
    width=350, 
    height=60, 
    button_type="success", # Botón verde sólido
    margin=(10, 10, 10, 10)
)

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

# Renderizar el componente
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    debounce_time=0
)

st.markdown('</div>', unsafe_allow_html=True) # Cierre button-wrapper


# 4. Terminal de Resultados
if result and "GET_TEXT" in result:
    texto_capturado = result.get("GET_TEXT").strip()
    
    # Publicar a MQTT
    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Act1": texto_capturado})
    client1.publish("voice_ctrl", message)
    
    # Mostrar en la terminal
    st.markdown(f"""
        <div class="terminal-box">
            <div class="terminal-header">
                <div class="dot r"></div>
                <div class="dot y"></div>
                <div class="dot g"></div>
            </div>
            <div class="terminal-output">
                <span class="terminal-prompt">user@mqtt:~$</span> {texto_capturado}
            </div>
            <div style="margin-top: 1rem; font-size: 0.8rem; color: #888;">
                > Mensaje publicado en el tópico "voice_ctrl"
            </div>
        </div>
    """, unsafe_allow_html=True)

# Mantener lógica de creación de carpeta
try:
    os.mkdir("temp")
except:
    pass


# 5. Footer (Tus datos)
st.markdown("""
    <div class="footer-metadata">
        <b>Juan Pablo</b> · Universidad EAFIT<br>
        Interfaces Multimodales · 2026
    </div>
""", unsafe_allow_html=True)
