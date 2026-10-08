import io
from time import perf_counter
from datetime import datetime
from gtts import gTTS
import ollama
from skills import execute_skill
import speech_recognition as sr
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Voice Virtual Assistant",
    layout="wide",
)

# Custom CSS for clean, modern aesthetic
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #888888;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .status-online {
        background-color: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .status-offline {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .metric-caption {
        font-size: 0.75rem;
        color: #888888;
        margin-top: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your AI voice assistant. Speak into the microphone or type below.",
            "audio": None,
            "latency": None,
        }
    ]

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None


# Helper: Check Ollama Connection & Available Models
@st.cache_data(ttl=10)
def check_ollama() -> tuple[bool, list[str]]:
    try:
        client = ollama.Client(host="http://localhost:11434", timeout=3)
        model_list = client.list()
        models = [m.model for m in model_list.models]
        return True, models
    except Exception:
        return False, []


# Helper: Transcribe Audio Bytes using SpeechRecognition
def transcribe_audio(audio_bytes: bytes) -> str | None:
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="en-US")
        return text.strip()
    except sr.UnknownValueError:
        return None
    except Exception as error:
        st.error(f"Speech recognition error: {error}")
        return None


# Helper: Generate TTS Audio (MP3)
def generate_speech(text: str) -> bytes | None:
    try:
        fp = io.BytesIO()
        tts = gTTS(text=text, lang="en")
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as error:
        st.warning(f"Voice synthesis error: {error}")
        return None


# Helper: Query Local Ollama LLM with multi-turn history
def query_ollama(prompt: str, model_name: str, history: list[dict] | None = None) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful voice assistant. "
                "Answer briefly in plain language, using at most three sentences."
            ),
        }
    ]

    # Include the last 8 conversation turns from history
    if history:
        for msg in history[-8:]:
            if msg.get("role") in ("user", "assistant") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": prompt})

    try:
        client = ollama.Client(host="http://localhost:11434", timeout=60)
        response = client.chat(
            model=model_name,
            messages=messages,
            think=False,
            options={"num_ctx": 2048, "num_predict": 150},
        )
        return response.message.content.strip()
    except Exception as error:
        return f"Sorry, I had trouble generating a response from the local AI model ({error})."


# Helper: Route command, execute system skills, or send to LLM
def process_command(user_query: str, model_name: str, history: list[dict] | None = None) -> tuple[str, str | None]:
    cleaned = user_query.strip().lower()

    if cleaned in ("exit", "quit", "bye", "stop"):
        return "Goodbye! Have a great day!", None
    elif cleaned in ("hello", "hey", "hi"):
        return "Hello! How can I assist you today?", None
    elif cleaned in ("time", "what is the time", "what time is it", "current time"):
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}.", None

    # Check for system automation skills (opening apps, searches, volume control)
    skill_handled, skill_response, target_url = execute_skill(user_query)
    if skill_handled and skill_response:
        return skill_response, target_url

    # Fallback to local Ollama LLM with multi-turn memory
    return query_ollama(user_query, model_name, history=history), None


