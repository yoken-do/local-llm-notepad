# Local LLM Notepad
Plug a USB drive and run a modern LLM on any PC **locally** with a double‑click. 

***No installation, no internet, no API, no Cloud computing, no GPU, no admin rights required.***

Local LLM Notepad is an open-source, offline plug-and-play app for running local large-language models. Drop the single bundled .exe onto a USB stick, walk up to any computer, and start chatting, brainstorming, or drafting documents. 


![Portable One‑File Build](img/directory.png)

![combined_gif](img/Combined_gif.gif)


# Why you’ll love it

## 🔌 Portable

Drop the one‑file EXE and your .gguf model onto a flash drive; run on any Windows PC without admin rights.

## 🪶 Clean UI

Two‑pane layout: type prompts below, watch token‑streamed answers above—no extra chrome.

## 🔍 Source‑word under‑lining

Every word or number you wrote in your prompt is automatically bold‑underlined in the model’s reply. Ctrl+left click on them to view them in a separate window. Handy for fact‑checking summaries, tables, or data extractions.

## 💾 Save/Load chats

One‑click JSON export keeps conversations with the model portable alongside the EXE.

## ⚡ Llama.cpp inside

CPU‑only by default for max compatibility.

## 🎹 Hot‑keys

| Keyboard shortcuts | Action |
|------|------|
| `Shift` + `Enter` | send |
| `Ctrl` + `Z` | stop |
| `Ctrl` + `F` | find |
| `Ctrl` + `X` | clear chat history |
| `Ctrl` + `Mouse-Wheel` | zoom |


# Quick Start

Download `Local_LLM_Notepad-portable.exe` from the Releases page.

Copy the `.exe` and a compatible `.gguf` model (e.g. `gemma-3-1b-it-Q4_K_M.gguf`) onto your USB.

Double‑click the `.exe` on any Windows computer. First launch caches the model into RAM; subsequent prompts stream instantly.

Need another model? Use `File ▸ Select Model…` and point to a different `.gguf`.


# Download links:


