"""Juno AI — built-in offline answers (no network, no model weights).

Teaches Linux, Linux Mint, common shell commands, terminal basics, and includes
a classic apple pie walkthrough. All wording is original to Juno AI.
"""

from __future__ import annotations

import html
import random
import re
import textwrap
from typing import Iterable

from mint_fun_facts import MINT_FUN_FACTS, random_mint_fact

# Longer keys first so e.g. "rm -r" wins over "rm"
LINUX_COMMAND_HELP: dict[str, str] = {
    "rm -rf /": (
        "Extremely dangerous: recursively deletes from the filesystem root. "
        "Never run this as a joke. Recovery is painful or impossible without backups."
    ),
    "rm -r": "Removes a directory and everything inside it. Double-check the path first.",
    "rm -f": "Removes files without prompting; combine with care.",
    "rm": "Deletes files. There is no undo from the trash like a file manager—gone means gone.",
    "chmod +x": "Marks a file as executable (often used on scripts you trust).",
    "chmod": "Changes who may read, write, or execute a file or directory (permissions bits).",
    "chown": "Changes the owner (and optionally group) of a file—usually needs elevated rights.",
    "chgrp": "Changes the group ownership of a file or directory.",
    "touch": "Creates an empty file if missing, or updates its timestamp if it already exists.",
    "head": "Prints the first lines of a file (great for peeking at logs).",
    "tail": "Prints the last lines; `tail -f` follows a growing log in real time.",
    "wc": "Counts lines, words, or bytes—handy for quick file stats.",
    "sort": "Sorts lines of text; often chained with other tools.",
    "uniq": "Collapses adjacent duplicate lines (often after `sort`).",
    "tee": "Writes stdin to a file and still passes it through to stdout—useful with sudo.",
    "find": "Walks directories matching names, types, or dates—powerful, read examples before wildcards.",
    "locate": "Fast name search using a prebuilt database (`updatedb` refreshes it).",
    "which": "Shows the path of the executable that would run for a command name.",
    "whereis": "Locates binary, source, and manual page files for a command.",
    "history": "Lists recent shell commands from this session and past sessions (if saved).",
    "alias": "Defines a short nickname for a longer command sequence.",
    "export": "Sets environment variables visible to child processes.",
    "source": "Runs a shell script in the current shell (often used after editing `~/.bashrc`).",
    "echo": "Prints text or variable values—simple but essential for scripts and quick checks.",
    "printf": "Formatted printing; safer than `echo` in scripts when you need precise control.",
    "read": "Reads a line of input from the user in scripts.",
    "sleep": "Pauses for a given number of seconds—common in scripts and demos.",
    "jobs": "Lists background tasks started from this shell.",
    "fg": "Brings a background job to the foreground.",
    "bg": "Continues a stopped job in the background.",
    "nohup": "Keeps a command running after you disconnect (output often goes to `nohup.out`).",
    "curl": "Transfers data from URLs—downloads, API checks, and more.",
    "wget": "Non-interactive file downloader; good for mirrors and resumes in some modes.",
    "ssh": "Secure remote shell—encrypts your session to another machine.",
    "scp": "Secure copy over SSH between machines.",
    "rsync": "Smart file sync with deltas—great for backups when used carefully.",
    "tar": "Archives many files into one `.tar` (often gzipped as `.tar.gz`).",
    "gzip": "Compresses files (typically one file per archive).",
    "gunzip": "Decompresses `.gz` files.",
    "zip": "Creates `.zip` archives familiar from other operating systems.",
    "unzip": "Extracts `.zip` archives.",
    "df": "Shows disk space usage per mounted filesystem.",
    "du": "Estimates space used by directories—pair with `-h` for human-readable sizes.",
    "free": "Shows RAM and swap usage.",
    "top": "Live-updating list of processes by resource use.",
    "htop": "Friendlier, colorful `top` if installed.",
    "ps": "Snapshot of running processes—often `ps aux` for detail.",
    "kill": "Sends a signal to a process ID; default tries to stop it politely.",
    "killall": "Signals processes by name—be sure you matched the right program.",
    "systemctl": "Controls systemd services on many modern Linux desktops (start/stop/status).",
    "journalctl": "Reads systemd logs—powerful filter options exist.",
    "apt update": "Refreshes package index lists from repositories (does not upgrade packages yet).",
    "apt upgrade": "Installs newer versions of packages already on the system.",
    "apt install": "Installs named packages from configured repositories.",
    "apt remove": "Removes packages but may leave configuration files behind.",
    "apt purge": "Removes packages and their configuration files.",
    "apt search": "Searches package names and descriptions.",
    "apt show": "Displays metadata for one package.",
    "dpkg -l": "Lists installed Debian-format packages.",
    "snap": "Manages Snap packages if that subsystem is enabled.",
    "flatpak": "Manages Flatpak applications in a sandboxed layout.",
    "sudo": "Runs a single command with administrator privileges—asks for your password.",
    "su": "Switch user; `su -` loads a login shell for root on traditional setups.",
    "whoami": "Prints the current username—sanity check when permissions act weird.",
    "id": "Shows user ID, group ID, and group memberships.",
    "passwd": "Changes your password (or root can change others' with care).",
    "ls -la": "Detailed list including hidden files (`-a`) in long format (`-l`).",
    "ls": "Lists files and folders in the current directory.",
    "cd": "Changes your working directory; `cd` alone often returns to your home folder.",
    "pwd": "Prints the full path of your current directory—know where you are before destructive commands.",
    "mkdir": "Creates directories; `-p` creates parent folders as needed.",
    "rmdir": "Removes empty directories only.",
    "cp": "Copies files or directories (`-r` for trees).",
    "mv": "Moves or renames files and directories.",
    "ln -s": "Creates a symbolic link (shortcut) to another path.",
    "cat": "Dumps entire file contents to the terminal—avoid on huge files.",
    "less": "Pages through a file interactively (space to scroll, `q` to quit).",
    "more": "Older pager; `less` is usually preferred today.",
    "grep": "Searches for text patterns in files or piped input.",
    "cut": "Extracts columns from lines (often with `-d` delimiter).",
    "awk": "Pattern scanning and small programs per line—mini language, very capable.",
    "sed": "Stream editor for substitutions and simple transforms.",
    "tr": "Translates or deletes characters—often used upper/lowercase tricks.",
    "xargs": "Builds commands from stdin lines—watch spaces and quoting.",
    "nano": "Beginner-friendly terminal text editor; on-screen shortcuts use `^` for Ctrl.",
    "vim": "Modal editor with a learning curve; powerful once muscle memory forms.",
    "emacs": "Extensible editor and environment—different key philosophy from Vim.",
    "man": "Opens the manual page for a command—press `q` to leave.",
    "info": "GNU documentation browser—sometimes deeper than `man` for GNU tools.",
    "help": "In Bash, lists shell builtins; for external commands use `man`.",
    "exit": "Ends the current shell session (or closes a terminal tab).",
    "clear": "Clears the visible terminal scroll (Ctrl+L often works too).",
    "reset": "Reinitializes terminal state when characters look corrupted.",
}

