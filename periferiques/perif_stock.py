# Importations
from .thread_stock import PerifStockThread

from services import ServicesStock

from queue import Queue
import threading as th

# Classe
class PeriferiqueStock:
    # Méthodes spéciales
    def __init__(self, uuid, id_p, event):
        self._uuid  = uuid
        self.modifs = Queue()
        self.etat   = 0
        self._infos = {"uuid": uuid, "id": id_p}
        
        sevent = th.Event()
        
        self._thread = PerifStockThread(self, event, sevent)
        self._thread.start()
        
        self.services = ServicesStock(self, sevent)
    
    # Méthodes
    def mise_a_jour(self, infos):
        self._infos = self.infos
        self.etat += 1
        self._infos.update(infos)
        self.modifs.put(("mise_a_jour", [infos, self.etat], {}))
    
    def ajouter_service(self, infos):
        self.services.ajouter(infos)
    
    def maj_service(self, nom, infos):
        self.services.mise_a_jour(self, nom, infos)
    
    # Propriétés
    @property
    def infos(self):
        if self.etat == self._thread.etat:
            self._infos = {}
            return self._thread.infos.contenu
        
        return self._infos
