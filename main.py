import os
from datetime import datetime
from dotenv import load_dotenv
import numpy as np
import noisereduce as nr
import sounddevice as sd
import speech_recognition as sr
import win32com.client
from skills import execute_skill
from llm_service import query_llm

# Load .env file if present
load_dotenv()

# Audio configuration
SAMPLE_RATE = 16000

# Initialize Windows SAPI voice engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")

# Initialize Speech Recognizer
recognizer = sr.Recognizer()
recognizer.operation_timeout = 15

# Persistent multi-turn conversation memory
conversation_history: list[dict] = []


def respond(message: str) -> None:
    """Prints the assistant response and speaks it."""
    print(f"Assistant: {message}")
    speaker.Speak(message)


def ask_llm(prompt: str) -> str:
    """Queries Hybrid LLM (Groq / Gemini / Local Ollama) with multi-turn memory."""
    global conversation_history

    # Auto-detect cloud keys or fallback to local Ollama
    if os.environ.get("GROQ_API_KEY"):
        provider = "Cloud (Groq)"
        model_name = "llama-3.1-8b-instant"
    elif os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        provider = "Cloud (Google Gemini)"
        model_name = "gemini-3.8-flash"
    else:
        provider = "Local (Ollama)"
        model_name = "qwen3:1.7b"

    answer = query_llm(
        prompt=prompt,
        provider=provider,
        model_name=model_name,
        history=conversation_history,
    )

    # Append to memory
    conversation_history.append({"role": "user", "content": prompt})
    conversation_history.append({"role": "assistant", "content": answer})
    return answer



def handle_command(command: str) -> bool:
    """Processes a user command, executes system skills, or routes to local LLM with memory.
    
    Returns:
        bool: False if the loop should terminate ('exit'), True otherwise.
    """
    global conversation_history
    cleaned_command = command.strip().lower()

    if cleaned_command in ("exit", "quit", "bye", "stop"):
        respond("Goodbye!")
        return False
    elif cleaned_command in ("clear memory", "forget conversation", "reset memory", "reset"):
        conversation_history.clear()
        respond("I have cleared my memory of our previous conversation.")
        return True
    elif cleaned_command in ("hello", "hey", "hi"):
        respond("Hello! How can I help you today?")
        return True
    elif cleaned_command in ("time", "what is the time", "what time is it"):
        current_time = datetime.now().strftime("%I:%M %p")
        respond(f"The current time is {current_time}.")
        return True

    # 1. Check for system automation skills (opening apps, searches, volume control)
    skill_handled, skill_response, _ = execute_skill(command)
    if skill_handled and skill_response:
        respond(skill_response)
        return True


    # 2. Fallback to local Ollama LLM with memory
    print("Thinking...")
    answer = ask_llm(command)
    respond(answer)
    return True



def record_audio(duration: int) -> np.ndarray:
    """Record mono audio as 16-bit integer samples."""
    recording = sd.rec(
        duration * SAMPLE_RATE,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    return recording[:, 0]


def listen(noise: np.ndarray) -> str | None:
    """Records speech, applies noise reduction, and transcribes to text."""
    print("Speak now. Recording for five seconds...")
    recording = record_audio(5)

    cleaned = nr.reduce_noise(
        y=recording.astype(np.float32),
        sr=SAMPLE_RATE,
        y_noise=noise.astype(np.float32),
        stationary=True,
        prop_decrease=0.7,
    )

    cleaned_pcm = np.clip(cleaned, -32768, 32767).astype("<i2")
    audio = sr.AudioData(
        cleaned_pcm.tobytes(),
        sample_rate=SAMPLE_RATE,
        sample_width=2,
    )

    print("Transcribing...")
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        respond("I couldn't understand you. Please try again.")
    except sr.RequestError as error:
        print(f"Recognition service failed: {error}")
        respond("The speech recognition service is unavailable.")

    return None


def main() -> None:
    print("=== Voice Virtual Assistant ===")
    print("Commands: hello, time, clear memory, ask any question, or exit")
    print("Press Ctrl+C to quit at any time.\n")

    try:
        input("Press Enter, then stay silent for two seconds...")
        print("Measuring background noise...")
        noise = record_audio(2)

        while True:
            input("\nPress Enter to speak...")
            command = listen(noise)

            if command is None:
                continue

            if not handle_command(command):
                break

    except (KeyboardInterrupt, EOFError):
        print("\nAssistant stopped.")


if __name__ == "__main__":
    main()