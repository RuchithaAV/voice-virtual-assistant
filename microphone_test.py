import sounddevice as sd 


SAMPLE_RATE = 16000
DURATION = 5

input("Press Enter to start recording...")
print("Recording for five seconds. Say: hello assistant.")

recording = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
)
sd.wait()

print("Playing your recording...")
sd.play(recording, SAMPLE_RATE)
sd.wait()

print("Finished.")