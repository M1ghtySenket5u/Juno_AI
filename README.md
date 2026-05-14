# Juno AI

Juno AI is a **Linux Mint–friendly desktop chat companion**. She speaks with a calm, mission-focused tone (inspired loosely by popular game characters — original wording only) and ships with a **full offline curriculum**: Linux concepts, Linux Mint workflows, common terminal commands, how to work confidently in a shell, and a complete **apple pie** recipe — no account or network required for that core experience.

**Everything for the app lives in one folder** (the `juno-ai` directory): Python sources, launcher scripts, desktop template, install helper, `.deb` builder, and docs.

## How Juno responds

| Mode | What happens |
|------|----------------|
| **Offline (default)** | Built-in answers from `juno_offline.py` — facts, Mint notes, command glossaries, terminal drills, apple pie checklist. |
| **OpenAI (optional)** | If you add your own API key in Settings, replies stream from OpenAI Chat Completions (for example `gpt-4o-mini`). |
| **Local HTTP API (advanced)** | If you point Settings at any **OpenAI-compatible** `/v1` Chat Completions server on your machine or LAN, Juno can stream from there. Some operators use local stacks that expose that shape of API; configure base URL and model id to match your environment. |

If a live model call fails, Juno **falls back** to the same offline library so the window stays useful.

The interface uses a **galaxy background** with clean typography and **Japanese palette accents** (indigo, vermilion, gold).

---

## What you need

- **Offline only:** Python 3 + PyQt6 (installed by the helper script below). No API keys.
- **OpenAI:** your own [API key](https://platform.openai.com/api-keys) and network when chatting.
- **Local HTTP API:** whatever server you run; Juno only needs a reachable base URL and model name.

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

### 5. Optional: connect a live model

1. In Juno: **File → Settings…**
2. Leave **Offline** selected to stay on built-in lessons, **or** choose **OpenAI** and paste a key, **or** choose **Local HTTP API** and set base URL + model id to match your stack.
3. Click **Save**.

On first launch, **Offline** is already selected — you can learn Mint and Linux immediately.

When you exit, Juno shows a **mission-style farewell plaque** for **5 seconds** (with a live countdown) before the app closes — lines like **“See you later, partner”** and **“Race you to the moon”** are in the rotation along with a few similar sign-offs.

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
| `juno_offline.py` | Offline facts, Mint notes, commands, terminal primer, apple pie |
| `juno_environment.py` | Detects missing pieces (Python, venv, imports) and suggests `apt` / install commands |
| `setup_wizard.py` | Step-by-step setup dialog with copy-to-clipboard terminal blocks |
| `galaxy_widget.py` | Painted galaxy / starfield background |
| `mint_fun_facts.py` | Mint trivia for startup rotation |
| `juno_system_prompt.py` | Persona and safety rules for live models |
| `config_store.py` | Saves `~/.config/juno-ai/config.json` (defaults to offline) |
| `requirements.txt` | Python dependencies |
| `juno-ai.sh` | Launcher (uses `.venv` when present) |
| `juno-ai.desktop.template` | Template for the menu entry |
| `install-linux.sh` | One-shot local install + menu shortcut |
| `build-deb.sh` | Builds a simple `.deb` |
| `INSTALL.md` | Short numbered install steps |

On the **first launch** with a **new** `~/.config/juno-ai/config.json`, Juno opens a short **setup guide** (four steps: health check, install commands, launch command, how to chat). You can reopen it anytime from **Help → Setup guide…**. If your config file predates this feature, the guide stays skipped so you are not interrupted.

---

## Medical and safety note

Juno can discuss **general** medical or biology topics for education when a live model is enabled, but she is **not** a clinician. For personal diagnosis, treatment, or emergencies, contact a qualified professional or local emergency services.

---

## Troubleshooting

- **OpenAI errors** — Confirm your key in Settings; on failure Juno falls back to offline answers automatically.
- **Local HTTP API errors** — Confirm the base URL responds on your machine, the model id exists on that server, and firewalls allow localhost/LAN access as needed. Failed calls also fall back offline.
- **PyQt6 import errors** — Re-run `./install-linux.sh` or manually: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

---

## License

Use and modify for personal use. Third-party APIs and servers have their own terms; Juno AI does not ship any model weights.
