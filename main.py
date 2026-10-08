import win32com.client
from datetime import datetime
import numpy as np
import noisereduce as nr
import sounddevice as sd
import speech_recognition as sr

# Initialize Windows SAPI voice engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")


def respond(message: str) -> None:
    """Prints the assistant response and speaks it."""
    print(f"Assistant: {message}")
    speaker.Speak(message)


def handle_command(command: str) -> bool:
    """Processes a user command.
    
    Returns:
        bool: False if the loop should terminate ('exit'), True otherwise.
    """
    cleaned_command = command.strip().lower()

    if cleaned_command == "hello":
        respond("Hello! How can I help you today?")
    elif cleaned_command == "time":
        current_time = datetime.now().strftime("%I:%M %p")
        respond(f"The current time is {current_time}.")
    elif cleaned_command == "exit":
        respond("Goodbye!")
        return False
    else:
        respond("I don't understand that command yet.")

    return True

SAMPLE_RATE = 16000

recognizer = sr.Recognizer()
recognizer.operation_timeout = 15


def record_audio(duration: int) -> np.ndarray:
    recording = sd.rec(
        duration * SAMPLE_RATE,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    return recording[:, 0]


def listen(noise: np.ndarray) -> str | None:
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
    print("Commands: hello, time, exit")
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