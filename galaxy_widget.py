"""Painted galaxy backdrop with subtle starfield — NASA × Japanese palette accents."""

from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget


class GalaxyBackdrop(QWidget):
    """Full-area gradient nebula + stars; children should sit in a layout on top (opaque frames)."""

    def paintEvent(self, event) -> None:  # noqa: ARG002
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        # Deep space → indigo → teal nebula (galaxy feel)
        linear = QLinearGradient(0.0, 0.0, float(w), float(h))
        linear.setColorAt(0.0, QColor("#070b1a"))
        linear.setColorAt(0.35, QColor("#12082a"))
        linear.setColorAt(0.65, QColor("#0a2344"))
        linear.setColorAt(1.0, QColor("#041016"))
        painter.fillRect(self.rect(), QBrush(linear))

        glow = QRadialGradient(QPointF(w * 0.72, h * 0.28), min(w, h) * 0.55)
        glow.setColorAt(0.0, QColor(180, 90, 160, 55))
        glow.setColorAt(0.4, QColor(40, 80, 140, 35))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), QBrush(glow))

        second = QRadialGradient(QPointF(w * 0.2, h * 0.75), min(w, h) * 0.45)
        second.setColorAt(0.0, QColor(30, 120, 160, 40))
        second.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), QBrush(second))

        # Starfield (deterministic pseudo-random from size)
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(140):
            sx = ((i * 7919) % max(w, 1))
            sy = ((i * 6151 + w) % max(h, 1))
            br = 1 + (i % 3)
            alpha = 35 + (i * 17) % 120
            painter.setBrush(QColor(230, 245, 255, alpha))
            painter.drawEllipse(QRectF(float(sx), float(sy), float(br), float(br)))

        # Vermillion horizon line (samurai / 緋色 accent)
        pen = QPen(QColor("#B23A48"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(0, h - 3, w, h - 3)

        gold = QPen(QColor("#C9A227"))
        gold.setWidth(1)
        painter.setPen(gold)
        painter.drawLine(0, h - 6, w, h - 6)
