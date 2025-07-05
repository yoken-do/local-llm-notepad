# Local LLM Notepad



**local-llm-notepad** is an open-source, offline plug-and-play app for running local large-language models. 

![main_img](img/main.gif)

| File | Link | Notes |
|-------|------|------|
| `local-llm-notepad.exe` | [Download](https://github.com/yoken-do/local-llm-notepad/releases/tag/v1.0.2) | ~25 MB, contains everything needed to run LLM on Windows computer |
| `gemma-3-1b-it-Q4_K_M.gguf` | [Download](https://huggingface.co/ggml-org/gemma-3-1b-it-GGUF/tree/main) | Fast CPU model (~0.8 GB) we recommend for first-time users. Achieves ~20 tokens/second on an i7-10750H CPU |


# Why you’ll love it

## 🔌 Portable

Drop the one‑file EXE and your .gguf model onto a flash drive; run on any Windows PC without admin rights.

## 🪶 Clean UI

Two‑pane layout: type prompts below, watch token‑streamed answers above—no extra chrome.

## 💾 Save/Load chats

One‑click JSON export keeps conversations with the model portable alongside the EXE.

## ⚡ Llama.cpp inside

CPU‑only by default for max compatibility.

## 🎹 Hot‑keys (Optional)

| Keyboard shortcuts | Action |
|------|------|
| `Shift` + `Return` | send |
| `Ctrl` + `Z` | stop |
| `Ctrl` + `F` | find |
| `Ctrl` + `X` | clear chat history |
| `Ctrl` + `Mouse-Wheel` | zoom |
| `Ctrl` + `P` | edit system prompt |


# Run app from source code
The process is identical to the [`main`](https://github.com/runzhouye/Local_LLM_Notepad) repository (only directory names and library versions in `requirements.txt` differ).

If you're using `uv`, switch to the [`branch`](https://github.com/yoken-do/local-llm-notepad/tree/uv)

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

### 6. Go to src directory

```bash
cd src
```

### 7. Compile
```bash
nuitka --standalone --enable-plugin=tk-inter --windows-console-mode=disable --onefile --output-filename=local-llm-notepad.exe main.py
```

### 8. Add [`gemma-3-1b-it-Q4_K_M.gguf`](https://huggingface.co/ggml-org/gemma-3-1b-it-GGUF/tree/main) (the default model) and run app
```bash
local-llm-notepad.exe
```
