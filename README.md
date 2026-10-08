# Voice Virtual Assistant

A modular Python-based voice and text virtual assistant project built step-by-step for learning, experimentation, and expansion.

---

## 📁 Project Structure

```text
voice-virtual-assistant/
├── main.py                 # Core assistant loop with TTS voice responses
├── speech_test.py          # Standalone Text-to-Speech (TTS) test script (pyttsx3)
├── microphone_test.py      # Microphone recording & audio playback test (sounddevice)
├── speech_to_text_test.py  # Speech-to-Text (STT) transcription test (sounddevice + SpeechRecognition)
├── README.md               # Project documentation
└── .venv/                  # Python virtual environment (git-ignored)
```

---

## 🚀 Features Implemented So Far

- **Interactive Command Loop**: Handles commands like `hello`, `time`, and `exit` with clean input validation and graceful termination (`Ctrl+C` / EOF).
- **Text-to-Speech (TTS)**: Assistant speaks responses out loud using the Windows SAPI voice engine (`win32com.client`) and `pyttsx3`.
- **Microphone Recording & Playback**: Captures 5 seconds of audio using `sounddevice` and immediately plays it back to test audio hardware.
- **Speech-to-Text (STT)**: Records voice input and transcribes spoken words to text using the Google Speech Recognition API with comprehensive error handling.

---

## 🛠️ Getting Started

### 1. Prerequisites
- **Python 3.10+** (tested with Python 3.13)
- Windows OS (for native Windows SAPI TTS)
- Working microphone and speaker

### 2. Virtual Environment & Dependencies

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install required packages:

```powershell
pip install sounddevice SpeechRecognition pywin32 pyttsx3 numpy
```

---

## 🧪 Running the Modules

### 1. Run the Assistant
Runs the interactive virtual assistant with voice responses:
```powershell
python main.py
```
*(Or directly: `.\.venv\Scripts\python.exe main.py`)*

### 2. Test Text-to-Speech (TTS)
Verifies that the TTS engine can speak:
```powershell
python speech_test.py
```

### 3. Test Microphone Recording & Playback
Records 5 seconds of microphone audio and plays it back:
```powershell
python microphone_test.py
```

### 4. Test Speech-to-Text (Voice Recognition)
Records 5 seconds of speech and transcribes it to text:
```powershell
python speech_to_text_test.py
```

---

## 📌 Next Steps
- [ ] Connect microphone voice input (`speech_to_text_test.py`) directly into the main assistant loop (`main.py`).
- [ ] Add a wake word or continuous listening mode.
- [ ] Implement additional skills (web search, opening applications, weather forecasts, volume control).
