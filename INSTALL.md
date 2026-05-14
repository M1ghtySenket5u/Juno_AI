# Juno AI — installation guide (Linux Mint)

Follow these steps in order. The full project also has a [README.md](README.md) with troubleshooting and feature overview.

## 1. Put the project in your home folder

Example:

```bash
mkdir -p ~/juno-ai
# copy all project files into ~/juno-ai (main.py, requirements.txt, etc.)
cd ~/juno-ai
```

## 2. Install Python tools (once per machine)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

## 3. Run the installer script

```bash
chmod +x install-linux.sh juno-ai.sh build-deb.sh
./install-linux.sh
```

This creates `.venv`, installs dependencies, and adds **Juno AI** to your application menu.

## 4. Launch Juno

- Open the **menu**, search **Juno AI**, click it, **or**
- Run `~/juno-ai/juno-ai.sh` from a terminal.

## 5. Configure the AI

1. **File → Settings…**
2. Pick **OpenAI** (needs API key) or **Ollama (local)**.
3. Save.

## Optional: `.deb` package

From the project root:

```bash
chmod +x build-deb.sh
./build-deb.sh
sudo apt install ./juno-ai_1.0.0_all.deb
```

Then launch **Juno AI** from the menu or run `juno-ai` in a terminal.
