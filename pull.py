import inkex
import os



class Extension(inkex.Effect):
    
    def effect(self):
        inkex.errormsg("Action PULL exécutée")

if __name__ == '__main__':
    Extension().run()