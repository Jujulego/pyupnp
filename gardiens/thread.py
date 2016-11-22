# Importations
from base.wrapper import ThreadSafeWrapper
from log.mixin import LogMixin

import multiprocessing as mp
import threading as th

# Classe
class BaseThread(th.Thread, LogMixin):
    # Attributs
    nom_log = "gardien"
    _arret_gardien = ThreadSafeWrapper(False)
    
    # Méthodes
    def join(self, timeout=None):
        if not self._arret_gardien.objet and (mp.current_process().gardien.status == "actif"):
            with self._arret_gardien:
                self._arret_gardien.objet = True
            
            mp.current_process().gardien.arreter()
        
        else:
            super(BaseThread, self).join(timeout)

class PreparationThread(th.Thread):
    # Attributs
    __registre__ = ThreadSafeWrapper([])
    
    # Méthodes spéciales
    def __init__(self, *args, **kwargs):
        with self.__registre__:
            self.__registre__.objet.append(self)
        
        super(PreparationThread, self).__init__(*args, **kwargs)
    
    # Méthodes
    def join(self):
        with self.__registre__:
            if self in self.__registre__.objet:
                self.__registre__.objet.remove(self)
        
        super(PreparationThread, self).join()
