import sys
import inkex
import os
sys.path.insert(0, "libs")
import requests
from lxml import etree
import configparser
import xml.parsers.expat

from file_browser import FileBrowser

config = configparser.ConfigParser()
config.read("config.ini")

API_KEY = config["server"]["api_key"]
URL = config["server"]["url"]
headers = {"X-API-Key": API_KEY}
TIMEOUT = 30 # seconds, Inkscape is blocked while waiting the server

# the svg comes from the network: no entity resolution (it can read local files), nor network access
SVG_PARSER = etree.XMLParser(huge_tree=True, strip_cdata=False, resolve_entities=False, no_network=True)


class StopParsing(Exception):
    pass

def declares_entities(data):
    """True if the xml declares entities: they can read local files, or fill the memory while parsing (even not resolved)"""
    found = []

    def entity(*args):
        found.append(True)
        raise StopParsing

    def root(*args):
        raise StopParsing # all the declarations are before the root element

    parser = xml.parsers.expat.ParserCreate()
    parser.EntityDeclHandler = entity
    parser.StartElementHandler = root
    try:
        parser.Parse(data, True)
    except StopParsing:
        pass
    return bool(found)


class Pull(inkex.Effect):

    METADATA_NODE = "{http://www.w3.org/2000/svg}metadata"
    NODE_ID = "{http://www.w3.org/2000/svg}id_document"

    def get_document_id(self):
        """Return the id of the server file linked to the document (None if not linked)"""
        metadata = self.svg.find(Pull.METADATA_NODE)
        if metadata is not None:
            node_document_id = metadata.find(Pull.NODE_ID)
            if node_document_id is not None and node_document_id.text:
                return node_document_id.text
        return None

    def set_document_id(self, id):
        """Link the document to the server file with this id (None to unlink it)"""
        metadata = self.svg.find(Pull.METADATA_NODE)
        if metadata is None:
            metadata = etree.SubElement(self.svg, Pull.METADATA_NODE)
        node_document_id = metadata.find(Pull.NODE_ID)
        if node_document_id is None:
            node_document_id = etree.SubElement(metadata, Pull.NODE_ID)
        node_document_id.text = id

    def pull(self, id):
        """Replace the document with the server file with this id"""

        try:
            res = requests.get(f"{URL}download", params={"id": id}, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            inkex.errormsg(f"Erreur lors de la récupération du fichier depuis le serveur: {e}")
            return

        if res.status_code == 404:
            inkex.errormsg(f"Le fichier '{id}' n'existe plus sur le serveur : choisissez-en un autre avec Synchro > Manage distant server files")
            return
        if res.status_code != 200:
            inkex.errormsg("Erreur lors de la récupération du fichier depuis le serveur")
            return

        try:
            if declares_entities(res.content):
                inkex.errormsg(f"Le fichier '{id}' a été refusé : il déclare des entités XML, qui peuvent lire des fichiers de cet ordinateur")
                return
            new_svg = etree.fromstring(res.content, parser=SVG_PARSER)
        except (xml.parsers.expat.ExpatError, ValueError, etree.XMLSyntaxError) as e:
            inkex.errormsg(f"Le fichier '{id}' n'est pas un SVG valide : {e}")
            return

        # Remplacer les attributs de la racine
        self.svg.attrib.clear()
        self.svg.attrib.update(new_svg.attrib)

        # Remplacer tout le contenu
        for child in list(self.svg):
            self.svg.remove(child)

        for child in list(new_svg):
            self.svg.append(child)

        # the server file should already contain its id, but make sure the document is linked to it
        self.set_document_id(id)

    def browse(self):
        """Open the window listing the server files, then pull the chosen one"""

        browser = FileBrowser(URL, headers, self.get_document_id())
        browser.run()

        if browser.chosen_id is not None:
            self.pull(browser.chosen_id)
        elif browser.current_deleted:
            self.set_document_id(None)

    def effect(self):

        id = self.get_document_id()
        if id is not None:
            self.pull(id)
        else:
            # first pull: the user chooses the server file to link with the document
            self.browse()


if __name__ == '__main__':
    Pull().run()
