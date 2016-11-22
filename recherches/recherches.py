# Importations
from .thread import RecherchesThread

from log.mixin import ThreadLogMixin

# Classe
class Recherches(ThreadLogMixin):
    # Attributs
    nom_log = "upnp.recherches"
    
    # Méthodes spéciales
    def __init__(self, barriere):
        self._thread = RecherchesThread(barriere)
    
    # Méthodes
    def lancer(self):
        self._thread.start()
    
    def arreter(self):
        self._thread.arreter()
        self._thread.join()
