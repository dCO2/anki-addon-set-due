from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

from aqt import mw
from aqt.browser import previewer
from aqt.qt import QDialogButtonBox, QKeySequence, qconnect
from aqt.utils import tooltip


BUTTON_TEXT = "Tomorrow"
DUE_TOMORROW = "1"
SHORTCUT = "T"


def set_card_due_tomorrow(card_id: int, parent: Any = None) -> None:
    """Set exactly one card due tomorrow."""
    mw.col.sched.set_due_date([card_id], DUE_TOMORROW)
    mw.col.save()
    tooltip("Set previewed card due tomorrow", parent=parent)


def resolve_card_id(preview_window: Any) -> Optional[int]:
    """Resolve the card id from the clicked preview window instance."""
    for attr in ("card", "_card", "current_card"):
        value = getattr(preview_window, attr, None)
        if value is None:
            continue

        card = value() if callable(value) else value
        card_id = getattr(card, "id", None)
        if card_id is not None:
            return int(card_id)

    for attr in ("card_id", "_card_id", "cid", "_cid"):
        value = getattr(preview_window, attr, None)
        if value is not None:
            return int(value)

    return None


def install_due_button(preview_window: Any) -> None:
    """Install an instance-local Tomorrow button on a preview window."""
    if getattr(preview_window, "_preview_due_button_installed", False):
        return

    bbox = getattr(preview_window, "bbox", None)
    if bbox is None:
        tooltip("Preview due button could not find the button box", parent=preview_window)
        return

    button = bbox.addButton(BUTTON_TEXT, QDialogButtonBox.ButtonRole.ActionRole)
    button.setAutoDefault(False)
    button.setShortcut(QKeySequence(SHORTCUT))
    button.setToolTip(f"Set this previewed card due tomorrow ({SHORTCUT})")

    def on_click() -> None:
        card_id = resolve_card_id(preview_window)
        if card_id is None:
            tooltip("Could not find card for this preview window", parent=preview_window)
            return
        set_card_due_tomorrow(card_id, parent=preview_window)

    qconnect(button.clicked, on_click)
    preview_window._preview_due_button_installed = True


def patch_previewer_create_gui() -> None:
    """Patch Anki preview dialogs so every preview instance receives a button."""
    preview_class = previewer.Previewer
    if getattr(preview_class, "_preview_due_button_patched", False):
        return

    original_create_gui: Callable[..., Any] = preview_class._create_gui

    def patched_create_gui(self: Any, *args: Any, **kwargs: Any) -> Any:
        result = original_create_gui(self, *args, **kwargs)
        install_due_button(self)
        return result

    preview_class._create_gui = patched_create_gui
    preview_class._preview_due_button_patched = True


def init() -> None:
    """Entry point loaded by Anki."""
    patch_previewer_create_gui()


init()
