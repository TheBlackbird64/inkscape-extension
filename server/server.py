from fastapi import FastAPI, HTTPException, UploadFile, Depends, File, Form
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
import uvicorn
import shutil
import os
import secrets

# constants
PORT = 8000
DIR_UPLOADS = os.path.join(os.path.dirname(__file__), "uploads")

app = FastAPI()

API_KEY = os.environ["API_KEY"]
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Depends(api_key_header)):
    if not secrets.compare_digest(key, API_KEY):
        raise HTTPException(status_code=401, detail="Non autorisé")

@app.get("/id", dependencies=[Depends(verify_api_key)])
def get_id(filename: str):
    """Return a not used id for a new document"""
    print(f"Request for id with filename: {filename}")
    x = 0
    while os.path.exists(os.path.join(DIR_UPLOADS, filename)):
        x += 1
    return {"id": f"{os.path.splitext(filename)[0]}_{x}"} # document name + _x (where x is when a file with same name exists)

@app.post("/upload", dependencies=[Depends(verify_api_key)])
def upload_file(file: UploadFile = File(...), name: str = Form(...)):
    """Save the file on the server"""

    if name == "":
        return {"message": "Le fichier n'a pas de nom, il n'a pas été sauvegardé !"}

    filepath = os.path.join(DIR_UPLOADS, name)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    print(filepath)
    
    # Save the file on the serveur
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": f"Le fichier '{name}' a été sauvegardé !"}


@app.get("/download", dependencies=[Depends(verify_api_key)])
def download_file(id: str):
    """Return the file with the given id"""

    filepath = os.path.join(DIR_UPLOADS, id)
    if not os.path.exists(filepath):
        return {"message": f"Le fichier '{id}' n'existe pas sur le serveur !"}

    return FileResponse(
        path=filepath, 
        media_type="image/svg+xml", 
        filename="mon_fichier.svg"
    )
    
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=PORT)