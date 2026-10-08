# Voice Virtual Assistant

A modular Python-based voice and text virtual assistant project built step-by-step for learning, experimentation, and local AI integration.

---

## Project Structure

```text
voice-virtual-assistant/
|-- main.py                 # Full voice assistant with noise reduction, STT, Ollama LLM, and TTS
|-- llm_test.py             # Standalone local LLM response generation test (Ollama)
|-- speech_to_text_test.py  # Standalone STT transcription test with noise reduction
|-- microphone_test.py      # Microphone recording and playback hardware test
|-- speech_test.py          # Standalone Text-to-Speech (TTS) test (pyttsx3)
|-- README.md               # Project documentation
`-- .venv/                  # Python virtual environment (git-ignored)
```

---

## Architecture and Workflow

The core assistant in `main.py` executes the following sequential pipeline:

1. **Noise Profiling**: Measures a 2-second ambient noise profile on startup.
2. **Audio Capture**: Records 5 seconds of 16 kHz mono microphone audio via `sounddevice`.
3. **Noise Reduction**: Cleans the input signal using `noisereduce` against the initial noise baseline.
4. **Speech-to-Text**: Converts processed audio to text using the Google Speech Recognition API (`speech_recognition`).
5. **Command & LLM Routing**:
   - Matches built-in commands (`hello`, `time`, `exit`).
   - Routes open-ended questions to a local **Ollama** model (`qwen3:1.7b`) for concise, intelligent answers.
6. **Text-to-Speech Output**: Speaks the response aloud using the native Windows SAPI voice engine (`win32com.client`).

---

## Features Implemented

- **Voice-Driven Assistant Loop**: Fully hands-free voice interaction loop with real-time feedback and clean `Ctrl+C` interrupt handling.
- **Ambient Noise Calibration & Reduction**: Dynamic background noise subtraction ensures higher transcription accuracy in everyday environments.
- **Speech Recognition (STT)**: High-accuracy speech transcription with automatic fallbacks for unrecognized speech or network timeouts.
- **Local AI Intelligence (LLM)**: Offline, private conversational AI powered by Ollama (`qwen3:1.7b`), constrained to short voice-friendly responses.
- **Text-to-Speech (TTS)**: Fast, natural speech synthesis via Windows SAPI.
- **Hardware & Component Tests**: Dedicated standalone diagnostic scripts to test microphone capture, audio playback, TTS synthesis, STT transcription, and LLM latency individually.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.13)
- Windows OS (for native Windows SAPI TTS)
- Working microphone and audio output device
- Ollama installed and running locally with the target model:
  ```powershell
  ollama run qwen3:1.7b
  ```

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
Runs the full end-to-end voice assistant:
```powershell
python main.py
```
*(Or run directly with the virtual environment executable: `.\.venv\Scripts\python.exe main.py`)*

### 2. Standalone Diagnostic Tests

- **Local LLM Test**:
  ```powershell
  python llm_test.py
  ```
- **Speech-to-Text with Noise Reduction**:
  ```powershell
  python speech_to_text_test.py
  ```
- **Microphone Hardware Loopback**:
  ```powershell
  python microphone_test.py
  ```
- **Text-to-Speech Synthesis**:
  ```powershell
  python speech_test.py
  ```

---

## Roadmap

- [x] Integrate local LLM intelligence directly into the main voice loop.
- [ ] Implement continuous listening / wake word activation (e.g., "Hey Assistant").
- [ ] Add system automation skills (opening applications, browser searches, volume control).
- [ ] Add live weather and news API integrations.

