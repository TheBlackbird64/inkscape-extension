# Inkscape sync extension

## Overview
This extension synchronizes svg documents between local and remote locations using a simple push/pull workflow, triggered from inkscape with an extension.


## Usage

Execute : 

for windows:
```batch
start-test.bat
``` 
for linux:
```bash
start-test
``` 
to copy files to the inkscape extension directory.

Now you have to run the server on the machine you want to be hosting the server.

Then you can test it in the software.

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


Use the provided `push.py` and `pull.py` scripts to run the push and pull actions.

