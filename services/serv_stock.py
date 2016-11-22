# Importations
from .thread_stock import ServiceThreadStock

from queue import Queue

# Classe
class ServicesStock:
    # Méthodes spéciales
    def __init__(self, perif, event):
        self.perif  = perif
        self.modifs = Queue()
        
        self._etat  = 0
        self._infos = {}
        
        self._thread = ServiceThreadStock(perif.infos["uuid"], self.modifs, event)
        self._thread.start()
    
    # Méthodes
    def ajouter(self, infos):
        self._infos = self.infos
        self._etat += 1
        self._infos[infos["infos"]["identifiant"]] = infos
        
        self.modifs.put(("ajouter", [infos, self._etat], {}))
    
    def mise_a_jour(self, nom, infos):
        self._infos = self.infos
        self._etat += 1
        self._infos[nom].update(infos)
        
        self.modifs.put(("mise_a_jour", [nom, infos, self._etat], {}))
    
    # Propriétés
    @property
    def infos(self):
        if self._etat == self._thread.etat:
            self._infos = {}
            return self._thread.infos
        
        return self._infos
