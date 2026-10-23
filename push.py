import os

from lxml import etree
import inkex
import sys
sys.path.insert(0, "libs")
import requests

url = "http://localhost:8000/"

class Save(inkex.Effect):

    NODE_ID = "{http://www.w3.org/2000/svg}id_document"

    def effect(self):
        
        # 0: check if the document is saved

        if (self.options.input_file or "") == "":
            inkex.errormsg("Le document doit être sauvegardé avant de pouvoir être poussé sur le serveur")
            return
        
        # 1: get the id metadata
        
        metadata_node = "{http://www.w3.org/2000/svg}metadata"
        root = self.document.getroot()
        
        metadata = root.find(metadata_node)
        if metadata is None:
            metadata = etree.SubElement(root, metadata_node)
        node_document_id = metadata.find(Save.NODE_ID)
        if node_document_id is None:
            node_document_id = etree.SubElement(metadata, Save.NODE_ID)

        # 2: ask to server an id if the node is empty
        
        if node_document_id.text == "" or node_document_id.text is None:
            res = requests.get(url + "id", params={"filename": self.svg.name})
            if res.status_code != 200:
                inkex.errormsg("Erreur lors de la récupération de l'id du document")
                return

            node_document_id.text = res.json()["id"]

        self.document.write(self.options.input_file, encoding="utf-8", xml_declaration=True)

        # 3: push with the id
        
        with open(self.options.input_file, "rb") as f:
            res = requests.post(url + "upload", files={"file": (self.options.input_file, f, "image/svg+xml")})
        
        if res.status_code != 200:
            inkex.errormsg("Erreur lors de l'envoi du fichier sur le serveur")
            return

        inkex.errormsg("Fichier envoyé avec succès !")


if __name__ == '__main__':
    Save().run()