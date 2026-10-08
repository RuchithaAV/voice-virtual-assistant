# Voice Virtual Assistant

A modular Python-based voice and text virtual assistant project built step-by-step for learning, experimentation, local AI integration, and interactive web visualization.

---

## Project Structure

```text
voice-virtual-assistant/
|-- app.py                  # Interactive Streamlit Web UI (voice recording, multi-turn chat, audio playback)
|-- main.py                 # Terminal voice assistant with noise reduction, STT, multi-turn Ollama LLM, and TTS
|-- llm_test.py             # Standalone local LLM response generation test (Ollama)
|-- speech_to_text_test.py  # Standalone STT transcription test with noise reduction
|-- microphone_test.py      # Microphone recording and playback hardware test
|-- speech_test.py          # Standalone Text-to-Speech (TTS) test (pyttsx3)
|-- README.md               # Project documentation
`-- .venv/                  # Python virtual environment (git-ignored)
```

---

## Architecture and Workflow

The voice assistant executes the following pipeline:

1. **Audio Capture**: Captures voice through microphone hardware (`sounddevice` in terminal or `st.audio_input` in browser).
2. **Noise Reduction & Audio Preprocessing**: Cleans the input signal using `noisereduce` against an ambient baseline.
3. **Speech-to-Text (STT)**: Converts audio into text with the Google Speech Recognition API (`speech_recognition`).
4. **Contextual Memory & Routing**:
   - Matches built-in commands (`hello`, `time`, `clear memory`, `exit`).
   - Appends user and assistant dialogue turns to a sliding-window memory buffer (retaining the last 8 messages).
   - Routes open-ended questions and follow-ups to a local **Ollama** model (`qwen3:1.7b`) for contextual answers.
5. **Text-to-Speech Output**: Speaks the response aloud using the Windows SAPI voice engine (`win32com.client`) or browser audio streaming (`gTTS`).

---

## Features Implemented

- **Multi-Turn Conversation Memory**: Retains conversation history so users can ask contextual follow-up questions (e.g., "Who was Alexander Fleming?" followed by "When did he receive the Nobel Prize?").
- **Streamlit Web Interface (`app.py`)**: Full visual dashboard with browser microphone input, chat history, live response latency tracking, Ollama status/model selector, and in-browser audio playback.
- **Terminal Voice-Driven Loop (`main.py`)**: Hands-free command loop with background noise calibration and real-time TTS.
- **Ambient Noise Calibration & Reduction**: Background noise subtraction ensures high transcription accuracy in everyday environments.
- **Speech Recognition (STT)**: Robust transcription with automatic error handling for speech timeouts or background noise.
- **Local AI Intelligence (LLM)**: Offline, private conversational AI powered by Ollama (`qwen3:1.7b`).
- **Hardware Diagnostics**: Standalone scripts to test microphone capture, audio playback, TTS synthesis, STT transcription, and LLM latency individually.

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
pip install sounddevice SpeechRecognition pywin32 pyttsx3 numpy noisereduce ollama streamlit gTTS
```

---

## Running the Applications

### 1. Streamlit Web Dashboard (Recommended)
Launch the interactive web interface in your browser:
```powershell
streamlit run app.py
```
*(Access the app at `http://localhost:8501`)*

### 2. Terminal Voice Assistant
Run the voice-driven terminal assistant:
```powershell
python main.py
```
*(Or run directly with the virtual environment executable: `.\.venv\Scripts\python.exe main.py`)*

### 3. Standalone Diagnostic Tests

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

## Commands Supported

- `hello` / `hi` / `hey` - Greet the assistant.
- `time` / `what time is it` - Report the current local time.
- `clear memory` / `forget conversation` / `reset` - Wipe conversation history context.
- `exit` / `quit` / `stop` / `bye` - Terminate the assistant loop.
- *Any other query* - Handled by the local Ollama LLM with multi-turn memory.

---

## Roadmap

- [x] Integrate local LLM intelligence directly into the main voice loop.
- [x] Build an interactive Streamlit web interface with microphone recording and audio playback.
- [x] Implement multi-turn conversation memory and contextual follow-up understanding.
- [ ] Implement continuous listening / wake word activation (e.g., "Hey Assistant").
- [ ] Add system automation skills (opening applications, browser searches, volume control).
- [ ] Add live weather and news API integrations.


