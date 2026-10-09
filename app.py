import io
import os
from time import perf_counter
from datetime import datetime
from gtts import gTTS
import speech_recognition as sr
import streamlit as st
from skills import execute_skill
from llm_service import (
    query_llm,
    get_available_ollama_models,
    get_available_groq_models,
    get_available_gemini_models,
)

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
        margin-bottom: 0.5rem;
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
            "url": None,
        }
    ]

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None


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


import tempfile
import win32com.client


# Helper: Generate TTS Audio (Local Windows SAPI WAV or Cloud gTTS MP3)
def generate_speech(text: str) -> tuple[bytes | None, str]:
    # 1. Native Offline Windows SAPI TTS (Instant, Zero Network Latency)
    try:
        temp_wav = os.path.join(tempfile.gettempdir(), f"assistant_tts_{os.getpid()}.wav")
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
        file_stream.Open(temp_wav, 3, False)
        speaker.AudioOutputStream = file_stream
        speaker.Speak(text)
        file_stream.Close()
        with open(temp_wav, "rb") as f:
            data = f.read()
        return data, "audio/wav"
    except Exception:
        pass

    # 2. Online gTTS Fallback
    try:
        fp = io.BytesIO()
        tts = gTTS(text=text, lang="en")
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue(), "audio/mp3"
    except Exception as error:
        st.warning(f"Voice synthesis error: {error}")
        return None, "audio/mp3"



# Helper: Route command, execute system skills, or send to LLM
def process_command(
    user_query: str,
    provider: str,
    model_name: str,
    history: list[dict] | None = None,
    api_key: str | None = None,
) -> tuple[str, str | None]:
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

    # Fallback to selected LLM provider (Local Ollama, Groq, or Gemini)
    response_text = query_llm(
        prompt=user_query,
        provider=provider,
        model_name=model_name,
        history=history,
        api_key=api_key,
    )
    return response_text, None


