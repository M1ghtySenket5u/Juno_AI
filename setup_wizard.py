"""Step-by-step setup guide with copy-paste terminal commands."""

from __future__ import annotations

import html

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config_store import load_config, save_config
from juno_environment import JUNO_ROOT, SetupIssue, analyze_installation

COLOR_TITLE = "#F2F6FF"
COLOR_SUBTITLE = "#B8C5E0"
COLOR_PANEL_BG = "rgba(8, 14, 32, 0.96)"
COLOR_ERROR = "#FF6B6B"
COLOR_OK = "#7EC8E3"
COLOR_GOLD = "#D4AF37"


def _issue_block(issue: SetupIssue) -> str:
    sev = issue.severity.upper()
    title = html.escape(issue.title, quote=True)
    detail = html.escape(issue.detail, quote=True).replace("\n", "<br>")
    return (
        f"<p style='margin-bottom:12px;'><b>[{sev}] {title}</b><br>{detail}</p>"
    )


def _commands_widget(commands: tuple[str, ...], parent: QWidget | None) -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    if not commands:
        lay.addWidget(QLabel("<i>No commands needed for this item.</i>", parent))
        return w
    block = "\n".join(commands)
    edit = QPlainTextEdit(block)
    edit.setReadOnly(True)
    edit.setMaximumHeight(min(160, 28 * (2 + len(commands))))
    edit.setStyleSheet(
        "QPlainTextEdit { background: rgba(3,8,20,0.95); color: #F4F8FF; "
        "border: 1px solid #D4AF37; border-radius: 6px; padding: 8px; font-family: monospace; }"
    )
    btn = QPushButton("Copy commands to clipboard")
    btn.setStyleSheet(
        "QPushButton { padding: 8px 14px; font-weight: bold; color: #F4F8FF; "
        "background-color: #1a5080; border: 1px solid #D4AF37; border-radius: 8px; }"
    )

    def _copy() -> None:
        QApplication.clipboard().setText(block)
        btn.setText("Copied!")
        QApplication.processEvents()

    btn.clicked.connect(_copy)
    lay.addWidget(edit)
    lay.addWidget(btn)
    return w


