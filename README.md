# Anki Preview Due Date Button

Companion Anki add-on for setting the due date of the card shown in a preview pane/window without touching the active review card.

## Goal

When multiple preview windows are open, each window gets its own action buttons.
Clicking a button acts on the card currently shown in that same preview window only.

```text
Review card A remains active
Preview window 1 shows card B -> buttons affect B
Preview window 2 shows card C -> buttons affect C
Preview window 3 shows card D -> buttons affect D
```

## Architecture

The button must be instance-local:

- do not use `mw.reviewer.card`
- do not use Browser selection
- do not use global "current card" state
- do resolve the card from the preview window/pane that owns the clicked button

The add-on currently adds two buttons:

- `View`: opens the previewed card in Anki's Browser using `cid:<card id>`.
- `Set Due Date: Tomorrow`: sets the previewed card due tomorrow.

The scheduling operation itself is small:

```python
mw.col.sched.set_due_date([card_id], "1")
```

The current implementation patches Anki's multi-card preview dialog and uses
the preview window's own `card()` method at click time. This keeps each action
local to the preview window whose button was clicked.

## Implementation Workflow

1. Patch `aqt.browser.previewer.MultiCardPreviewer._create_gui`.
2. Let Anki create the normal preview window UI.
3. Add a spacer, then `View` and `Set Due Date: Tomorrow` buttons to that preview window's button box.
4. On click, ask that same preview instance for its current card id.
5. For `View`, open Anki's Browser filtered to that one card.
6. For `Set Due Date: Tomorrow`, call Anki's scheduler for that one card id.
7. Show a tooltip.

## Preferred Strategy

Patch the preview dialog UI creation method:

```python
original_create_gui = MultiCardPreviewer._create_gui

def patched_create_gui(self, *args, **kwargs):
    result = original_create_gui(self, *args, **kwargs)
    install_due_button(self)
    return result

MultiCardPreviewer._create_gui = patched_create_gui
```

The click handler should resolve the current card at click time:

```python
def on_click():
    card_id = resolve_card_id(preview_window)
    set_due_tomorrow(card_id)
```

This matters if a preview window can change which card it displays after opening.

## Installation During Development

Create a symlink from Anki's add-on folder to `preview_due_button`:

```sh
ln -s /Users/dco2/Documents/repo/anki-addon-set-due/preview_due_button \
  "$HOME/Library/Application Support/Anki2/addons21/preview_due_button"
```

Then restart Anki.

## Packaging

Zip the contents of `preview_due_button` and rename the archive to:

```text
preview_due_button.ankiaddon
```
