import numpy as np
import noisereduce as nr
import sounddevice as sd
import speech_recognition as sr

SAMPLE_RATE = 16000
NOISE_DURATION = 2
SPEECH_DURATION = 5

recognizer = sr.Recognizer()
recognizer.operation_timeout = 15


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


def main() -> None:
    input("Press Enter, then stay silent for two seconds...")
    print("Measuring background noise...")
    noise = record_audio(NOISE_DURATION)

    input("Press Enter to record your command...")
    print("Speak now. Recording for five seconds...")
    recording = record_audio(SPEECH_DURATION)

    print("Reducing background noise...")
    cleaned = nr.reduce_noise(
        y=recording.astype(np.float32),
        sr=SAMPLE_RATE,
        y_noise=noise.astype(np.float32),
        stationary=True,
        prop_decrease=0.7,
    )

    # Convert back to little-endian, signed 16-bit PCM audio.
    cleaned_pcm = np.clip(cleaned, -32768, 32767).astype("<i2")

    audio = sr.AudioData(
        cleaned_pcm.tobytes(),
        sample_rate=SAMPLE_RATE,
        sample_width=2,
    )

    print("Transcribing...")
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Could not understand the recording. Try speaking clearly.")
    except sr.RequestError as error:
        print(f"Recognition service failed: {error}")


if __name__ == "__main__":
    main()
    