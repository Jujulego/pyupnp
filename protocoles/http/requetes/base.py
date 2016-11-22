# Importations
from .codes import str_code
from .dict_headers import DictHeaders
from .exceptions import HTTPErreur
from .headers import BaseHeader
from .meta import MetaRqHe, BaseRq

from base.decorateurs import verif_type

import re

# Arguments
__all__ = ["BaseRequete"]

# Classe
class BaseRequete(BaseRq, metaclass=MetaRqHe):
    # Attributs
    methodes = []
    
    # Méthodes spéciales
    @verif_type(entete=str, headers=str, corps=str)
    def __init__(self, entete, headers, corps):
        self.entete  = entete
        self.headers = DictHeaders(headers)
        self.corps   = corps
        
        self._check_headers()
    
    def __repr__(self):
        if self.est_reponse():
            return "<{} {:d} {}>".format(self.__class__.__name__, self.code, self.erreur)
        
        return "<{} {} {}>".format(self.__class__.__name__, self.methode, self.url)
    
    # Méthodes de classe
    @classmethod
    @verif_type(requete=str)
    def analyser(cls, requete):
        # Analyse générale
        result = re.match(r"(?P<entete>([^ ]+ (/[^ ]+|\*) )?HTTP/[0-9.]{3,}(?(2)\b| [0-9]{3} [^ ]+))\n(?P<headers>([^:]+: ?.+\n)*)\n*(?P<corps>(.*\n)*)\n*", requete)
        
        if result == None:
            raise HTTPErreur("Requete invalide ! {}".format(requete))
        
        result = result.groupdict()
        
        if len(cls.methodes) > 0:
            if result["entete"].startswith("HTTP/"):
                pass
            
            elif not result["entete"].split(' ')[0] in cls.methodes:
                raise HTTPErreur("Cette methode n'est pas supportée ! {} {}".format(result["entete"].split(' ')[0], cls.__name__))
        
        return cls(**result)
    
    @classmethod
    @verif_type(methode=(str, type(None)), url=(str, type(None)), version=str, code=(str, int, type(None)), headers=dict, corps=str)
    def generer(cls, methode=None, url=None, version="1.1", code=None, headers={}, corps='\n'):
        # Génération de l'entete
        if (methode != None) and (url != None):
            entete = "{} {} HTTP/{}".format(methode, url, version)
        
        elif (code != None):
            entete = "HTTP/{} {} {}".format(version, str(code), str_code(int(code)))
        
        # Génération des headers
        headers = '\n'.join(["{}: {}".format(n.upper(), v) for n, v in headers.items()])
        
        return cls.analyser("{}\n{}\n{}\n\n{}\n\n".format(entete, headers, corps))
    
    # Méthodes privées
    def _check_headers(self):
        for n, v in self.headers.headers():
            if not n in self._headers:
                continue
            
            if not getattr(self, "_check_{}".format(n))(v):
                raise HTTPErreur("Header {} invalide ! {}".format(n, v))
    
    def _gen_entete(self, arg1, arg2, arg3, rep):
        if rep:
            self.entete = "HTTP/{} {} {}".format(arg1, arg2, arg3)
        
        else:
            self.entete = "{} {} HTTP/{}".format(arg1, arg2, arg3)
    
    # Méthodes
    def est_reponse(self):
        return self.entete.startswith('HTTP/')
    
    # Propriétés
    @property
    def requete(self):
        return "{}\n{}\n{}\n\n{}\n\n".format(self.entete, self.headers._generer(), self.corps)
    
    @property
    def methode(self):
        if self.est_reponse():
            return None
        
        return self.entete.split(' ')[0]
    
    @methode.setter
    @verif_type(val=str)
    def methode(self, val):
        if self.est_reponse():
            raise HTTPErreur("Pas de méthode, c'est une réponse !")
        
        if not val in self.methodes:
            raise HTTPErreur("Cette méthode n'est pas supportée ! {} {}".format(val, self.__class__.__name__))
        
        self._gen_entete(val, self.url, self.versionHTTP, self.est_reponse())
    
    @property
    def url(self):
        if self.est_reponse():
            return None
        
        return self.entete.split(' ')[1]
    
    @url.setter
    @verif_type(val=str)
    def url(self, val):
        if self.est_reponse():
            raise HTTPErreur("Pas d'URL, c'est une réponse !")
        
        self._gen_entete(self.methode, val, self.versionHTTP, self.est_reponse())
    
    @property
    def versionHTTP(self):
        if self.est_reponse():
            return self.entete.split(' ')[0][5:]
        
        return self.entete.split(' ')[2][5:]
    
    @versionHTTP.setter
    @verif_type(val=str)
    def versionHTTP(self, val):
        if self.est_reponse():
            self._gen_entete(val, str(self.code), self.erreur, self.est_reponse())
        
        else:
            self._gen_entete(self.methode, val, self.versionHTTP, self.est_reponse())
    
    @property
    def code(self):
        if self.est_reponse():
            return int(self.entete.split(' ')[1])
        
        return None
    
    @code.setter
    @verif_type(val=(int, str))
    def code(self, val):
        if self.est_reponse():
            self._gen_entete(self.versionHTTP, str(val), str_code(int(val)), self.est_reponse())
        
        raise HTTPErreur("Pas de code d'erreur, c'est une requête !")
    
    @property
    def erreur(self):
        if self.est_reponse():
            return self.entete.split(' ')[2]
        
        return None
    
    @erreur.setter
    @verif_type(val=str)
    def erreur(self, val):
        if self.est_reponse():
            self._gen_entete(self.versionHTTP, self.erreur, val, self.est_reponse())
        
        raise HTTPErreur("Pas de message d'erreur, c'est une requête !")
