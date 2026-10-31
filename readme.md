# Inkscape sync extension

## Overview
This extension synchronizes svg documents between local and remote locations using a simple push/pull workflow, triggered from inkscape with an extension.


## Usage

Run the server on the machine you want to be hosting the server : 

On the server, in the `server` folder:

for windows:
```batch
create_environment.bat
``` 
for linux:
```bash
create_environment
``` 

Copy the generated config.ini file and paste it next to the extension files

On the client, execute : 

for windows:
```batch
start-test.bat
``` 
for linux:
```bash
start-test
``` 
to copy files to the inkscape extension directory.

## Logic

### Push
- Check if the document has an `id`.
- If `id` exists:
	- Verify `id_modif` of the local doc matches the remote doc's `id_modif`.
	- If they differ, show a warning.
	- Push and replace the remote document.
- If `id` does not exist:
	- Ask the user for an `id`, then push the document.

### Pull
- Check if the document has an `id`.
- If `id` exists: replace the local document with the remote version.
- If `id` does not exist:
	- Open a dialog to choose which remote document to sync with.
	- Add the chosen `id` to the local document and synchronize.

### Manage
- Open the same dialog (tkinter window) even if the document already has an `id`.
- `Ouvrir`: replace the local document with the selected remote document and link to it (`id`).
- `Supprimer`: delete the selected remote document. If it was the linked one, the local document is unlinked (the next push creates a new `id`).


Use the provided `push.py`, `pull.py` and `manage.py` scripts (menu Extensions > Synchro) to run the push, pull and manage actions.
On linux, the dialog needs tkinter for the python used by inkscape (`python3-tk` package).

