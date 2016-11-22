# Importations
from .exceptions import GENAErreur

from base.decorateurs import verif_type

import abc
import re

# Métaclasse
class MetaRequete(abc.ABCMeta):
    # Attributs
    __registre_cls__ = {}
    
    # Méthodes
    def __new__(metacls, nom, base, attrs):
        cls = super(MetaRequete, metacls).__new__(metacls, nom, base, attrs)
        
        if hasattr(cls, "methode"): # Pour les requetes !
            metacls.__registre_cls__[cls.methode] = cls
        
        return cls

# Classe
class BaseRequete(metaclass=MetaRequete):
    # Attributs
    _regex_requete = re.compile(r"^(?P<entete>.+)\n(?P<headers>(.+\n)+)\n*(?P<corps>(.+\n)+)?$")
    _regex_entete  = re.compile(r"^((?P<methode>((UN)?SUBSCRIBE)|(NOTIFY)) (?P<url>.+) )?HTTP/(?P<versionHTTP>[0-9.]+)(?(1)$| (?P<code>[0-9]{3}) (?P<message>.+)$)")
    _regex_header  = re.compile(r"^(?P<nom>[A-Za-z-]+): ?(?P<valeur>.+)$")
    
    # Méthodes spéciales
    def __init__(self, entete, headers, corps):
        self._entete  = entete
        self._headers = headers
        self._corps   = corps
    
    # Méthodes de classe
    @classmethod
    def analyser(cls, requete):
        resultat = cls._analyser(requete)
        
        if resultat["entete"]["methode"] != None:
            cls = cls.__registre_cls__[resultat["entete"]["methode"]]
        
        cls._check_requete(resultat, requete)
        return cls(**resultat)
    
    @classmethod
    def _analyser(cls, requete):
        resultat = {}
        
        # Structure
        result1 = cls._regex_requete.match(requete)
        
        if result1 == None:
            raise GENAErreur("Format de requete invalide", requete)
        
        entete            = result1.groupdict()["entete"]
        headers           = result1.groupdict()["headers"]
        resultat["corps"] = result1.groupdict()["corps"]
        
        # Check entête
        result2 = cls._regex_entete.match(entete)
        
        if result2 == None:
            raise GENAErreur("Requete inconnue : {}".format(entete), requete)
        
        resultat["entete"] = result2.groupdict()
        
        # Analyse headers
        resultat["headers"] = {}
        
        for header in headers.split('\n')[:-1]:
            resulth = cls._regex_header.match(header)
            
            if resulth == None:
                raise GENAErreur("Header invalide : {}".format(header), requete)
            
            resultat["headers"][resulth.groupdict()["nom"].upper()] = resulth.groupdict()["valeur"]
        
        return resultat
    
    # Propriétés
    @property
    def requete(self):
        entete = ""
        
        if self._entete["methode"] != None:
            entete = "{0[methode]} {0[url]} HTTP/{0[versionHTTP]}".format(self._entete)
        
        else:
            entete = "HTTP/{0[versionHTTP]} {0[code]} {0[message]}".format(self._entete)
        
        headers = ""
        
        for n, v in self._headers.items():
            headers += "{}: {}\n".format(n, v)
        
        return "{}\n{}\n{}\n\n".format(entete, headers, self._corps or "")
