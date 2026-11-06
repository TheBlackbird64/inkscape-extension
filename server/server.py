from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import shutil
import os
import secrets
import tempfile

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

API_KEY = config["server"]["api_key"]
headers = {"X-API-Key": API_KEY}

# constants
PORT = 8000
DIR_UPLOADS = os.path.join(os.path.dirname(__file__), "uploads")
MAX_UPLOAD_SIZE = 50 * 1024 * 1024 # 50 Mo

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None) # no public documentation of the api

@app.middleware("http")
async def check_request(request: Request, call_next):
    """Refuse a request before its body is read (FastAPI reads the body of a form before checking the dependencies)"""

    # compare bytes: compare_digest fails on str with non ascii characters
    key = request.headers.get("X-API-Key", "")
    if not secrets.compare_digest(key.encode(), API_KEY.encode()):
        return JSONResponse(status_code=401, content={"detail": "Non autorisé"})

    if request.method == "POST":
        length = request.headers.get("Content-Length", "")
        if not length.isdecimal():
            return JSONResponse(status_code=411, content={"detail": "Taille de la requête manquante"})
        if int(length) > MAX_UPLOAD_SIZE:
            return JSONResponse(status_code=413, content={"detail": f"Fichier trop gros (max {MAX_UPLOAD_SIZE // (1024 * 1024)} Mo)"})

    return await call_next(request)

def file_path(id: str):
    """Return the path of the file with the given id (the id must stay inside the uploads folder)"""
    if id in (".", "..") or os.path.basename(id) != id:
        raise HTTPException(status_code=400, detail=f"Id invalide : '{id}'")
    return os.path.join(DIR_UPLOADS, id)

@app.get("/id")
def get_id(filename: str):
    """Return a not used id for a new document"""
    print(f"Request for id with filename: {filename}")
    name = os.path.splitext(filename)[0] or "dessin" # the document name is empty until the document is saved
    id = name
    x = 0
    while os.path.exists(file_path(id)):
        x += 1
        id = f"{name}_{x}"
    return {"id": id} # document name, + _x only when a file with the same name exists

@app.get("/list")
def list_files():
    """Return the files stored on the server, most recently modified first"""
    if not os.path.isdir(DIR_UPLOADS):
        return []

    files = []
    for entry in os.scandir(DIR_UPLOADS):
        if entry.is_file() and not entry.name.startswith("."): # hidden files: uploads in progress
            stat = entry.stat()
            files.append({"id": entry.name, "size": stat.st_size, "modified": stat.st_mtime})
    files.sort(key=lambda f: f["modified"], reverse=True)
    return files

@app.post("/upload")
def upload_file(file: UploadFile = File(...), name: str = Form(...)):
    """Save the file on the server"""

    if name == "":
        return {"message": "Le fichier n'a pas de nom, il n'a pas été sauvegardé !"}

    filepath = file_path(name)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    print(filepath)

    # Save the file on the serveur: in a temporary file first, so an error (disk full...) can't truncate the existing file
    fd, tmp_path = tempfile.mkstemp(dir=DIR_UPLOADS, prefix=".", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            shutil.copyfileobj(file.file, f)
        os.replace(tmp_path, filepath)
    except Exception:
        os.remove(tmp_path)
        raise

    return {"message": f"Le fichier '{name}' a été sauvegardé !"}


@app.get("/download")
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


@app.delete("/delete")
def delete_file(id: str):
    """Delete the file with the given id"""

    filepath = file_path(id)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Le fichier '{id}' n'existe pas sur le serveur !")

    os.remove(filepath)
    return {"message": f"Le fichier '{id}' a été supprimé !"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=PORT)