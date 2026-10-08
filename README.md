# Voice Virtual Assistant

A modular Python-based virtual assistant project built step-by-step for learning and experimentation.

## Project Structure

- `main.py`: Core assistant entry point and command processing loop.
- `.venv/`: Project-local virtual environment (ignored in git).

## Getting Started

### 1. Prerequisites
- Python 3.10+

### 2. Setup
Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Run the Assistant
```powershell
python main.py
```
*(Or directly without activating: `.venv\Scripts\python.exe main.py`)*

## Current Features
- Interactive text command loop (`hello`, `time`, `exit`).
- Robust input handling and graceful exit on `Ctrl+C`.