class SetupGuideDialog(QDialog):
    """Multi-step setup: checks → install → launch → use Juno."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Juno AI — setup guide")
        self.setMinimumSize(560, 520)
        self._issues = analyze_installation()

        root = QVBoxLayout(self)
        header = QLabel("<b>Welcome — set up Juno in a few steps</b>")
        hf = QFont()
        hf.setPointSize(13)
        header.setFont(hf)
        header.setStyleSheet(f"color: {COLOR_TITLE};")
        root.addWidget(header)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._page_step1())
        self._stack.addWidget(self._page_step2())
        self._stack.addWidget(self._page_step3())
        self._stack.addWidget(self._page_step4())
        root.addWidget(self._stack, stretch=1)

        nav = QHBoxLayout()
        self._btn_back = QPushButton("← Back")
        self._btn_next = QPushButton("Next →")
        self._btn_finish = QPushButton("Start chatting")
        self._btn_finish.setDefault(True)
        self._btn_back.clicked.connect(self._go_back)
        self._btn_next.clicked.connect(self._go_next)
        self._btn_finish.clicked.connect(self._finish)
        nav.addWidget(self._btn_back)
        nav.addStretch()
        nav.addWidget(self._btn_next)
        nav.addWidget(self._btn_finish)
        root.addLayout(nav)

        self._sync_nav()
        self._apply_style()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"""
            QDialog {{ background-color: {COLOR_PANEL_BG}; }}
            QLabel {{ color: {COLOR_SUBTITLE}; font-size: 12px; }}
            QPushButton {{ padding: 8px 14px; color: {COLOR_TITLE}; }}
            """
        )

    def _wrap_scroll(self, inner: QWidget) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(inner)
        return scroll

    def _page_step1(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        step = QLabel("<b>Step 1 of 4 — Quick health check</b>")
        step.setStyleSheet(f"color: {COLOR_GOLD}; font-size: 13px;")
        v.addWidget(step)
        body = QLabel(
            "Juno looked at your machine for common blockers. "
            "Anything marked ERROR should be fixed before you rely on live models; "
            "warnings are suggestions. INFO means you are in good shape."
        )
        body.setWordWrap(True)
        v.addWidget(body)

        html_parts: list[str] = []
        for issue in self._issues:
            color = COLOR_ERROR if issue.severity == "error" else COLOR_SUBTITLE
            if issue.severity == "info":
                color = COLOR_OK
            html_parts.append(
                f"<div style='color:{color};'>{_issue_block(issue)}</div>"
            )
        report = QLabel("".join(html_parts))
        report.setWordWrap(True)
        report.setTextFormat(Qt.TextFormat.RichText)
        v.addWidget(report)

        for issue in self._issues:
            if issue.copy_commands:
                cap = QLabel()
                cap.setText(f"Copy/paste — {issue.title}")
                cap.setStyleSheet(f"color: {COLOR_TITLE}; font-weight: bold;")
                v.addWidget(cap)
                v.addWidget(_commands_widget(issue.copy_commands, page))

        v.addStretch()
        return self._wrap_scroll(page)

    def _page_step2(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        step = QLabel("<b>Step 2 of 4 — Install Python dependencies (Linux Mint)</b>")
        step.setStyleSheet(f"color: {COLOR_GOLD}; font-size: 13px;")
        v.addWidget(step)
        v.addWidget(
            QLabel(
                "Open <b>Terminal</b>. Run the commands below <b>in order</b> from your Juno folder. "
                "They install a private virtual environment (`.venv`) and PyQt6 + openai — nothing system-wide except "
                "the small `apt` line if Python tools are missing."
            ),
            page,
        )
        v.addWidget(
            QLabel("<b>A — If you never installed system Python tools:</b>", page),
        )
        v.addWidget(_commands_widget(_apt_only_block(), page))
        v.addWidget(
            QLabel("<b>B — Always run the Juno installer from the project folder:</b>", page),
        )
        v.addWidget(_commands_widget(_full_install_block(), page))
        v.addStretch()
        return self._wrap_scroll(page)

    def _page_step3(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        step = QLabel("<b>Step 3 of 4 — Launch Juno</b>")
        step.setStyleSheet(f"color: {COLOR_GOLD}; font-size: 13px;")
        v.addWidget(step)
        v.addWidget(
            QLabel(
                "After Step 2 finishes, start Juno from the <b>application menu</b> (search “Juno AI”) "
                "or run the launcher script below."
            ),
            page,
        )
        launch = f"cd {JUNO_ROOT}\n./juno-ai.sh"
        v.addWidget(_commands_widget(tuple(launch.split("\n")), page))
        v.addStretch()
        return self._wrap_scroll(page)

    def _page_step4(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        step = QLabel("<b>Step 4 of 4 — You are ready</b>")
        step.setStyleSheet(f"color: {COLOR_GOLD}; font-size: 13px;")
        v.addWidget(step)
        body = QLabel(
            "<ul>"
            "<li><b>Offline first:</b> Juno answers immediately about Linux, Mint, the terminal, commands, "
            "and even an apple pie checklist — no API key required.</li>"
            "<li><b>Optional:</b> use <b>File → Settings</b> only if you want OpenAI or a local OpenAI-compatible HTTP API.</li>"
            "<li><b>Help:</b> open this guide again anytime via <b>Help → Setup guide…</b></li>"
            "</ul>"
        )
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.RichText)
        v.addWidget(body)
        v.addStretch()
        return self._wrap_scroll(page)

    def _sync_nav(self) -> None:
        i = self._stack.currentIndex()
        self._btn_back.setEnabled(i > 0)
        self._btn_next.setVisible(i < self._stack.count() - 1)
        self._btn_finish.setVisible(i == self._stack.count() - 1)

    def _go_back(self) -> None:
        self._stack.setCurrentIndex(max(0, self._stack.currentIndex() - 1))
        self._sync_nav()

    def _go_next(self) -> None:
        self._stack.setCurrentIndex(min(self._stack.count() - 1, self._stack.currentIndex() + 1))
        self._sync_nav()

    def _finish(self) -> None:
        data = load_config()
        data["setup_guide_done"] = True
        save_config(data)
        self.accept()


def _apt_only_block() -> tuple[str, ...]:
    return (
        "sudo apt update",
        "sudo apt install -y python3 python3-venv python3-pip",
    )


def _full_install_block() -> tuple[str, ...]:
    root = str(JUNO_ROOT)
    return (
        f"cd {root}",
        "chmod +x install-linux.sh juno-ai.sh build-deb.sh",
        "./install-linux.sh",
    )


def should_show_setup_guide() -> bool:
    return not bool(load_config().get("setup_guide_done"))