# --- Sidebar ---
with st.sidebar:
    st.header("Settings & Diagnostics")

    ollama_ok, available_models = check_ollama()

    if ollama_ok:
        st.markdown(
            '<div class="status-badge status-online">Ollama: Online</div>',
            unsafe_allow_html=True,
        )
        if available_models:
            default_index = 0
            if "qwen3:1.7b" in available_models:
                default_index = available_models.index("qwen3:1.7b")
            selected_model = st.selectbox(
                "Active LLM Model",
                options=available_models,
                index=default_index,
            )
        else:
            selected_model = "qwen3:1.7b"
            st.warning("No models found in Ollama. Run: `ollama run qwen3:1.7b`")
    else:
        st.markdown(
            '<div class="status-badge status-offline">Ollama: Offline</div>',
            unsafe_allow_html=True,
        )
        st.error("Ollama is not running locally at http://localhost:11434.")
        selected_model = "qwen3:1.7b"

    enable_voice_reply = st.toggle("Voice Audio Output", value=True)

    st.divider()

    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Conversation cleared. How can I help you?",
                "audio": None,
                "latency": None,
                "url": None,
            }
        ]
        st.session_state.last_processed_audio = None
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        **Pipeline:**
        1. Voice recorded in browser via `st.audio_input`.
        2. Transcribed via Google Speech Recognition.
        3. Local Ollama LLM (`qwen3:1.7b`) generates response.
        4. Audio synthesized with `gTTS` and played back.
        """
    )


# --- Main Application Area ---
st.markdown('<div class="main-title">Voice Virtual Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Powered by Streamlit, SpeechRecognition, and Local Ollama</div>', unsafe_allow_html=True)

col_chat, col_audio = st.columns([2.5, 1.2], gap="large")

with col_audio:
    st.subheader("Voice Recording")
    st.caption("Click to record your voice command:")
    audio_data = st.audio_input("Record Voice Command", label_visibility="collapsed")

with col_chat:
    # Render Conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("url"):
                st.link_button("Open Link in Browser", msg["url"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/mp3")
            if msg.get("latency"):
                st.markdown(f'<div class="metric-caption">Response time: {msg["latency"]:.2f}s</div>', unsafe_allow_html=True)

    # Handle Audio Input
    if audio_data is not None:
        audio_bytes = audio_data.getvalue()
        if st.session_state.last_processed_audio != audio_bytes:
            st.session_state.last_processed_audio = audio_bytes

            with st.spinner("Transcribing voice..."):
                transcribed_text = transcribe_audio(audio_bytes)

            if transcribed_text:
                st.session_state.messages.append({"role": "user", "content": transcribed_text, "audio": None, "latency": None, "url": None})
                with st.chat_message("user"):
                    st.write(transcribed_text)

                with st.chat_message("assistant"):
                    start_time = perf_counter()
                    with st.spinner("Thinking..."):
                        assistant_response, target_url = process_command(
                            transcribed_text, selected_model, history=st.session_state.messages[:-1]
                        )

                    audio_response_bytes = None
                    if enable_voice_reply:
                        with st.spinner("Generating audio..."):
                            audio_response_bytes = generate_speech(assistant_response)

                    elapsed = perf_counter() - start_time
                    st.write(assistant_response)
                    if target_url:
                        st.link_button("Open Link in Browser", target_url)
                    if audio_response_bytes:
                        st.audio(audio_response_bytes, format="audio/mp3", autoplay=True)
                    st.markdown(f'<div class="metric-caption">Response time: {elapsed:.2f}s</div>', unsafe_allow_html=True)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_response,
                        "audio": audio_response_bytes,
                        "latency": elapsed,
                        "url": target_url,
                    }
                )
            else:
                st.error("Could not understand audio. Please try speaking again.")

    # Handle Text Input
    user_text_input = st.chat_input("Or type your question here...")
    if user_text_input:
        st.session_state.messages.append({"role": "user", "content": user_text_input, "audio": None, "latency": None, "url": None})
        with st.chat_message("user"):
            st.write(user_text_input)

        with st.chat_message("assistant"):
            start_time = perf_counter()
            with st.spinner("Thinking..."):
                assistant_response, target_url = process_command(
                    user_text_input, selected_model, history=st.session_state.messages[:-1]
                )

            audio_response_bytes = None
            if enable_voice_reply:
                with st.spinner("Generating audio..."):
                    audio_response_bytes = generate_speech(assistant_response)

            elapsed = perf_counter() - start_time
            st.write(assistant_response)
            if target_url:
                st.link_button("Open Link in Browser", target_url)
            if audio_response_bytes:
                st.audio(audio_response_bytes, format="audio/mp3", autoplay=True)
            st.markdown(f'<div class="metric-caption">Response time: {elapsed:.2f}s</div>', unsafe_allow_html=True)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "audio": audio_response_bytes,
                "latency": elapsed,
                "url": target_url,
            }
        )