LINUX_FACTS: tuple[str, ...] = (
    "The Linux kernel is the core that talks to your hardware; everything else (shells, GUIs, apps) builds on top.",
    "A 'distribution' bundles the kernel with installers, default apps, and a package manager—Mint is one distro among many.",
    "Open source means you can read and modify the code under a license; it does not automatically mean 'no cost,' but Mint is free to download.",
    "The filesystem is a tree starting at `/` (root). Your personal files usually live under `/home/yourname`.",
    "File names are case-sensitive: `Notes.txt` and `notes.txt` can coexist in the same folder.",
    "Hidden files start with a dot (`.bashrc`); `ls` hides them unless you add `-a`.",
    "Permissions use owner/group/others with read/write/execute bits—`ls -l` shows the story at a glance.",
    "Environment variables like `PATH` tell the shell where to search for programs.",
    "Standard input (0), output (1), and error (2) can be redirected with `>`, `>>`, and `2>`.",
    "Cron and systemd timers can schedule recurring tasks—great for backups you would otherwise forget.",
)


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def _pick(seq: tuple[str, ...] | list[str], n: int = 3) -> list[str]:
    if len(seq) <= n:
        return list(seq)
    return random.sample(list(seq), n)


def _command_explanation(user_line: str) -> str | None:
    raw = user_line.strip()
    lower = raw.lower()
    for key in sorted(LINUX_COMMAND_HELP.keys(), key=len, reverse=True):
        lk = key.lower()
        if lower == lk or lower.startswith(lk + " ") or lower.startswith(lk + "\t"):
            expl = LINUX_COMMAND_HELP[key]
            return textwrap.dedent(
                f"""
                **Command check:** `{_esc(raw)}`

                **What it means:** {expl}

                **Quick pattern:** read the manual when in doubt:

                ```bash
                man {lk.split()[0]}
                ```

                I'm on **offline instruments** right now—short briefing mode. If you want flag-by-flag decoding, paste the exact line again and say *which part confuses you*.
                """
            ).strip()
    return None


