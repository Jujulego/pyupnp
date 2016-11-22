# Importations
from base.exceptions import RequeteInvalide
from log.mixin import ThreadLogMixin
from pystock import Stock
from settings import DOSSIER_RACINE

import queue
import threading as th
from time import sleep

# Classe
class QueueServeurThread(ThreadLogMixin, th.Thread):
    # Attributs
    timeout = 1
    _blacklist = []
    
    # Méthodes spéciales
    def __init__(self, queue):
        self.queue = queue
        self.fini  = False
        
        super(QueueServeurThread, self).__init__()
    
    # Méthodes
    def run(self):
        self._setup()
        
        try:
            while not self.fini:
                try:
                    requete, opts, nopts = self.queue.get(True, self.timeout)
                    
                    if requete == "fini":
                        break
                    
                    elif requete.startswith("_") or requete in ("run", "arreter") or requete in self._blacklist:
                        raise RequeteInvalide(requete, opts, nopts)
                    
                    else:
                        getattr(self, requete)(*opts, **nopts)
                
                except queue.Empty:
                   pass
                
                except Exception as err:
                    self._handle_erreur(err)
        
        finally:
            self._nettoyer()
    
    def _setup(self):
        pass
    
    def _nettoyer(self):
        pass
    
    def _handle_erreur(self, err):
        pass
    
    def arreter(self):
        self.fini = True
        self.queue.put(("fini", [], {}))
        self.join()
