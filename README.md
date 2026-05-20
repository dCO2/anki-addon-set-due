# Anki Preview Due Date Button

An Anki add-on that adds quick actions to preview windows. It lets you open the
previewed card in Anki's Browser or set that previewed card due tomorrow without
affecting the active review card.

## Features

- Adds a `View` button to preview windows.
- Adds a `Set Due Date: Tomorrow` button to preview windows.
- Shows a number-only count of cards due tomorrow in the previewed card's top-level deck.
- Acts on the card currently shown in the clicked preview window.
- Leaves the active review card untouched.
- Supports multiple preview windows at once.

## Why This Exists

During review, you may open a separate card preview from another add-on or from
Anki's preview UI. Sometimes the previewed card needs a scheduling action, but
the current review card should not be affected. This add-on keeps those two
contexts separate.

If several preview windows are open, each window's buttons affect only the card
shown in that window.

## Installation

### Development Install

Clone this repository and symlink the add-on package into Anki's `addons21`
folder:

```sh
ln -s /path/to/anki-preview-due-date-button/preview_due_button \
  "$HOME/Library/Application Support/Anki2/addons21/preview_due_button"
```

Then restart Anki.

On Windows and Linux, replace the Anki profile path with the location of your
Anki `addons21` directory.

### Packaged Install

Build the `.ankiaddon` archive:

```sh
make package
```

The packaged add-on will be created at:

```text
dist/preview_due_button.ankiaddon
```

Install the `.ankiaddon` file through Anki's add-on installer.

## Usage

1. Open a card preview window.
2. Click `View` to open the previewed card in Anki's Browser.
3. Click `Set Due Date: Tomorrow` to set the previewed card due tomorrow.

The buttons resolve the current card from the preview window where they were
clicked.

The numeric label shows the number of cards due tomorrow in the previewed card's
top-level deck. For a card in `Biology::Chapter 1::Enzymes`, the count is scoped
to `Biology` and its subdecks. The label refreshes when the preview changes and
immediately after `Set Due Date: Tomorrow` is clicked.

## Architecture

The actions are instance-local:

- do not use `mw.reviewer.card`
- do not use Browser selection
- do not use global "current card" state
- do resolve the card from the preview window/pane that owns the clicked button

The current implementation patches Anki's multi-card preview dialog and uses
the preview window's own `card()` method at click time. This keeps each action
local to the preview window whose button was clicked.

The scheduling operation uses Anki's scheduler:

```python
mw.col.sched.set_due_date([card_id], "1")
```

The Browser action opens Anki's Browser with a card-specific search:

```python
browser.search_for(f"cid:{card_id}")
```

The due-tomorrow count uses Anki's search system:

```python
deck:<top-level-deck> prop:due=1
```

## Development

Run a syntax check with:

```sh
make syntax
```

Remove generated files with:

```sh
make clean
```
