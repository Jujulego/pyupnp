# Importations
from .variables.base import BaseVariable
from .actions import Action

from base.objets import Namespace

# Classe
class Service:
    # Méthodes spéciales
    def __init__(self, perif, ident):
        self.perif = perif
        self._ident = ident
    
    def __repr__(self):
        return "<Service {}>".format(self.identifiant)
    
    # Propriété
    @property
    def _infos(self):
        return self.perif._recup_services()[self._ident]
    
    # Informations
    @property
    def infos(self):
        return self._infos["infos"]
    
    @property
    def identifiant(self):
        return self._ident
    
    @property
    def type(self):
        return self.infos["type"]
    
    @property
    def version(self):
        return self.infos["version"]
    
    @property
    def namespaces(self):
        return (self.infos["namespaceId"], self.infos["namespaceType"])
    
    # Variables/Actions
    @property
    def variables(self):
        return list(self._infos["variables"].values())
    
    @property
    def actions(self):
        return list(self._infos["actions"].values())
