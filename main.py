#!/usr/bin/env python3
"""Juno AI — Linux Mint desktop buddy (OpenAI streaming + optional Ollama)."""

from __future__ import annotations

import random
import sys
from typing import Any

from PyQt6.QtCore import QEvent, QObject, QThread, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QAction, QCloseEvent, QFont, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
)

from openai import OpenAI

from config_store import load_config, save_config
from galaxy_widget import GalaxyBackdrop
from juno_system_prompt import JUNO_SYSTEM_PROMPT
from mint_fun_facts import random_mint_fact

# NASA × samurai × galaxy UI tokens
COLOR_TITLE = "#F2F6FF"
COLOR_SUBTITLE = "#B8C5E0"
COLOR_ASSISTANT = "#7EC8E3"
COLOR_USER = "#F4F8FF"
COLOR_GOLD = "#D4AF37"
COLOR_VERMILION = "#C73E4A"
COLOR_PANEL_BG = "rgba(8, 14, 32, 0.92)"
COLOR_CHAT_BG = "rgba(4, 10, 24, 0.94)"
COLOR_ERROR = "#FF6B6B"

FAREWELL_MS = 5000

# Mission-style sign-offs (includes your two classics, plus a few in the same voice).
_FAREWELL_LINES: tuple[str, ...] = (
    "See you later, partner.",
    "Race you to the moon.",
    "See you later, partner — trajectory looks clean from up here.",
    "Race you to the moon. Try not to take a shortcut through the asteroid belt.",
    "Signing off for now. See you later, partner.",
    "Race you to the moon... I'll spot you the head start.",
    "Mission clock paused. See you later, partner.",
    "Race you to the moon — throttle smooth, yeah?",
)


class EnterSendsFilter(QObject):
    """Return/Enter sends; Shift+Return inserts a newline."""

    def __init__(self, send_callback) -> None:
        super().__init__()
        self._send = send_callback

    def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:  # noqa: ARG002
        if event is not None and event.type() == QEvent.Type.KeyPress:
            ke = event
            if ke.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if ke.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    return False
                self._send()
                return True
        return False


def _openai_compatible_v1_base(url: str) -> str:
    u = (url or "http://127.0.0.1:11434").strip().rstrip("/")
    return u if u.endswith("/v1") else f"{u}/v1"


