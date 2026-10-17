import sys
import inkex
import os
sys.path.insert(0, "libs")
import requests


class Extension(inkex.Effect):
    
    def effect(self):
        inkex.errormsg("Action PULL exécutée")

if __name__ == '__main__':
    Extension().run()