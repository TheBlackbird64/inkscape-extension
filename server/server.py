from fastapi import FastAPI, UploadFile, File, Form
import uvicorn
import shutil
import os
import sqlite3

# constants
DIR_UPLOADS = os.path.join(os.path.dirname(__file__), "uploads")

app = FastAPI()

@app.get("/id")
def get_id(filename: str):
    """Return a not used id for a new document"""
    print(f"Request for id with filename: {filename}")
    x = 0
    while os.path.exists(os.path.join(DIR_UPLOADS, filename)):
        x += 1
    return {"id": f"{os.path.splitext(filename)[0]}_{x}"} # document name + _x (where x is when a file with same name exists)

@app.post("/upload")
def uploader_fichier(file: UploadFile = File(...)):

    filepath = os.path.join(DIR_UPLOADS, file.filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    print(DIR_UPLOADS)
    
    # Save the file on the serveur
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": f"Le fichier '{file.filename}' a été sauvegardé !"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    pass