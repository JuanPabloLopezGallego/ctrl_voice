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
    page_title="Voice Control · Juan Pablo",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# ESTILOS — LIGHT MODE / CLEAN UI
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    :root {
        --bg:         #F3F4F6;
        --surface:    #FFFFFF;
        --border:     #E5E7EB;
        --text:       #111827;
        --muted:      #6B7280;
        --primary:    #4F46E5; /* Índigo */
        --primary-lt: #EEF2FF;
        --success:    #10B981;
        --success-bg: #ECFDF5;
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
        background-image: radial-gradient(circle at 50% 0%, #ffffff 0%, transparent 70%);
        background-attachment: fixed;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 2rem !important;
        max-width: 650px !important;
    }

    /* ═══ HEADER ═══ */
    .hero {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    .hero h1 {
        font-size: 3rem !important;
        color: var(--text) !important;
        margin: 0 0 0.5rem 0 !important;
    }
    .hero p {
        font-size: 1.05rem;
        color: var(--muted);
        margin: 0;
        font-weight: 500;
    }

    /* ═══ TARJETA PRINCIPAL (BLANCA) ═══ */
    .main-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 10px 30px -5px rgba(0,0,0,0.05), 0 4px 6px -2px rgba(0,0,0,0.02);
        margin-bottom: 2rem;
        position: relative;
    }

    /* Instrucciones */
    .instructions {
        font-size: 0.95rem;
        color: var(--muted);
        line-height: 1.6;
        margin-bottom: 2rem;
        padding: 0 1rem;
    }
    .instructions b {
        color: var(--text);
    }

    /* ═══ FIX IFRAME BOKEH (Ahora se funde con la tarjeta blanca) ═══ */
    iframe[title="streamlit_bokeh_events.streamlit_bokeh_events"] {
        background-color: transparent !important;
        border: none !important;
        width: 100% !important;
        height: 80px !important;
        display: block;
        margin: 0 auto;
    }
    div[data-testid="stCustomComponentV1"] {
        background-color: transparent !important;
    }

    /* ═══ TARJETA DE RESULTADOS ═══ */
    .result-card {
        background: var(--success-bg);
        border: 1px solid #A7F3D0;
        border-left: 4px solid var(--success);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .result-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #047857;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .result-text {
        font-size: 1.25rem;
        font-weight: 500;
        color: #064E3B;
        font-style: italic;
    }

    /* ═══ FOOTER METADATOS ═══ */
    .footer-meta {
        text-align: center;
        border-top: 1px solid var(--border);
        padding-top: 1.5rem;
        margin-top: 3rem;
    }
    .footer-meta .author {
        font-family: 'Outfit', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 0.2rem;
    }
    .footer-meta .details {
        font-size: 0.8rem;
        color: var(--muted);
        letter-spacing: 0.05em;
        text-transform: uppercase;
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
        <h1>Control por Voz</h1>
        <p>Interfaces Multimodales · EAFIT</p>
    </div>
""", unsafe_allow_html=True)

# 2. Tarjeta Principal
st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.markdown("""
    <div class="instructions">
        <b>¿Cómo funciona?</b><br>
        Presiona el botón, permite el acceso al micrófono y habla claramente. 
        El sistema transcribirá tu voz y enviará el texto vía MQTT.
    </div>
""", unsafe_allow_html=True)

# Botón de Bokeh
stt_button = Button(
    label="🎤 Iniciar Escucha", 
    width=280, 
    height=60, 
    button_type="primary", 
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

# Componente Bokeh (con altura forzada para ocultar fondo)
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=80, 
    debounce_time=0
)

st.markdown('</div>', unsafe_allow_html=True) # Cierre main-card

# 3. Resultados
if result and "GET_TEXT" in result:
    texto_capturado = result.get("GET_TEXT").strip()
    
    # Publicar a MQTT
    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Act1": texto_capturado})
    client1.publish("voice_ctrl", message)
    
    # Mostrar tarjeta elegante
    st.markdown(f"""
        <div class="result-card">
            <div class="result-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                Enviado a MQTT
            </div>
            <div class="result-text">"{texto_capturado}"</div>
        </div>
    """, unsafe_allow_html=True)

# Mantener lógica original
try:
    os.mkdir("temp")
except:
    pass

# 4. Footer (Tus Datos)
st.markdown("""
    <div class="footer-meta">
        <div class="author">Juan Pablo</div>
        <div class="details">Universidad EAFIT · 2026</div>
    </div>
""", unsafe_allow_html=True)
