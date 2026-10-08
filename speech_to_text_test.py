import sounddevice as sd
import speech_recognition as sr

SAMPLE_RATE = 16000
DURATION = 5

recognizer = sr.Recognizer()
recognizer.operation_timeout = 15

input("Press Enter to start recording...")
print("Speak now. Recording for five seconds...")

recording = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
)
sd.wait()

audio = sr.AudioData(
    recording.tobytes(),
    sample_rate=SAMPLE_RATE,
    sample_width=2,
)

print("Transcribing...")

try:
    text = recognizer.recognize_google(audio, language="en-US")
    print(f"You said: {text}")
except sr.UnknownValueError:
    print("Could not understand the recording.")
except sr.RequestError as error:
    print(f"Recognition service failed: {error}")