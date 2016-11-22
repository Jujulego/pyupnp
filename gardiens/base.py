# Importations
from base.wrapper import ThreadSafeWrapper

# Classes
class BaseGardien:
    # Méthodes spéciales
    def __init__(self):
        self._status = ThreadSafeWrapper(0)
    
    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.status)
    
    # Méthodes
    def lancer(self):
        with self._status:
            assert self._status.objet == 0, "L'objet a déjà été lancé"
            self._status.objet += 1
    
    def arreter(self):
        with self._status:
            assert self._status.objet == 1, "L'objet doit être actif"
            self._status.objet += 1
    
    # Propriétés
    @property
    def status(self):
        if self._status.objet == 0:
            return "initial"
        
        elif self._status.objet == 1:
            return "actif"
        
        else:
            return "terminé"