| File | Link | Notes |
|------|------|-------|
| **Local_LLM_Notepad-portable.exe** | [Direct download (v1.0.1)](https://github.com/runzhouye/Local_LLM_Notepad/releases/tag/v1.0.1) | ~45 MB, contains everything needed to run LLM on Windows computer |
| **gemma-3-1b-it-Q4_K_M.gguf** | [Hugging Face](https://huggingface.co/ggml-org/gemma-3-1b-it-GGUF/tree/main) | Fast CPU model (~0.8 GB) we recommend for first-time users. Achieves ~20 tokens/second on an i7-10750H CPU  ![HF_screenshot](img/HF_models.png)|
| **Icon (optional)** | [Notepad icon PNG](https://upload.wikimedia.org/wikipedia/commons/c/c9/Windows_Notepad_icon.png) | Save as `Icon.png` next to the EXE and it will be used automatically |


# Feature Details

### Portable One‑File Build

![Portable One‑File Build](img/directory.png)


### Automated Source Highlighting (Ctrl + click)

Every word, number you used in the prompt is bold‑underlined in the LLM answer.  

Ctrl + click any under‑lined word to open a side window with every single prompt that contained it—great for tracing sources.

![bold_text_demo](img/bold_text_demo.gif)

### Ctrl + S to Send text to LLM

![CtrlS](img/CtrlS.gif)

### Ctrl + Z to stop LLM generation

![CtrlZ](img/CtrlZ.gif)

### Ctrl + F to find in chat history

![CtrlF](img/CtrlF.gif)

### Ctrl + X to clear chat history

![CtrlX](img/CtrlX.gif)

### Ctrl + P to edit system prompt anytime

![change_syst_prompt](img/change_syst_prompt.gif)

### File ▸ Save/Load chat history

![Load_chat](img/Load_chat.gif)


# (Optional) Building your own portable `.exe`
The process is identical to the main repository:
`https://github.com/runzhouye/Local_LLM_Notepad` (only directory names and library versions in `requirements.txt` differ).

### 1. Clone repository
```bash
git clone https://github.com/yoken-do/local-llm-notepad.git
```
### 2. Go to the directory
```bash
cd local-llm-notepad.
```
### 3. Create environment
```bash
python -m venv .venv
```
### 4. Activate environment
```bash
.venv\Scripts\activate
```
### 5. Install dependecies
```bash
pip install -r requirements.txt
```

### 6. Go to `src` directory
```bash
cd src
```

### 7. Bundle everything
```bash
pyinstaller --onefile --noconsole --additional-hooks-dir=. main.py
```


# Known Issues in the [`main`](https://github.com/runzhouye/Local_LLM_Notepad) repository 
These issues remain unresolved in our version as well.
## Windows 11
1. The `Ctrl` + `S` shortcut does not work when launching the `.exe` file.
2. When running: 
```bash
pip install -r requirements.txt
```
The following error occurs:
```bash
ERROR: Ignored the following yanked versions: 0.2.8
ERROR: Could not find a version that satisfies the requirement llama-cpp-python<1.0,>=0.5.0 (from versions: 0.1.1, 0.1.2, 0.1.3, 0.1.4, 0.1.5, 0.1.6, 0.1.7, 0.1.8, 0.1.9, 0.1.10, 0.1.11, 0.1.12, 0.1.13, 0.1.14, 0.1.15, 0.1.16, 0.1.17, 0.1.18, 0.1.19, 0.1.20, 0.1.21, 0.1.22, 0.1.23, 0.1.24, 0.1.25, 0.1.26, 0.1.27, 0.1.28, 0.1.29, 0.1.30, 0.1.31, 0.1.32, 0.1.33, 0.1.34, 0.1.35, 0.1.36, 0.1.37, 0.1.38, 0.1.39, 0.1.40, 0.1.41, 0.1.42, 0.1.43, 0.1.44, 0.1.45, 0.1.46, 0.1.47, 0.1.48, 0.1.49, 0.1.50, 0.1.51, 0.1.52, 0.1.53, 0.1.54, 0.1.55, 0.1.56, 0.1.57, 0.1.59, 0.1.61, 0.1.62, 0.1.63, 0.1.64, 0.1.65, 0.1.66, 0.1.67, 0.1.68, 0.1.69, 0.1.70, 0.1.71, 0.1.72, 0.1.73, 0.1.74, 0.1.76, 0.1.77, 0.1.78, 0.1.79, 0.1.80, 0.1.81, 0.1.82, 0.1.83, 0.1.84, 0.1.85, 0.2.0, 0.2.1, 0.2.2, 0.2.3, 0.2.4, 0.2.5, 0.2.6, 0.2.7, 0.2.9, 0.2.10, 0.2.11, 0.2.12, 0.2.13, 0.2.14, 0.2.15, 0.2.16, 0.2.17, 0.2.18, 0.2.19, 0.2.20, 0.2.22, 0.2.23, 0.2.24, 0.2.25, 0.2.26, 0.2.27, 0.2.28, 0.2.29, 0.2.30, 0.2.31, 0.2.32, 0.2.33, 0.2.34, 0.2.35, 0.2.36, 0.2.37, 0.2.38, 0.2.39, 0.2.40, 0.2.41, 0.2.42, 0.2.43, 0.2.44, 0.2.45, 0.2.46, 0.2.47, 0.2.48, 0.2.49, 0.2.50, 0.2.51, 0.2.52, 0.2.53, 0.2.54, 0.2.55, 0.2.56, 0.2.57, 0.2.58, 0.2.59, 0.2.60, 0.2.61, 0.2.62, 0.2.63, 0.2.64, 0.2.65, 0.2.66, 0.2.67, 0.2.68, 0.2.69, 0.2.70, 0.2.71, 0.2.72, 0.2.73, 0.2.74, 0.2.75, 0.2.76, 0.2.77, 0.2.78, 0.2.79, 0.2.80, 0.2.81, 0.2.82, 0.2.83, 0.2.84, 0.2.85, 0.2.86, 0.2.87, 0.2.88, 0.2.89, 0.2.90, 0.3.0, 0.3.1, 0.3.2, 0.3.3, 0.3.4, 0.3.5, 0.3.6, 0.3.7, 0.3.8, 0.3.9)
ERROR: No matching distribution found for llama-cpp-python<1.0,>=0.5.0
```
