import win32com.client
from datetime import datetime
import numpy as np
import noisereduce as nr
from ollama import Client
from skills import execute_skill
import sounddevice as sd
import speech_recognition as sr

# Audio configuration
SAMPLE_RATE = 16000

# Initialize Windows SAPI voice engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")

# Initialize Speech Recognizer
recognizer = sr.Recognizer()
recognizer.operation_timeout = 15

# Initialize local Ollama client
ollama_client = Client(host="http://localhost:11434", timeout=60)
MODEL_NAME = "qwen3:1.7b"

# System prompt for concise voice responses
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a helpful voice assistant. "
        "Answer briefly in plain language, using at most three sentences."
    ),
}

# Persistent multi-turn conversation memory
conversation_history: list[dict] = []
MAX_HISTORY_MESSAGES = 8  # Keeps last 4 user-assistant exchanges


def respond(message: str) -> None:
    """Prints the assistant response and speaks it."""
    print(f"Assistant: {message}")
    speaker.Speak(message)


def ask_llm(prompt: str) -> str:
    """Queries Ollama with full multi-turn conversation history."""
    global conversation_history

    # Append current user question to history
    conversation_history.append({"role": "user", "content": prompt})

    # Keep only the most recent N messages to avoid context overflow
    trimmed_history = conversation_history[-MAX_HISTORY_MESSAGES:]

    try:
        response = ollama_client.chat(
            model=MODEL_NAME,
            messages=[SYSTEM_PROMPT] + trimmed_history,
            think=False,
            options={"num_ctx": 2048, "num_predict": 150},
        )
        answer = response.message.content.strip()

        # Append assistant response to history
        conversation_history.append({"role": "assistant", "content": answer})
        return answer
    except Exception as error:
        print(f"LLM generation failed: {error}")
        return "Sorry, I had trouble generating a response."


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