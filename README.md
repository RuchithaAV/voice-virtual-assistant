# Voice Virtual Assistant

A modular Python-based voice and text virtual assistant project built step-by-step for learning, experimentation, and local AI integration.

---

## Project Structure

```text
voice-virtual-assistant/
|-- main.py                 # Main voice assistant with noise reduction, STT, and TTS
|-- llm_test.py             # Local LLM response generation test (Ollama)
|-- speech_to_text_test.py  # Standalone STT transcription test with noise reduction
|-- microphone_test.py      # Microphone recording and playback hardware test
|-- speech_test.py          # Standalone Text-to-Speech (TTS) test (pyttsx3)
|-- README.md               # Project documentation
`-- .venv/                  # Python virtual environment (git-ignored)
```

---

## Features Implemented

- **Voice-Driven Assistant Loop**: Listens for user speech, transcribes commands in real time, and speaks responses aloud using Windows SAPI (`win32com.client`).
- **Ambient Noise Calibration & Reduction**: Measures a 2-second background noise profile at startup and applies spectral noise reduction (`noisereduce` and `numpy`) before audio transcription.
- **Speech-to-Text (STT)**: Captures 16 kHz mono audio via `sounddevice` and transcribes using the Google Speech Recognition API with comprehensive error handling.
- **Text-to-Speech (TTS)**: Delivers spoken voice responses using Windows SAPI (`SAPI.SpVoice`) and `pyttsx3`.
- **Local LLM Intelligence**: Queries a locally running Ollama instance (`qwen3:1.7b`) with concise system prompting and response latency tracking.
- **Hardware Diagnostics**: Dedicated standalone scripts for testing microphone input, speaker playback, speech recognition, and LLM inference independently.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.13)
- Windows OS (for native Windows SAPI TTS)
- Working microphone and audio output device
- Ollama installed and running locally (`ollama run qwen3:1.7b`)

### 2. Virtual Environment Setup

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install required dependencies:

```powershell
pip install sounddevice SpeechRecognition pywin32 pyttsx3 numpy noisereduce ollama
```

---

## Running the Modules

### 1. Main Voice Assistant
Calibrates ambient noise, listens to voice commands, and responds with voice:
```powershell
python main.py
```
*(Or run directly with the virtual environment interpreter: `.\.venv\Scripts\python.exe main.py`)*

### 2. Local LLM Test
Sends a prompt to the local Ollama instance and prints the response along with inference time:
```powershell
python llm_test.py
```

### 3. Speech-to-Text Test with Noise Reduction
Measures 2 seconds of ambient silence, records 5 seconds of speech, applies noise reduction, and prints transcribed text:
```powershell
python speech_to_text_test.py
```

### 4. Microphone Recording and Playback Test
Records 5 seconds of microphone audio and immediately plays it back to verify hardware functionality:
```powershell
python microphone_test.py
```

### 5. Text-to-Speech Test
Verifies that the TTS engine can synthesize and speak text:
```powershell
python speech_test.py
```

---

## Roadmap

- Integrate local LLM fallback into `main.py` for queries beyond fixed commands.
- Implement continuous listening / wake word activation.
- Add additional skills (system automation, weather lookups, web searching).
