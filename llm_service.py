import os
from dotenv import load_dotenv
import ollama
from groq import Groq
from google import genai

# Load environment variables from .env if present
load_dotenv()

SYSTEM_PROMPT = (
    "You are a helpful, intelligent voice assistant. "
    "Answer briefly in plain language, using at most three sentences."
)


def get_available_ollama_models() -> tuple[bool, list[str]]:
    """Checks if local Ollama is running and returns installed models."""
    try:
        client = ollama.Client(host="http://localhost:11434", timeout=3)
        model_list = client.list()
        models = [m.model for m in model_list.models]
        return True, models
    except Exception:
        return False, []


def query_ollama(
    prompt: str,
    model_name: str = "qwen3:1.7b",
    history: list[dict] | None = None,
) -> str:
    """Queries local Ollama instance with conversation history."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

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
            options={"num_ctx": 2048, "num_predict": 600},
        )
        return response.message.content.strip()
    except Exception as error:
        return f"Local Ollama error: {error}. Ensure Ollama is running locally."


def get_available_groq_models(api_key: str | None = None) -> list[str]:
    """Retrieves available text chat model IDs from Groq API or returns supported defaults."""
    default_models = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "gemma2-9b-it",
        "mixtral-8x7b-32768",
    ]
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        return default_models

    try:
        client = Groq(api_key=key)
        models_data = client.models.list()
        excluded_keywords = ("whisper", "guard", "canopylabs", "orpheus", "playai", "tts", "embedding", "vision", "specdec")
        active_models = [
            m.id for m in models_data.data 
            if not any(kw in m.id.lower() for kw in excluded_keywords)
        ]
        if active_models:
            # Ensure fast standard chat models are prioritized at the top
            for priority_model in ("llama-3.1-8b-instant", "llama-3.3-70b-versatile", "llama-3.1-70b-versatile"):
                if priority_model in active_models:
                    active_models.remove(priority_model)
                    active_models.insert(0, priority_model)
            return active_models
    except Exception:
        pass
    return default_models


def query_groq(
    prompt: str,
    model_name: str = "llama-3.1-8b-instant",
    history: list[dict] | None = None,
    api_key: str | None = None,
) -> str:
    """Queries Groq Cloud API for ultra-fast high-parameter LLM inference with automatic model fallback."""
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        return "Groq API key missing. Please provide your API key in settings or set GROQ_API_KEY in .env."

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for msg in history[-8:]:
            if msg.get("role") in ("user", "assistant") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": prompt})

    candidate_models = [model_name]
    for fallback in ("llama-3.1-8b-instant", "llama-3.3-70b-versatile"):
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    client = Groq(api_key=key)
    last_error = None
    for candidate in candidate_models:
        try:
            completion = client.chat.completions.create(
                model=candidate,
                messages=messages,
                max_tokens=600,
                temperature=0.6,
            )
            return completion.choices[0].message.content.strip()
        except Exception as error:
            last_error = error
            err_str = str(error)
            # If terms required, model deprecated/not found, or overloaded, try standard fallback model
            if any(x in err_str for x in ("model_terms_required", "terms acceptance", "404", "400", "503")):
                continue
            return f"Groq Cloud error: {error}."

    return f"Groq Cloud error: {last_error}."



def get_available_gemini_models(api_key: str | None = None) -> list[str]:
    """Retrieves available free-tier Flash model IDs from Gemini API or returns supported defaults."""
    default_models = [
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-2.5-flash-lite",
    ]
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        return default_models

    try:
        client = genai.Client(api_key=key)
        models_data = list(client.models.list())
        active = []
        for m in models_data:
            clean_name = m.name.replace("models/", "") if hasattr(m, "name") else str(m)
            # Only include Flash models for reliable free tier quota
            if "flash" in clean_name and "pro" not in clean_name:
                if not any(x in clean_name for x in ("preview-tts", "imagen", "embedding", "aqa", "experimental")):
                    active.append(clean_name)
        if active:
            if "gemini-3.8-flash" in active:
                active.remove("gemini-3.8-flash")
                active.insert(0, "gemini-3.8-flash")
            return active
    except Exception:
        pass
    return default_models


def query_gemini(
    prompt: str,
    model_name: str = "gemini-3.8-flash",
    history: list[dict] | None = None,
    api_key: str | None = None,
) -> str:
    """Queries Google Gemini API with system instructions, chat history, and automatic fallback."""
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        return "Gemini API key missing. Please provide your API key in settings or set GEMINI_API_KEY in .env."

    try:
        client = genai.Client(api_key=key)

        # Format conversation context for Gemini
        conversation_context = f"System Instruction: {SYSTEM_PROMPT}\n\n"
        if history:
            for msg in history[-6:]:
                role = "User" if msg.get("role") == "user" else "Assistant"
                conversation_context += f"{role}: {msg.get('content', '')}\n"

        conversation_context += f"User: {prompt}\nAssistant:"

        # Candidate models list with fallback if chosen model is busy or hits quota
        candidate_models = [model_name]
        for fallback in ("gemini-3.8-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"):
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        last_error = None
        for candidate in candidate_models:
            try:
                response = client.models.generate_content(
                    model=candidate,
                    contents=conversation_context,
                )
                return response.text.strip()
            except Exception as candidate_err:
                last_error = candidate_err
                err_str = str(candidate_err)
                # If 503 high demand, 404 not found, or 429 quota on a specific model, try next candidate
                if any(x in err_str for x in ("503", "404", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED")):
                    continue
                else:
                    return f"Google Gemini error: {candidate_err}."

        return f"Google Gemini quota exceeded ({last_error}). Please select 'gemini-3.8-flash' or switch to 'Cloud (Groq)' in the sidebar for unlimited high-speed inference."
    except Exception as error:
        return f"Google Gemini error: {error}."




def query_llm(
    prompt: str,
    provider: str = "Local (Ollama)",
    model_name: str = "qwen3:1.7b",
    history: list[dict] | None = None,
    api_key: str | None = None,
) -> str:
    """
    Unified router that directs prompts to Local Ollama, Groq Cloud, or Google Gemini.
    """
    if "Groq" in provider:
        return query_groq(prompt, model_name=model_name, history=history, api_key=api_key)
    elif "Gemini" in provider:
        return query_gemini(prompt, model_name=model_name, history=history, api_key=api_key)
    else:
        return query_ollama(prompt, model_name=model_name, history=history)
