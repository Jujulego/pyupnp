from .base import Fichier

from tag import Tag

class FichierMp3(Fichier):
    # Attributs
    bytes = True
    extension = ".mp3"
    
    # Propriétés
    @property
    def tags(self):
        self._assertion()
        
        return Tag(self._fichier)
