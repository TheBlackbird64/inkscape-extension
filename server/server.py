from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os
import sqlite3

# constants
DIR_UPLOADS = os.path.join(os.path.dirname(__file__), "uploads")

app = FastAPI()

# @app.get("/id")


@app.get("/infos")
def get_files():

    files = []
    for root, _, filenames in os.walk(DIR_UPLOADS):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(root, filename), DIR_UPLOADS))
    
    return files

@app.post("/upload")
def uploader_fichier(folder: str = Form(...), file: UploadFile = File(...)):

    filepath = os.path.join(DIR_UPLOADS, folder, file.filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Sauvegarde du fichier sur le serveur
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    return {"message": f"Fichier '{file.filename}' reçu et sauvegardé avec succès !"}

if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="localhost", port=8000)
    pass