from fastapi import FastAPI, HTTPException, UploadFile, Depends, File, Form
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
import uvicorn
import shutil
import os
import secrets

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

API_KEY = config["server"]["api_key"]
headers = {"X-API-Key": API_KEY}

# constants
PORT = 8000
DIR_UPLOADS = os.path.join(os.path.dirname(__file__), "uploads")

app = FastAPI()

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Depends(api_key_header)):
    if not secrets.compare_digest(key, API_KEY):
        raise HTTPException(status_code=401, detail="Non autorisé")

def file_path(id: str):
    """Return the path of the file with the given id (the id must stay inside the uploads folder)"""
    if id in (".", "..") or os.path.basename(id) != id:
        raise HTTPException(status_code=400, detail=f"Id invalide : '{id}'")
    return os.path.join(DIR_UPLOADS, id)

@app.get("/id", dependencies=[Depends(verify_api_key)])
def get_id(filename: str):
    """Return a not used id for a new document"""
    print(f"Request for id with filename: {filename}")
    name = os.path.splitext(filename)[0] or "dessin" # the document name is empty until the document is saved
    id = name
    x = 0
    while os.path.exists(os.path.join(DIR_UPLOADS, id)):
        x += 1
        id = f"{name}_{x}"
    return {"id": id} # document name, + _x only when a file with the same name exists

@app.get("/list", dependencies=[Depends(verify_api_key)])
def list_files():
    """Return the files stored on the server, most recently modified first"""
    if not os.path.isdir(DIR_UPLOADS):
        return []

    files = []
    for entry in os.scandir(DIR_UPLOADS):
        if entry.is_file():
            stat = entry.stat()
            files.append({"id": entry.name, "size": stat.st_size, "modified": stat.st_mtime})
    files.sort(key=lambda f: f["modified"], reverse=True)
    return files

@app.post("/upload", dependencies=[Depends(verify_api_key)])
def upload_file(file: UploadFile = File(...), name: str = Form(...)):
    """Save the file on the server"""

    if name == "":
        return {"message": "Le fichier n'a pas de nom, il n'a pas été sauvegardé !"}

    filepath = file_path(name)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    print(filepath)
    
    # Save the file on the serveur
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": f"Le fichier '{name}' a été sauvegardé !"}


@app.get("/download", dependencies=[Depends(verify_api_key)])
def download_file(id: str):
    """Return the file with the given id"""

    filepath = file_path(id)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Le fichier '{id}' n'existe pas sur le serveur !")

    return FileResponse(
        path=filepath,
        media_type="image/svg+xml",
        filename="mon_fichier.svg"
    )


@app.delete("/delete", dependencies=[Depends(verify_api_key)])
def delete_file(id: str):
    """Delete the file with the given id"""

    filepath = file_path(id)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Le fichier '{id}' n'existe pas sur le serveur !")

    os.remove(filepath)
    return {"message": f"Le fichier '{id}' a été supprimé !"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=PORT)