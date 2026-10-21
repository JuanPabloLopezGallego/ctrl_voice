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
# ESTILOS — SMART HOME / GLASSMORPHISM
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    :root {
        --bg:         #09090B;
        --glass:      rgba(24, 24, 27, 0.6);
        --border:     rgba(255, 255, 255, 0.1);
        --text:       #FAFAFA;
        --muted:      #A1A1AA;
        --accent:     #8B5CF6; /* Violeta */
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
            radial-gradient(circle at 50% -10%, rgba(139, 92, 246, 0.2) 0%, transparent 60%),
            radial-gradient(circle at 50% 110%, rgba(16, 185, 129, 0.1) 0%, transparent 60%);
        background-attachment: fixed;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
        max-width: 700px !important;
    }

    /* ═══ TÍTULOS ═══ */
    .hero {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    .hero-kicker {
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--accent);
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: block;
    }
    .hero h1 {
        font-size: 3rem !important;
        margin: 0 0 0.5rem 0 !important;
    }
    .hero p {
        font-size: 1.05rem;
        color: var(--muted);
        margin: 0;
    }

    /* ═══ TARJETA PRINCIPAL (Glassmorphism) ═══ */
    .control-card {
        background: var(--glass);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 3rem 2rem 2rem 2rem;
        text-align: center;
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.7);
        position: relative;
        overflow: hidden;
    }
    
    /* Aura de fondo dentro de la tarjeta */
    .control-card::before {
        content: '';
        position: absolute;
        top: -50px; left: 50%;
        transform: translateX(-50%);
        width: 200px; height: 200px;
        background: var(--accent);
        filter: blur(80px);
        opacity: 0.3;
        z-index: 0;
        border-radius: 50%;
    }
    .control-card > * {
        position: relative;
        z-index: 1;
    }

    /* ═══ IMAGEN CIRCULAR PERFECTA ═══ */
    /* Forzamos la imagen a ser un círculo perfecto, sin importar si es rectangular */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
    }
    [data-testid="stImage"] img {
        width: 160px !important;
        height: 160px !important;
        object-fit: cover !important;
        border-radius: 50% !important;
        clip-path: circle(50% at 50% 50%);
        border: 4px solid var(--accent);
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.4);
        transition: all 0.3s ease;
    }
    [data-testid="stImage"] img:hover {
        transform: scale(1.05);
        box-shadow: 0 0 50px rgba(139, 92, 246, 0.7);
    }

    /* ═══ INSTRUCCIÓN ═══ */
    .instruction {
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--text);
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    /* ═══ EL IFRAME DE BOKEH ═══ */
    /* Hacemos que el iframe sea transparente y se fusione con la tarjeta */
    iframe[title="bokeh"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 12px;
        display: block;
        margin: 0 auto;
    }

    /* ═══ RESULTADO ═══ */
    .result-card {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        text-align: left;
        animation: fadeIn 0.4s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .result-header {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--success);
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .result-text {
        font-size: 1.3rem;
        font-weight: 600;
        color: #fff;
        font-style: italic;
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

st.markdown("""
    <div class="hero">
        <span class="hero-kicker">Interfaces Multimodales</span>
        <h1>Control por Voz</h1>
        <p>Habla y deja que la magia suceda</p>
    </div>
""", unsafe_allow_html=True)

# Abrimos la tarjeta de control
st.markdown('<div class="control-card">', unsafe_allow_html=True)

# Imagen del micrófono (con fallback si no existe)
try:
    image = Image.open('voice_ctrl.jpg')
    st.image(image)
except Exception:
    st.markdown('<div style="font-size: 6rem; margin-bottom: 1rem; text-align: center;">🎙️</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="instruction">
        <span>👇</span> Toca el botón y comienza a hablar
    </div>
""", unsafe_allow_html=True)

# Botón de Bokeh (Usamos button_type="success" para que sea verde sólido nativo)
stt_button = Button(
    label="🎤 Iniciar Escucha", 
    width=200, 
    height=50, 
    button_type="success", # Esto hace que el botón sea verde sólido
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

# Componente de eventos de Bokeh
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    debounce_time=0
)

st.markdown('</div>', unsafe_allow_html=True) # Cerramos la tarjeta de control


# ═══════════════════════════════════════════════════════════════
# MANEJO DE RESULTADOS
# ═══════════════════════════════════════════════════════════════
if result:
    if "GET_TEXT" in result:
        texto_capturado = result.get("GET_TEXT").strip()
        
        # 1. Publicar a MQTT
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": texto_capturado})
        client1.publish("voice_ctrl", message)
        
        # 2. Mostrar Tarjeta de Éxito
        st.markdown(f"""
            <div class="result-card">
                <div class="result-header">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    Enviado a MQTT con éxito
                </div>
                <div class="result-text">"{texto_capturado}"</div>
            </div>
        """, unsafe_allow_html=True)

    # Mantener la lógica original
    try:
        os.mkdir("temp")
    except:
        pass
