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
    """Return a not used id for a new document"""
    return {"id": "12345"}

@app.post("/upload")
def uploader_fichier(file: UploadFile = File(...)):

    filepath = os.path.join(DIR_UPLOADS, file.filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save the file on the serveur
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    return {"message": f"Le fichier '{file.filename}' a été sauvegardé !"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    pass