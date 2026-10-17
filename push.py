import inkex
import sys
sys.path.insert(0, "libs")
import requests

url = "http://localhost:8000/upload"

data = {"folder": "mes_documents/2026"}
files = {"file": open("rapport.txt", "rb")}

reponse = requests.post(url, data=data, files=files)

print(reponse.json())


class Extension(inkex.Effect):

    def effect(self):
        # send a file to a distant server
        url = "http://localhost:8000/upload"

        # 1: get the id metadata

        # 2: ask to server (ok or id doesn't exists or None => send id)

        # 3: push with the id


if __name__ == '__main__':
    Extension().run()