class StreamingWorker(QObject):
    chunk = pyqtSignal(str)
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(
        self,
        *,
        provider: str,
        api_key: str,
        model: str,
        ollama_base: str,
        ollama_model: str,
        messages: list[dict[str, Any]],
    ) -> None:
        super().__init__()
        self.provider = provider.lower().strip()
        self.api_key = api_key
        self.model = model
        self.ollama_base = ollama_base
        self.ollama_model = ollama_model
        self.messages = messages

    def run(self) -> None:
        try:
            if self.provider == "ollama":
                client = OpenAI(
                    api_key="ollama",
                    base_url=_openai_compatible_v1_base(self.ollama_base),
                )
                use_model = self.ollama_model.strip() or "llama3.2"
            else:
                client = OpenAI(api_key=self.api_key)
                use_model = self.model.strip() or "gpt-4o-mini"

            stream = client.chat.completions.create(
                model=use_model,
                messages=self.messages,
                temperature=0.75,
                stream=True,
            )
            parts: list[str] = []
            for event in stream:
                choice = event.choices[0] if event.choices else None
                if choice is None:
                    continue
                delta = getattr(choice, "delta", None)
                piece = getattr(delta, "content", None) if delta is not None else None
                if piece:
                    parts.append(piece)
                    self.chunk.emit(piece)
            self.finished.emit("".join(parts))
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Juno AI — Settings")
        self.setMinimumWidth(480)
        cfg = load_config()

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.provider = QComboBox()
        self.provider.addItems(["OpenAI", "Ollama (local)"])
        prov = (cfg.get("provider") or "openai").lower()
        self.provider.setCurrentIndex(1 if prov == "ollama" else 0)

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("sk-… (OpenAI only)")
        self.api_key.setText(cfg.get("api_key", ""))

        self.model = QLineEdit()
        self.model.setPlaceholderText("gpt-4o-mini")
        self.model.setText(cfg.get("model", "gpt-4o-mini"))

        self.ollama_base = QLineEdit()
        self.ollama_base.setPlaceholderText("http://127.0.0.1:11434")
        self.ollama_base.setText(cfg.get("ollama_base", "http://127.0.0.1:11434"))

        self.ollama_model = QLineEdit()
        self.ollama_model.setPlaceholderText("llama3.2")
        self.ollama_model.setText(cfg.get("ollama_model", "llama3.2"))

        form.addRow("Provider", self.provider)
        form.addRow("OpenAI API key", self.api_key)
        form.addRow("OpenAI model", self.model)
        form.addRow("Ollama base URL", self.ollama_base)
        form.addRow("Ollama model", self.ollama_model)
        layout.addLayout(form)

        hint = QLabel(
            "OpenAI: https://platform.openai.com/api-keys — stored in ~/.config/juno-ai/config.json\n"
            "Ollama: run `ollama serve` and `ollama pull <model>`; uses the /v1 OpenAI-compatible API."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLOR_SUBTITLE}; font-size: 11px;")
        layout.addWidget(hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._apply_dialog_style()

    def _apply_dialog_style(self) -> None:
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {COLOR_PANEL_BG};
            }}
            QLabel {{
                color: {COLOR_TITLE};
            }}
            QLineEdit {{
                background-color: rgba(3, 8, 20, 0.9);
                color: {COLOR_USER};
                border: 1px solid {COLOR_GOLD};
                border-radius: 6px;
                padding: 6px;
            }}
            QComboBox {{
                background-color: rgba(3, 8, 20, 0.9);
                color: {COLOR_USER};
                border: 1px solid {COLOR_VERMILION};
                border-radius: 6px;
                padding: 6px;
            }}
            """
        )

    def _save(self) -> None:
        is_ollama = self.provider.currentIndex() == 1
        key = self.api_key.text().strip()
        if not is_ollama and not key:
            QMessageBox.warning(self, "Juno AI", "OpenAI mode needs an API key.")
            return
        data = load_config()
        data["provider"] = "ollama" if is_ollama else "openai"
        data["api_key"] = key
        data["model"] = self.model.text().strip() or "gpt-4o-mini"
        data["ollama_base"] = self.ollama_base.text().strip() or "http://127.0.0.1:11434"
        data["ollama_model"] = self.ollama_model.text().strip() or "llama3.2"
        save_config(data)
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Juno AI")
        self.resize(780, 700)

        self._thread: QThread | None = None
        self._worker: StreamingWorker | None = None
        self._history: list[dict[str, str]] = []
        self._pending_user = ""
        self._streaming = False
        self._quit_after_farewell = False
        self._farewell_active = False
        self._farewell_dialog: QDialog | None = None
        self._farewell_countdown_timer: QTimer | None = None

        backdrop = GalaxyBackdrop()
        self.setCentralWidget(backdrop)
        outer = QVBoxLayout(backdrop)
        outer.setContentsMargins(20, 20, 20, 20)

        shell = QFrame()
        shell.setObjectName("mainShell")
        sh = QVBoxLayout(shell)
        sh.setContentsMargins(18, 18, 18, 18)

        title = QLabel("JUNO  AI")
        title.setObjectName("titleLabel")
        tf = QFont()
        tf.setPointSize(20)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet(
            f"color: {COLOR_TITLE}; border-bottom: 2px solid {COLOR_VERMILION}; "
            "padding-bottom: 6px; letter-spacing: 4px;"
        )
        sh.addWidget(title)

        subtitle = QLabel(
            "Mission control for Linux Mint — OpenAI or local Ollama. "
            "Enter sends · Shift+Enter newline."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"color: {COLOR_SUBTITLE}; font-size: 12px;")
        sh.addWidget(subtitle)

        self.chat = QTextBrowser()
        self.chat.setOpenExternalLinks(True)
        sh.addWidget(self.chat, stretch=1)

        row = QHBoxLayout()
        self.input = QTextEdit()
        self.input.setPlaceholderText("Message Juno…")
        self.input.setFixedHeight(92)
        self._enter_filter = EnterSendsFilter(self._send)
        self.input.installEventFilter(self._enter_filter)
        row.addWidget(self.input, stretch=1)

        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedWidth(100)
        self.send_btn.clicked.connect(self._send)
        row.addWidget(self.send_btn)
        sh.addLayout(row)

        self.status = QLabel("")
        self.status.setStyleSheet(f"color: {COLOR_SUBTITLE}; font-size: 12px;")
        sh.addWidget(self.status)

        outer.addWidget(shell, stretch=1)

        self._apply_theme()
        self._welcome_sequence()

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        act_settings = QAction("Settings…", self)
        act_settings.triggered.connect(self._open_settings)
        file_menu.addAction(act_settings)
        act_quit = QAction("Quit", self)
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            f"""
            QMenuBar {{
                background-color: rgba(6, 12, 28, 0.95);
                color: {COLOR_TITLE};
                border-bottom: 1px solid {COLOR_GOLD};
            }}
            QMenuBar::item:selected {{
                background-color: {COLOR_VERMILION};
            }}
            QMenu {{
                background-color: rgba(8, 14, 32, 0.98);
                color: {COLOR_TITLE};
                border: 1px solid {COLOR_GOLD};
            }}
            QFrame#mainShell {{
                background-color: {COLOR_PANEL_BG};
                border: 1px solid rgba(201, 162, 39, 0.45);
                border-left: 4px solid {COLOR_VERMILION};
                border-radius: 14px;
            }}
            QTextBrowser {{
                background-color: {COLOR_CHAT_BG};
                color: {COLOR_ASSISTANT};
                border: 1px solid rgba(126, 200, 227, 0.35);
                border-radius: 10px;
                padding: 10px;
                font-family: "Noto Sans", "Liberation Sans", "Segoe UI", sans-serif;
                font-size: 14px;
            }}
            QTextEdit {{
                background-color: rgba(3, 10, 24, 0.92);
                color: {COLOR_USER};
                border: 1px solid {COLOR_GOLD};
                border-radius: 10px;
                padding: 10px;
                font-family: "Noto Sans Mono", "Liberation Mono", monospace;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1a5080, stop:1 #0f3558);
                color: {COLOR_USER};
                border: 1px solid {COLOR_GOLD};
                border-radius: 10px;
                padding: 12px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: #2568a0;
            }}
            QPushButton:disabled {{
                background-color: #2a3f55;
                color: #8899aa;
                border-color: #555;
            }}
            """
        )

    def _welcome_sequence(self) -> None:
        fact = random_mint_fact()
        self._append_html(
            f'<p style="color:{COLOR_ASSISTANT}; margin: 6px 0;">'
            f"<b>Juno</b> — <i>Mint telemetry ping:</i> {_escape_html(fact)}</p>"
        )
        self._append_html(
            f'<p style="color:{COLOR_ASSISTANT}; margin: 6px 0;">'
            f"<b>Juno</b> — Systems green. Ask about Mint, or throw me a curveball — I can handle it.</p>"
        )

    def _append_user_message(self, text: str) -> None:
        user_html = (
            f'<p style="color:{COLOR_USER}; margin: 8px 0;"><b>You</b> — '
            f"{_escape_html(text)}</p><br>"
        )
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(user_html)
        self.chat.setTextCursor(cursor)

    def _append_html(self, html: str) -> None:
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(html + "<br>")
        self.chat.setTextCursor(cursor)

    def _begin_streaming_assistant(self) -> None:
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(
            f'<div style="color:{COLOR_ASSISTANT}; margin: 8px 0;">'
            f"<b>Juno</b> — "
        )
        self.chat.setTextCursor(cursor)
        self._streaming = True

    def _append_stream_chunk(self, chunk: str) -> None:
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(_escape_html(chunk))
        self.chat.setTextCursor(cursor)
        self.chat.verticalScrollBar().setValue(self.chat.verticalScrollBar().maximum())

    def _end_streaming_assistant(self) -> None:
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml("</div><br>")
        self.chat.setTextCursor(cursor)
        self._streaming = False

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Juno AI", "Settings saved.")

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._quit_after_farewell:
            event.accept()
            return
        if self._farewell_active:
            event.ignore()
            return
        event.ignore()
        self._farewell_active = True
        self._show_farewell_plaque()
        QTimer.singleShot(FAREWELL_MS, self._complete_farewell_and_quit)

    def _show_farewell_plaque(self) -> None:
        """HUD-style farewell so it matches Juno's NASA x samurai vibe; stays on screen for 5 seconds."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Juno")
        dlg.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(0, 0, 0, 0)

        plaque = QFrame()
        plaque.setStyleSheet(
            f"""
            QFrame {{
                background-color: rgba(6, 12, 28, 0.96);
                border: 2px solid {COLOR_GOLD};
                border-left: 6px solid {COLOR_VERMILION};
                border-radius: 14px;
                padding: 20px 24px;
            }}
            """
        )
        pv = QVBoxLayout(plaque)

        header = QLabel("JUNO — END OF MISSION")
        hf = QFont()
        hf.setPointSize(10)
        hf.setBold(True)
        header.setFont(hf)
        header.setStyleSheet(f"color: {COLOR_SUBTITLE}; letter-spacing: 3px;")
        pv.addWidget(header)

        line = random.choice(_FAREWELL_LINES)
        body = QLabel(line)
        bf = QFont()
        bf.setPointSize(15)
        bf.setBold(True)
        body.setFont(bf)
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {COLOR_ASSISTANT}; padding-top: 8px;")
        pv.addWidget(body)

        tag = QLabel("Stay curious on Mint. Same channel next time.")
        tag.setWordWrap(True)
        tag.setStyleSheet(f"color: {COLOR_SUBTITLE}; font-size: 11px; padding-top: 6px;")
        pv.addWidget(tag)

        self._farewell_countdown_label = QLabel("Closing in 5…")
        self._farewell_countdown_label.setStyleSheet(
            f"color: {COLOR_GOLD}; font-size: 12px; padding-top: 10px; font-weight: bold;"
        )
        pv.addWidget(self._farewell_countdown_label)

        outer.addWidget(plaque)

        dlg.adjustSize()
        dlg.resize(max(420, dlg.width()), dlg.height())

        self._farewell_dialog = dlg
        self._farewell_seconds = 5
        self._farewell_countdown_timer = QTimer(dlg)
        self._farewell_countdown_timer.timeout.connect(self._tick_farewell_countdown)
        self._farewell_countdown_timer.start(1000)
        dlg.show()
        host = self.frameGeometry()
        dlg_geo = dlg.frameGeometry()
        dlg_geo.moveCenter(host.center())
        dlg.move(dlg_geo.topLeft())

    def _tick_farewell_countdown(self) -> None:
        self._farewell_seconds -= 1
        if self._farewell_seconds <= 0:
            if self._farewell_countdown_timer:
                self._farewell_countdown_timer.stop()
            return
        if hasattr(self, "_farewell_countdown_label") and self._farewell_countdown_label is not None:
            self._farewell_countdown_label.setText(f"Closing in {self._farewell_seconds}…")

    def _complete_farewell_and_quit(self) -> None:
        if self._farewell_countdown_timer:
            self._farewell_countdown_timer.stop()
            self._farewell_countdown_timer = None
        if self._farewell_dialog is not None:
            self._farewell_dialog.close()
            self._farewell_dialog = None
        self._farewell_active = False
        self._quit_after_farewell = True
        self.close()

    def keyPressEvent(self, event) -> None:  # noqa: ANN001
        if event.key() == Qt.Key.Key_Return and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._send()
            return
        super().keyPressEvent(event)

    def _send(self) -> None:
        text = self.input.toPlainText().strip()
        if not text or self._streaming:
            return
        cfg = load_config()
        provider = (cfg.get("provider") or "openai").lower()
        api_key = (cfg.get("api_key") or "").strip()
        openai_model = (cfg.get("model") or "gpt-4o-mini").strip()
        ollama_base = (cfg.get("ollama_base") or "http://127.0.0.1:11434").strip()
        ollama_model = (cfg.get("ollama_model") or "llama3.2").strip()

        if provider != "ollama" and not api_key:
            QMessageBox.warning(
                self,
                "Juno AI",
                "Set your OpenAI API key in File → Settings, or switch to Ollama.",
            )
            self._open_settings()
            return

        self.input.clear()
        self._append_user_message(text)
        self._pending_user = text
        messages: list[dict[str, str]] = [
            {"role": "system", "content": JUNO_SYSTEM_PROMPT},
            *self._history,
            {"role": "user", "content": text},
        ]

        self.send_btn.setEnabled(False)
        self.status.setText("Juno is composing… (streaming)")
        self._begin_streaming_assistant()

        self._thread = QThread()
        self._worker = StreamingWorker(
            provider=provider,
            api_key=api_key,
            model=openai_model,
            ollama_base=ollama_base,
            ollama_model=ollama_model,
            messages=messages,
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.chunk.connect(self._append_stream_chunk)
        self._worker.finished.connect(self._on_stream_finished)
        self._worker.failed.connect(self._on_stream_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.failed.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _on_stream_finished(self, full: str) -> None:
        self._end_streaming_assistant()
        self.status.setText("")
        self._history.append({"role": "user", "content": self._pending_user})
        self._history.append({"role": "assistant", "content": full})
        if len(self._history) > 40:
            self._history = self._history[-40:]
        self.send_btn.setEnabled(True)

    def _on_stream_failed(self, err: str) -> None:
        if self._streaming:
            self._end_streaming_assistant()
        self.status.setText("")
        self._append_html(
            f'<p style="color:{COLOR_ERROR}; margin: 8px 0;"><b>Error</b> — {_escape_html(err)}</p>'
        )
        self.send_btn.setEnabled(True)


def _escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Juno AI")
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
