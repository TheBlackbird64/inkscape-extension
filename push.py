from lxml import etree
import inkex
import sys
sys.path.insert(0, "libs")
import requests

url = "http://localhost:8000/"

class Save(inkex.Effect):

    NODE_ID = "id_document"

    def effect(self):
        
        # 0: check if the document is saved
        inkex.errormsg(Save.document_path())
        if Save.document_path() is None:
            inkex.errormsg("Le document doit être sauvegardé avant de pouvoir être poussé sur le serveur")
            return
        
        # 1: get the id metadata
        
        root = self.document.getroot()
        
        metadata = root.find("metadata")
        if metadata is None:
            metadata = etree.SubElement(root, "metadata")
        node_document_id = metadata.find(Save.NODE_ID)
        if node_document_id is None:
            node_document_id = etree.SubElement(metadata, Save.NODE_ID)

        # 2: ask to server an id if the node is empty
        
        if node_document_id.text == "":
            res = requests.get(url + "id", params={"id": node_document_id.text})
            if res.status_code != 200:
                inkex.errormsg("Erreur lors de la récupération de l'id du document")
                return
        
            node_document_id.text = res.json()["id"]

        # 3: push with the id
        
        with open(Save.document_path(), "rb") as f:
            res = requests.post(url + "upload", files={"file": f})
        
        if res.status_code != 200:
            inkex.errormsg("Erreur lors de l'envoi du fichier sur le serveur")
            return

        inkex.errormsg("Fichier envoyé avec succès !")


if __name__ == '__main__':
    Save().run()