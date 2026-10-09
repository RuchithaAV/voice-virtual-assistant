# Voice Virtual Assistant

A modular Python-based voice and text virtual assistant project built step-by-step for learning, experimentation, local AI integration, cloud LLM scaling, system automation, and interactive web visualization.

---

## Project Structure

```text
voice-virtual-assistant/
|-- app.py                  # Interactive Streamlit Web UI (voice recording, multi-turn chat, audio playback)
|-- main.py                 # Terminal voice assistant with noise reduction, STT, hybrid LLM, and TTS
|-- llm_service.py          # Unified AI router (Local Ollama, Cloud Groq, Google Gemini)
|-- skills.py               # System automation skills engine (apps, web search, volume control)
|-- llm_test.py             # Standalone local LLM response generation test (Ollama)
|-- speech_to_text_test.py  # Standalone STT transcription test with noise reduction
|-- microphone_test.py      # Microphone recording and playback hardware test
|-- speech_test.py          # Standalone Text-to-Speech (TTS) test (pyttsx3)
|-- .env.example            # Environment variable template for optional Cloud API keys
|-- README.md               # Project documentation
`-- .venv/                  # Python virtual environment (git-ignored)
```

---

## Architecture and Workflow

The voice assistant executes the following pipeline:

1. **Audio Capture**: Captures voice through microphone hardware (`sounddevice` in terminal or `st.audio_input` in browser).
2. **Noise Reduction & Preprocessing**: Cleans the input signal using `noisereduce` against an ambient baseline.
3. **Speech-to-Text (STT)**: Converts audio into text with the Google Speech Recognition API (`speech_recognition`).
4. **Skills & Hybrid AI Dispatching**:
   - **System Automation Skills (`skills.py`)**: Intercepts commands for launching applications, web searches, and volume adjustments.
   - **Built-in Assistant Commands**: Handles greetings, time checks, memory reset, and exit.
   - **Hybrid LLM Router (`llm_service.py`)**:
     - **Local Mode (Ollama)**: 100% offline & private (`qwen3:1.7b`).
     - **Cloud Mode (Groq)**: Near-instant inference using 70B parameter model (`llama-3.3-70b-versatile`).
     - **Cloud Mode (Google Gemini)**: Deep reasoning and fresh knowledge (`gemini-2.0-flash`).
5. **Text-to-Speech Output**: Speaks the response aloud using the Windows SAPI voice engine (`win32com.client`) or browser audio streaming (`gTTS`).

---

## Features Implemented

- **Hybrid AI Brain (Local + Cloud)**:
  - **Local Ollama**: 100% offline and private.
  - **Groq Cloud**: High-speed reasoning powered by Llama 3.3 70B (<0.4s response time).
  - **Google Gemini**: Deep explanations and factual accuracy via Gemini Flash.
- **System Automation Skills (`skills.py`)**:
  - **Desktop Application Launcher**: Opens apps like Notepad, Calculator, VS Code, Chrome, Edge, File Explorer, Task Manager, Paint, and Spotify.
  - **Web & Video Search**: Performs Google and YouTube searches directly in the default browser.
  - **Direct Website Navigation**: Instantly opens YouTube, Google, GitHub, Wikipedia, Reddit, and ChatGPT.
  - **Hardware Volume Control**: Adjusts system volume up/down and toggles mute via Windows virtual-key events.
- **Multi-Turn Conversation Memory**: Retains conversation history so users can ask contextual follow-up questions.
- **Streamlit Web Interface (`app.py`)**: Full visual dashboard with browser microphone input, chat history, live latency tracking, provider/model selector, API key input, and in-browser audio playback.
- **Terminal Voice-Driven Loop (`main.py`)**: Hands-free command loop with background noise calibration and real-time TTS.
- **Ambient Noise Calibration & Reduction**: Background noise subtraction ensures high transcription accuracy in everyday environments.
- **Speech Recognition (STT)**: Robust transcription with automatic error handling for speech timeouts or background noise.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.13)
- Windows OS (for native Windows SAPI TTS and volume control)
- Working microphone and audio output device
- *(Optional for Local AI)*: Ollama installed and running with `ollama run qwen3:1.7b`
- *(Optional for Cloud AI)*: Free API key from [Groq](https://console.groq.com/keys) or [Google AI Studio](https://aistudio.google.com/app/apikey)

### 2. Virtual Environment Setup

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install required dependencies:

```powershell
pip install sounddevice SpeechRecognition pywin32 pyttsx3 numpy noisereduce ollama streamlit gTTS groq google-genai python-dotenv psutil requests
```

### 3. Optional: Configure Cloud API Keys

Copy the template file to `.env` and paste your free API key:

```powershell
copy .env.example .env
```

Edit `.env`:
```ini
GROQ_API_KEY=gsk_your_groq_key_here
GEMINI_API_KEY=AIzaSy_your_gemini_key_here
```
*(Or simply paste the key into the Streamlit sidebar at runtime).*

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

### 1. System Automation & Real-Time Skills
- **Live Weather**: *"what is the weather in London"*, *"weather in Tokyo"*, *"temperature in Paris"* (Powered by Open-Meteo API with zero API key requirement)
- **Encyclopedic Knowledge (Wikipedia RAG)**: *"who is Isaac Newton"*, *"who was Marie Curie"*, *"what is quantum computing"*, *"tell me about artificial intelligence"*
- **Date and Time**: *"what time is it"*, *"what is today's date"*, *"what day is today"*
- **System Health & Battery**: *"battery status"*, *"battery level"*, *"cpu usage"*, *"system diagnostics"*
- **Desktop Applications**: *"open notepad"*, *"open calculator"*, *"open chrome"*, *"open vs code"*, *"open file explorer"*, *"open task manager"*, *"open paint"*, *"open spotify"*
- **Web and Video Searches**: *"search google for machine learning"*, *"search youtube for lo-fi music"*, *"play bohemian rhapsody on youtube"*
- **Direct Website Navigation**: *"open youtube"*, *"open github"*, *"open wikipedia"*, *"open reddit"*, *"open chatgpt"*
- **Hardware Volume**: *"volume up"*, *"volume down"*, *"mute volume"*, *"unmute"*

### 2. Built-in Assistant Commands
- **Greetings**: `hello`, `hi`, `hey`
- **Memory**: `clear memory`, `forget conversation`, `reset`
- **Exit**: `exit`, `quit`, `stop`, `bye`
- **General AI Reasoning**: Any open-ended question answered by the active Local or Cloud LLM with multi-turn memory.

---

## Roadmap

- [x] Integrate local LLM intelligence directly into the main voice loop.
- [x] Build an interactive Streamlit web interface with microphone recording and audio playback.
- [x] Implement multi-turn conversation memory and contextual follow-up understanding.
- [x] Add system automation skills (opening applications, browser searches, volume control).
- [x] Add Hybrid Cloud AI option (Groq 70B and Google Gemini Flash support).
- [x] Add deterministic real-time skills (Open-Meteo Weather, Wikipedia RAG summary, Date/Time, System Diagnostics).
- [ ] Implement continuous listening / wake word activation (e.g., "Hey Assistant").
