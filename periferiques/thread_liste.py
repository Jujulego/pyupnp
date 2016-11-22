# Importations
from .handler import PerifHandler
from .serveur import PerifServeur

from base.wrapper import ThreadSafeWrapper
from helper import Helper
from log.mixin import ThreadLogMixin
from pystock import Stock

import threading as th
import queue

# Variables
helper = Helper()

# Classe
class PerifListeThread(ThreadLogMixin, th.Thread):
    # Attributs
    nom_log = "upnp.periferiques"
    marque  = "perif"
    events  = ThreadSafeWrapper({})
    
    # Méthodes spéciales
    def __init__(self, queue, events):
        self.queue = self.modifs = queue
        self.fini  = False
        
        with self.events:
            self.events.objet.update(events)
        
        super(PerifListeThread, self).__init__()
    
    # Méthodes
    def run(self):
        self.stock = helper.stock["periferiques"]
        
        with self.stock:
            while not self.fini:
                try:
                    requete, opts, nopts = self.modifs.get()
                    
                    if requete == "fini":
                        break
                    
                    elif hasattr(self, requete):
                        getattr(self, requete)(*opts, **nopts)
                
                except queue.Empty:
                    pass
    
    def ajout(self, uuid, id_p):
        with self.stock["liste"] as l:
            l.ajouter_valeurs(uuid=uuid, id=id_p)
        
        if not self.stock.existe(uuid):
            self.stock.ajouter_stock(uuid)
        
        self.events.objet[uuid].set()
    
    def arreter(self):
        self.fini = True
        self.modifs.put(("fini", [], {}))
        self.join()
