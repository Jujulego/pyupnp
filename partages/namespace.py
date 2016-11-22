# Importations
from argparse import Namespace as ArgparseNamespace

# Classe
class Namespace:
    # Méthodes spéciales
    def __init__(self, dictio):
        if isinstance(dictio, ArgparseNamespace):
            d = dictio
            dictio = {}
            
            for n, v in vars(d).items():
                if callable(v):
                    continue
                
                dictio[n] = v
        
        self._prepare(dictio)
    
    def __getstate__(self):
        return self.__dict__
    
    def __setstate__(self, etat):
        self._prepare(etat)
    
    # Méthodes privées
    def _prepare(self, dictio):
        for n, v in dictio.items():
            setattr(self, n, v)