# --- Sidebar: Settings & Provider Switching ---
with st.sidebar:
    st.header("AI Brain & Settings")

    # 1. Select AI Provider
    ai_provider = st.radio(
        "Select AI Provider",
        options=["Local (Ollama)", "Cloud (Groq)", "Cloud (Google Gemini)"],
        index=0,
    )

    api_key_input = None

    if ai_provider == "Local (Ollama)":
        ollama_ok, available_models = get_available_ollama_models()
        if ollama_ok:
            st.markdown(
                '<div class="status-badge status-online">Local Ollama: Online</div>',
                unsafe_allow_html=True,
            )
            if available_models:
                default_idx = available_models.index("qwen3:1.7b") if "qwen3:1.7b" in available_models else 0
                selected_model = st.selectbox("Local Model", options=available_models, index=default_idx)
            else:
                selected_model = "qwen3:1.7b"
                st.warning("No models found. Run `ollama run qwen3:1.7b`")
        else:
            st.markdown(
                '<div class="status-badge status-offline">Local Ollama: Offline</div>',
                unsafe_allow_html=True,
            )
            st.error("Ollama server not detected. Start Ollama or switch to Cloud above.")
            selected_model = "qwen3:1.7b"

    elif ai_provider == "Cloud (Groq)":
        st.markdown(
            '<div class="status-badge status-online">Cloud Groq: Ultra-Fast Inference</div>',
            unsafe_allow_html=True,
        )
        api_key_input = st.text_input(
            "Groq API Key",
            type="password",
            value=os.environ.get("GROQ_API_KEY", ""),
            placeholder="gsk_...",
            help="Get free key at console.groq.com",
        )
        groq_options = get_available_groq_models(api_key_input)
        default_idx = groq_options.index("llama-3.1-8b-instant") if "llama-3.1-8b-instant" in groq_options else 0
        selected_model = st.selectbox(
            "Groq Model",
            options=groq_options,
            index=default_idx,
        )
        if not api_key_input:
            st.info("Paste your free Groq API key above (from [console.groq.com](https://console.groq.com/keys)).")


    else:  # Google Gemini
        st.markdown(
            '<div class="status-badge status-online">Google Gemini: Multimodal Intelligence</div>',
            unsafe_allow_html=True,
        )
        api_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            value=os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", ""),
            placeholder="AIzaSy... or AQ....",
            help="Get free key at aistudio.google.com",
        )
        gemini_options = get_available_gemini_models(api_key_input)
        default_idx = gemini_options.index("gemini-3.8-flash") if "gemini-3.8-flash" in gemini_options else 0
        selected_model = st.selectbox(
            "Gemini Model",
            options=gemini_options,
            index=default_idx,
        )
        if not api_key_input:
            st.info("Paste your free Gemini key above (from [aistudio.google.com](https://aistudio.google.com/app/apikey)).")


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
        **Hybrid Architecture:**
        - **Local Ollama**: 100% private, offline 2B model.
        - **Cloud Groq**: 70B parameter model with near-instant inference (<0.4s).
        - **Google Gemini**: Deep reasoning with latest web knowledge.
        """
    )


# --- Main Application Area ---
st.markdown('<div class="main-title">Voice Virtual Assistant</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Running with <strong>{ai_provider}</strong> ({selected_model})</div>', unsafe_allow_html=True)

col_chat, col_audio = st.columns([2.5, 1.2], gap="large")

with col_audio:
    st.subheader("Voice Recording")
    st.caption("Click to record your voice command:")
    audio_data = st.audio_input("Record Voice Command", label_visibility="collapsed")

with col_chat:
    # Render Conversation History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("url"):
                st.link_button("Open Link in Browser", msg["url"])
            if msg.get("audio"):
                st.audio(msg["audio"], format=msg.get("format", "audio/wav"))
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
                st.session_state.messages.append({"role": "user", "content": transcribed_text, "audio": None, "latency": None, "url": None, "format": None})
                with st.chat_message("user"):
                    st.write(transcribed_text)

                with st.chat_message("assistant"):
                    start_time = perf_counter()
                    with st.spinner("Thinking..."):
                        assistant_response, target_url = process_command(
                            user_query=transcribed_text,
                            provider=ai_provider,
                            model_name=selected_model,
                            history=st.session_state.messages[:-1],
                            api_key=api_key_input,
                        )

                    audio_response_bytes, audio_fmt = None, "audio/wav"
                    if enable_voice_reply:
                        with st.spinner("Generating audio..."):
                            audio_response_bytes, audio_fmt = generate_speech(assistant_response)

                    elapsed = perf_counter() - start_time
                    st.write(assistant_response)
                    if target_url:
                        st.link_button("Open Link in Browser", target_url)
                    if audio_response_bytes:
                        st.audio(audio_response_bytes, format=audio_fmt, autoplay=True)
                    st.markdown(f'<div class="metric-caption">Response time: {elapsed:.2f}s</div>', unsafe_allow_html=True)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_response,
                        "audio": audio_response_bytes,
                        "latency": elapsed,
                        "url": target_url,
                        "format": audio_fmt,
                    }
                )
            else:
                st.error("Could not understand audio. Please try speaking again.")

    # Handle Text Input
    user_text_input = st.chat_input("Or type your question here...")
    if user_text_input:
        st.session_state.messages.append({"role": "user", "content": user_text_input, "audio": None, "latency": None, "url": None, "format": None})
        with st.chat_message("user"):
            st.write(user_text_input)

        with st.chat_message("assistant"):
            start_time = perf_counter()
            with st.spinner("Thinking..."):
                assistant_response, target_url = process_command(
                    user_query=user_text_input,
                    provider=ai_provider,
                    model_name=selected_model,
                    history=st.session_state.messages[:-1],
                    api_key=api_key_input,
                )

            audio_response_bytes, audio_fmt = None, "audio/wav"
            if enable_voice_reply:
                with st.spinner("Generating audio..."):
                    audio_response_bytes, audio_fmt = generate_speech(assistant_response)

            elapsed = perf_counter() - start_time
            st.write(assistant_response)
            if target_url:
                st.link_button("Open Link in Browser", target_url)
            if audio_response_bytes:
                st.audio(audio_response_bytes, format=audio_fmt, autoplay=True)
            st.markdown(f'<div class="metric-caption">Response time: {elapsed:.2f}s</div>', unsafe_allow_html=True)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "audio": audio_response_bytes,
                "latency": elapsed,
                "url": target_url,
                "format": audio_fmt,
            }
        )