def _topic_hits(text: str, words: Iterable[str]) -> bool:
    t = text.lower()
    return any(w in t for w in words)


def offline_reply(message: str) -> str:
    """
    Return Markdown-flavored text (plain ** and ``` segments) for Juno's offline voice.
    """
    cleaned = (message or "").strip()
    if not cleaned:
        return (
            "**Juno — offline channel open.**\n"
            "Ask me about **Linux**, **Linux Mint**, a **terminal** habit, a **command**, "
            "or say **apple pie** if you want the galley recipe."
        )

    cmd_hit = _command_explanation(cleaned)
    if cmd_hit:
        return cmd_hit

    low = cleaned.lower()

    # Apple pie (user asked for this explicitly in requirements)
    if _topic_hits(
        low,
        (
            "apple pie",
            "apple-pie",
            "bake a pie",
            "pie crust",
            "apple pie recipe",
            "how to make apple pie",
        ),
    ):
        return textwrap.dedent(
            """
            **Juno — galley briefing: classic apple pie**

            **Hardware (tools):** mixing bowl, peeler, sharp knife, rolling pin, 9-inch pie dish, oven.

            **Ingredients — filling**
            - 6–8 medium tart-sweet apples (a mix is nice), peeled, cored, sliced ~1/4 inch
            - 2/3 cup granulated sugar (adjust to apple sweetness)
            - 2 tbsp all-purpose flour (or 1 tbsp cornstarch) to thicken juices
            - 1 tsp ground cinnamon, pinch nutmeg, pinch salt
            - 1 tbsp lemon juice (brightness)
            - 2 tbsp cold butter, diced (dot on top before the lid)

            **Ingredients — crust (single double-crust batch)**
            - 2 1/2 cups all-purpose flour
            - 1 tsp salt
            - 1 cup cold unsalted butter, cubed (or 3/4 cup butter + shortening mix)
            - 6–10 tbsp ice water, drizzled while tossing

            **Crust procedure**
            1. Whisk flour + salt. Cut in cold butter until pea-sized crumbs form.
            2. Add ice water a spoon at a time until dough holds when squeezed (do not overwork).
            3. Split in two disks, wrap, chill **at least 45 minutes**.

            **Assembly**
            1. Heat oven to **425°F (220°C)**.
            2. Roll one disk, line the dish, chill while you prep apples.
            3. Toss apples with sugar, flour/spices, lemon, salt. Pile into shell; dot with butter.
            4. Roll top crust, vent with slashes or a small center hole, crimp edges, optional egg wash for color.

            **Bake**
            - **425°F** for **15 minutes**, then lower to **375°F (190°C)** until filling bubbles thickly (**40–55 min** more depending on depth).
            - If the rim browns early, shield with foil.

            **Mission rule:** let it cool **1–2 hours** before slicing so the filling sets—patience pays off.

            *(Offline mode — measurements are US-style home baking; scale if you use metric at home.)*
            """
        ).strip()

    # Linux Mint focus
    if _topic_hits(
        low,
        (
            "linux mint",
            "mint cinnamon",
            "mint mate",
            "mint xfce",
            "mint update manager",
            "mint timeshift",
            "mint software manager",
            "mint welcome",
        ),
    ):
        facts = "\n".join(f"- {_esc(x)}" for x in _pick(MINT_FUN_FACTS, 4))
        return textwrap.dedent(
            f"""
            **Juno — Mint sector scan**

            Here are a few **Linux Mint** facts worth knowing:

            {facts}

            **Operator tips**
            - **Update Manager** ranks updates—read the notes before you click everything on day one.
            - **Timeshift** snapshots are your rollback parachute before big changes.
            - **Driver Manager** is the polite front door for proprietary drivers when open drivers are not enough.

            **You typed:** {_esc(cleaned)}

            If you want a tighter answer, tell me whether you're on **Cinnamon, MATE, or Xfce**, and what you're trying to fix or learn.
            """
        ).strip()

    # Terminal literacy
    if _topic_hits(
        low,
        (
            "terminal",
            "shell",
            "bash",
            "command line",
            "how to use the terminal",
            " tty",
            "konsole",
            "gnome-terminal",
            "xfce4-terminal",
        ),
    ):
        return textwrap.dedent(
            f"""
            **Juno — terminal familiarization drill**

            **What the terminal is:** a text window where a **shell** (often Bash) reads commands, runs programs, and prints results. Faster than clicking through nested menus once you know the verbs.

            **Survival kit**
            1. **`pwd`** — confirm your coordinates.
            2. **`ls`** / **`ls -la`** — inventory the sector.
            3. **`cd FolderName`** — move; use quotes if names have spaces.
            4. **`man command`** — on-board documentation.
            5. **`Ctrl+C`** — interrupt a runaway process in the foreground.
            6. **`history`** — scroll back through what you already typed.

            **Safety culture**
            - Read twice before **`rm`**, **`dd`**, or anything touching **`/dev/`**.
            - Prefer copying commands from trustworthy docs; random internet one-liners can be hostile.

            **Your message:** {_esc(cleaned)}

            Paste a command you are unsure about and I will decode it in offline mode.
            """
        ).strip()

    # General Linux
    if _topic_hits(
        low,
        (
            "linux",
            "gnu/linux",
            "ubuntu",
            "debian",
            "kernel",
            "open source",
            "distro",
            "filesystem",
            "permission",
        ),
    ):
        picks = "\n".join(f"- {x}" for x in _pick(LINUX_FACTS, 4))
        return textwrap.dedent(
            f"""
            **Juno — Linux briefing (offline)**

            A few **Linux** fundamentals:

            {picks}

            **You asked:** {_esc(cleaned)}

            Narrow the scope—**networking, disks, audio, permissions, boot, or packages**—and I will go deeper without leaving offline mode.
            """
        ).strip()

    # Command glossary / "what does X mean"
    if _topic_hits(
        low,
        ("what does", "what is", "explain", "meaning of", "definition", "define ")
    ) and re.search(r"\b(ls|cd|pwd|sudo|apt|grep|chmod|man|rm|cp|mv)\b", low):
        return textwrap.dedent(
            """
            **Juno — glossary pass**

            Sounds like you want definitions—here is a compact map:

            - **`ls`** — list directory contents.
            - **`cd`** — change directory.
            - **`pwd`** — print working directory path.
            - **`cp` / `mv` / `rm`** — copy, move/rename, delete (destructive).
            - **`mkdir` / `rmdir`** — create directory; remove if empty.
            - **`grep`** — search text streams or files for patterns.
            - **`chmod` / `chown`** — change permissions or ownership.
            - **`sudo`** — run one command with elevated privileges.
            - **`apt`** — high-level package manager on Mint/Ubuntu bases.
            - **`man`** — manual reader for installed commands.

            Paste the **exact** command string (flags and all) for a line-by-line decode while I'm offline.
            """
        ).strip()

    # Default: rotate a fact + gentle guidance (original voice, not copied from other projects)
    fact = random_mint_fact()
    return textwrap.dedent(
        f"""
        **Juno — offline relay**

        I'm running **without** a live language model link, so this is curated mission data instead of improv.

        **Mint fact for you:** {_esc(fact)}

        **You sent:** {_esc(cleaned)}

        **Try prompts like:**
        - `ls -la` (I'll explain the command)
        - *"How do I use the terminal on Mint?"*
        - *"What is Linux Mint Timeshift?"*
        - *"Apple pie"* (yes, really—full checklist)

        Stay curious—your machine still works when the cloud does not.
        """
    ).strip()
