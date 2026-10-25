import io
import sys
import inkex
import os
sys.path.insert(0, "libs")
import requests
from lxml import etree

url = "http://localhost:8000/"

class Pull(inkex.Effect):

    NODE_ID = "{http://www.w3.org/2000/svg}id_document"
    
    def effect(self):

        # 1: get the id metadata
        
        metadata_node = "{http://www.w3.org/2000/svg}metadata"
        root = self.document.getroot()
        metadata = root.find(metadata_node)
        if metadata is not None:
            node_document_id = metadata.find(Pull.NODE_ID)
            if node_document_id is not None:
                id = node_document_id.text
                if id is not None and id != "":

                    # 2: ask the server the file with this id

                    try:
                        res = requests.get(f"{url}download", params={"id": id})
                    except requests.RequestException as e:
                        inkex.errormsg(f"Erreur lors de la récupération du fichier depuis le serveur: {e}")
                        return

                    if res.status_code == 200:

                        new_document = inkex.load_svg(io.BytesIO(res.content))
                        new_svg = new_document.getroot()

                        # Remplacer les attributs de la racine
                        self.svg.attrib.clear()
                        self.svg.attrib.update(new_svg.attrib)

                        # Remplacer tout le contenu
                        for child in list(self.svg):
                            self.svg.remove(child)

                        for child in list(new_svg):
                            self.svg.append(child)
                        
                    else:
                        inkex.errormsg("Erreur lors de la récupération du fichier depuis le serveur")
                    return
                
        
        inkex.errormsg("Erreur lors de la récupération du fichier depuis le serveur : le fichier doit contenir un id")
            

if __name__ == '__main__':
    Pull().run()