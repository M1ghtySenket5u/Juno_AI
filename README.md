# Juno AI

Juno AI is a **Linux Mint–friendly desktop chat companion**. She helps newcomers learn Mint, answers questions across many topics, and speaks with a calm, mission-focused tone (inspired loosely by popular game characters — original wording only).

**Everything for the app lives in one folder** (the `juno-ai` directory): Python sources, launcher scripts, desktop template, install helper, `.deb` builder, and docs — no extra subpackages to hunt for.

- **Cloud:** OpenAI Chat Completions API (models such as `gpt-4o-mini`), with **streaming** replies.
- **Local / offline (LAN):** [Ollama](https://ollama.com/) via the OpenAI-compatible endpoint — no OpenAI account required if your PC runs the model.

The interface uses a **galaxy background** with **NASA-clean typography** and **Japanese palette accents** (indigo, vermilion, gold).

---

## What you need

| Mode | Requirements |
|------|----------------|
| **OpenAI** | [API key](https://platform.openai.com/api-keys) and network access |
| **Ollama** | Ollama installed and a model pulled (e.g. `ollama pull llama3.2`) |

---

## Step-by-step install (Linux Mint — recommended)

These steps assume you copied the whole `juno-ai` folder to your computer (for example `~/juno-ai`).

### 1. Install system Python (if needed)

Open **Terminal** and run:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

### 2. Go into the project folder

```bash
cd ~/juno-ai
```

(Change the path if you put the folder somewhere else.)

### 3. Run the installer script

```bash
chmod +x install-linux.sh juno-ai.sh build-deb.sh
./install-linux.sh
```

This will:

- Create a **virtual environment** in `.venv`
- Install Python dependencies (`PyQt6`, `openai`, …)
- Install a **menu shortcut** so you can open Juno from the **Cinnamon applications menu**

### 4. Start Juno AI

- Press the **Super** key, type **Juno AI**, and click the icon, **or**
- Run:

```bash
~/juno-ai/juno-ai.sh
```

### 5. Configure the AI backend

1. In Juno: **File → Settings…**
2. Choose **OpenAI** or **Ollama (local)**.
3. **OpenAI:** paste your API key and pick a model name (default `gpt-4o-mini`).
4. **Ollama:** set base URL (default `http://127.0.0.1:11434`) and the model name you pulled.
5. Click **Save**.

You are done. Ask Juno anything; she opens with a **random Linux Mint fun fact** and, when you exit, shows a **mission-style farewell plaque** for **5 seconds** (with a live countdown) before the app closes — lines like **“See you later, partner”** and **“Race you to the moon”** are in the rotation along with a few similar sign-offs.

---

## Optional: install from a `.deb` package

On a machine with `dpkg-deb` (Mint has it):

```bash
cd ~/juno-ai
chmod +x build-deb.sh
./build-deb.sh
sudo apt install ./juno-ai_1.0.0_all.deb
```

The package installs to `/opt/juno-ai` and runs `postinst` to create the venv and `pip install` (needs **internet** during install). Then launch **Juno AI** from the menu or run `juno-ai` in a terminal.

---

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| **Enter** | Send message |
| **Shift+Enter** | New line in the message box |
| **Ctrl+Enter** | Send (same as Enter) |

---

## Files in this folder

| File | Purpose |
|------|---------|
| `main.py` | Application UI and logic |
| `galaxy_widget.py` | Painted galaxy / starfield background |
| `mint_fun_facts.py` | Mint trivia for startup |
| `juno_system_prompt.py` | Persona and safety rules for the model |
| `config_store.py` | Saves `~/.config/juno-ai/config.json` |
| `requirements.txt` | Python dependencies |
| `juno-ai.sh` | Launcher (uses `.venv` when present) |
| `juno-ai.desktop.template` | Template for the menu entry |
| `install-linux.sh` | One-shot local install + menu shortcut |
| `build-deb.sh` | Builds a simple `.deb` |
| `INSTALL.md` | Short numbered install steps (same flow as above, easy to print) |

---

## Medical and safety note

Juno can discuss **general** medical or biology topics for education, but she is **not** a clinician. For personal diagnosis, treatment, or emergencies, contact a qualified professional or local emergency services.

---

## Troubleshooting

- **“Set your OpenAI API key”** — Open **File → Settings** and save a valid key, or switch to Ollama.
- **Ollama errors** — Run `ollama serve`, confirm `curl http://127.0.0.1:11434` responds, and that you ran `ollama pull <model>` for the model name in Settings.
- **PyQt6 import errors** — Re-run `./install-linux.sh` or manually: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

---

## License

Use and modify for personal use. OpenAI and Ollama have their own terms; Juno AI does not ship any model weights.
