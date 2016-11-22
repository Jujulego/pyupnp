# Importations
from base.decorateurs import verif_type

import re

# Classe
class DictHeaders:
    # Méthodes spéciales
    @verif_type(headers=str)
    def __init__(self, headers):
        self._string = headers
        self._dict   = {}
        
        self._analyser()
    
    def __repr__(self):
        return "<DictHeaders {!r}>".format(self._dict)
    
    def __getitem__(self, nom):
        self._analyser()
        return self._dict[nom]
    
    def __setitem__(self, nom, val):
        self._dict[nom] = val
        self._generer()
    
    def __delitem__(self, nom):
        del self._dict[nom]
        self._generer()
    
    # Méthodes privées
    def _analyser(self):
        self._dict = {}
        
        for h in self._string.split('\n'):
            result = re.match(r"^(?P<nom>.+?): ?(?P<valeur>.+)?$", h)
            
            if result:
                self._dict[result.groupdict()["nom"].upper()] = result.groupdict()["valeur"]
    
    def _generer(self):
        self._string = []
        
        for n, v in self._dict.items():
            if v == None:
                self._string.append("{}:".format(n))
            
            else:
                self._string.append("{}: {}".format(n, v))
        
        self._string = "\n".join(self._string)
    
    # Méthodes
    @verif_type(defauts=dict)
    def appliquer_defauts(self, defauts):
        self._analyser()
        
        for n, v in defauts:
            n = n.upper()
            
            if not n in self._dict:
                self._dict[n] = v
        
        self._generer()
    
    @verif_type(nom=str)
    def recup_header(self, nom):
        self._analyser()
        
        nom = nom.upper()
        return self._dict[nom]
    
    @verif_type(nom=str, val=(str,type(None)))
    def chg_header(self, nom, val):
        self._analyser()
        
        nom = nom.upper()
        self._dict[nom] = val
        
        self.generer()
    
    @verif_type(nom=str)
    def suppr_header(self, nom):
        self._analyser()
        
        nom = nom.upper()
        del self._dict[nom]
        
        self._generer()
    
    def headers(self):
        return self._dict.items()
    
    # Propriétés
    @property
    def string(self):
        self._generer()
        return self._string
    
    @property
    def dict(self):
        self._analyser()
        return self._dict
