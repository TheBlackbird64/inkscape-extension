from fastapi import FastAPI, UploadFile, File, Form
import uvicorn
import shutil
import os
import sqlite3

# constants
DIR_UPLOADS = os.path.join(os.path.dirname(__file__), "uploads")

app = FastAPI()

@app.get("/id")
def get_id(id: str = None):
    return {"id": "12345"}

@app.get("/infos")
def get_files():

    files = []
    for root, _, filenames in os.walk(DIR_UPLOADS):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(root, filename), DIR_UPLOADS))
    
    return files

@app.post("/upload")
def uploader_fichier(file: UploadFile = File(...)):

    filepath = os.path.join(DIR_UPLOADS, file.filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Sauvegarde du fichier sur le serveur
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    return {"message": f"Fichier '{file.filename}' reçu et sauvegardé avec succès !"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    pass