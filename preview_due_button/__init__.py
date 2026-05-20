from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

from aqt import dialogs, mw
from aqt.browser import previewer
from aqt.qt import QDialogButtonBox, QKeySequence, qconnect
from aqt.utils import tooltip


DUE_BUTTON_TEXT = "Set Due Date: Tomorrow"
VIEW_BUTTON_TEXT = "View"
DUE_TOMORROW = "1"
DUE_SHORTCUT = "T"
VIEW_SHORTCUT = "V"


def set_card_due_tomorrow(card_id: int, parent: Any = None) -> None:
    """Set exactly one card due tomorrow."""
    mw.col.sched.set_due_date([card_id], DUE_TOMORROW)
    mw.col.save()
    tooltip("Set previewed card due tomorrow", parent=parent)


def open_card_in_browser(card_id: int, parent: Any = None) -> None:
    """Open exactly one previewed card in Anki's browser."""
    browser = dialogs.open("Browser", mw)
    browser.activateWindow()
    browser.search_for(f"cid:{card_id}")
    tooltip("Opened previewed card in Browser", parent=parent)


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
    """Install instance-local action buttons on a preview window."""
    if getattr(preview_window, "_preview_due_button_installed", False):
        return

    bbox = getattr(preview_window, "bbox", None)
    if bbox is None:
        tooltip("Preview due button could not find the button box", parent=preview_window)
        return

    layout = bbox.layout()
    if layout is not None and hasattr(layout, "insertStretch"):
        layout.insertStretch(layout.count(), 1)

    view_button = bbox.addButton(VIEW_BUTTON_TEXT, QDialogButtonBox.ButtonRole.ActionRole)
    view_button.setAutoDefault(False)
    view_button.setShortcut(QKeySequence(VIEW_SHORTCUT))
    view_button.setToolTip(f"Open this previewed card in Browser ({VIEW_SHORTCUT})")

    due_button = bbox.addButton(DUE_BUTTON_TEXT, QDialogButtonBox.ButtonRole.ActionRole)
    due_button.setAutoDefault(False)
    due_button.setShortcut(QKeySequence(DUE_SHORTCUT))
    due_button.setToolTip(
        f"Set this previewed card due tomorrow ({DUE_SHORTCUT})"
    )

    def current_card_id() -> Optional[int]:
        card_id = resolve_card_id(preview_window)
        if card_id is None:
            tooltip("Could not find card for this preview window", parent=preview_window)
        return card_id

    def on_view_click() -> None:
        card_id = current_card_id()
        if card_id is None:
            return
        open_card_in_browser(card_id, parent=preview_window)

    def on_due_click() -> None:
        card_id = current_card_id()
        if card_id is None:
            return
        set_card_due_tomorrow(card_id, parent=preview_window)

    qconnect(view_button.clicked, on_view_click)
    qconnect(due_button.clicked, on_due_click)
    preview_window._preview_due_button_installed = True


def patch_multi_card_previewer_create_gui() -> None:
    """Patch Anki multi-card preview dialogs with instance-local buttons."""
    preview_class = previewer.MultiCardPreviewer
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
    patch_multi_card_previewer_create_gui()


init()
