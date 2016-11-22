# Importations
from .meta import MetaRqHe, BaseHe

from base.decorateurs import verif_type

import re

# Classes
class BaseHeader(BaseHe, metaclass=MetaRqHe):
    pass

class HOSTHeader(BaseHeader):
    # Attributs
    nom = "HOST"
    
    port_defaut = 80
    
    # Méthodes
    def _check_HOST(self, val):
        return re.match(r"[^:]+(:[0-9]{1,5})?", val) != None
    
    @verif_type(hote=str, port=int)
    def _modif_HOST(self, hote, port):
        self._headers["HOST"] = "{}:{:d}".format(hote, port)
    
    # Propriétés
    @property
    def hote(self):
        return self.headers["HOST"].split(":")[0]
    
    @hote.setter
    @verif_type(val=str)
    def hote(self, val):
        self._modif_HOST(val, self.port)
    
    @property
    def port(self):
        r = self.headers["HOST"].split(":")
        
        if len(r) == 1:
            return self.port_defaut
        
        return int(r[1])
    
    @port.setter
    @verif_type(val=int)
    def port(self, val):
        self._modif_HOST(self.hote, str(val))
