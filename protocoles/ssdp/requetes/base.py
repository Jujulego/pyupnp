# Importations
from .exceptions import SSDPErreur

from base.decorateurs import verif_type
from base.objets import OrdreDict
from helper import Helper

from os import uname
import re
from socket import getfqdn

# Variables
helper = Helper()

# Classes
class SSDPRequete:
    '''
    Permet l'analyse et la création de requetes SSDP
    '''
    
    # Attributs
    _default_base = {
        "host": "239.255.255.250:1900",
        "server": "{0[0]}/{0[1]} UPnP/1.0 pyUPnP/{1}".format(uname(), helper.VERSION)
    }
    
    # Regex:
    _re_requete = re.compile(br"^(((?P<methode>(NOTIFY)|(M-SEARCH)) \* HTTP/(?P<versionHTTP1>[0-9]+\.[0-9]+))|(HTTP/(?P<versionHTTP2>[0-9]+\.[0-9]+) 200 OK))$", re.IGNORECASE)
    _re_header  = re.compile(br"^(?P<nom>[a-z-]+): ?(?P<valeur>.*)$", re.IGNORECASE)
    
    # Bases
    _base_requete1 = "{methode} * HTTP/{versionHTTP}"
    _base_requete2 = "HTTP/{versionHTTP} 200 OK"
    _base_header   = "{nom}: {valeur!s}"
    
    versionHTTP = "1.1"
    
    # Méthodes spéciales
    @verif_type(requete=(bytes, type(None)), ip_client=(tuple, type(None)), donnees=(dict, type(None)))
    def __init__(self, requete=None, ip_client=None, date=None, donnees=None):
        '''
        Si donnée, l'ance l'analyse de la requete SSDP.
        '''
        
        if requete:
            self._analyse(requete)
            
            if not ip_client or not date:
                raise ValueError("L'adresse IP et la date de reception sont requis !")
            
            n = getfqdn(ip_client[0]).split('.')[0]
            if n.isdigit():
                n = ip_client[0]
            
            self.adresseClient = n, ip_client[1]
            self.dateReception = date
        
        elif donnees:
            self._donnees = donnees
            
            self.headers = OrdreDict()
            
            if hasattr(self, "_default"):
                self._default_base.update(self._default)
            
            self._default_base.update(donnees)
            
            for n, v in self._default_base.items():
                try:
                    setattr(self, n, v)
                
                except AttributeError:
                    setattr(self, "_" + n, v)
    
    def __repr__(self):
        try:
            return "<SSDPRequete {0} de {1[0]}:{1[1]} le {2}>".format(self.methode, self.adresseClient, self.dateReception)
        
        except AttributeError:
            return "<SSDPRequete {0}>".format(self.methode)
    
    # Tests
    def __eq__(self, obj):
        if isinstance(obj, SSDPRequete):
            return self.headers == obj.headers
        
        return False
    
    def __ne__(self, obj):
        if isinstance(obj, SSDPRequete):
            return self.headers != obj.headers
        
        return True
    
    # Pickle
    def __getstate__(self):
        '''
        Pour pickler l'objet: état = message en bytes
        '''
        
        if hasattr(self, "adresseClient") and hasattr(self, "dateReception"):
            return {"requete": self.message, "ip_client": self.adresseClient, "date": self.dateReception}
        
        else:
            return {"donnees": self._donnees}
    
    def __setstate__(self, etat):
        '''
        Pour dépickler l'objet: lance l'analyse de l'état
        '''
        
        self.__init__(**etat)
    
    # Méthodes privées
    @verif_type(requete=bytes)
    def _analyse(self, requete):
        lignes = requete.split(b"\r\n")
        
        requete = self._re_requete.match(lignes[0])
        if requete:
            if requete.groupdict().get("methode"):
                self._methode = requete.groupdict().get("methode").decode("utf-8")
                self.versionHTTP = requete.groupdict().get("versionHTTP1").decode("utf-8")
            
            else:
                self._methode = "Reponse M-SEARCH"
                self.versionHTTP = requete.groupdict().get("versionHTTP2").decode("utf-8")
        
        else:
            raise SSDPErreur("Requête invalide !", requete)
        
        self.headers = OrdreDict()
        for l in lignes[1:]:
            if l != b"":
                h = self._re_header.match(l)
                if h:
                    d = h.groupdict()
                    self.headers[d["nom"].decode("utf-8").upper()] = d["valeur"].decode("utf-8")
                
                else:
                    pass
        
        # Vérification de la valeur de HOST
        if self.methode != "Reponse M-SEARCH":
            self.host = self.headers.get("HOST")
    
    def _generer(self):
        lignes = []
        
        if self.methode != "Reponse M-SEARCH":
            lignes.append(self._base_requete1.format(methode=self.methode, versionHTTP=self.versionHTTP))
        
        else:
            lignes.append(self._base_requete2.format(versionHTTP=self.versionHTTP))
        
        for n, v in self.headers.ordre_keys_items():
            lignes.append(self._base_header.format(nom=n, valeur=v))
        
        lignes.append("")
        
        return ("\r\n".join(lignes)).encode("utf-8")
    
    # Propriétés
    @property
    def message(self):
        return self._generer()
    
    @property
    def methode(self):
        return self._methode
    
    # Headers
    @property
    def host(self):
        return self._host
    
    @host.setter
    @verif_type(host=str)
    def host(self, host):
        if not host.startswith("239.255.255.250"):
            raise ValueError("Le header HOST doit contenir à '239.255.255.250'")
        
        self._host = host
        self.headers["HOST"] = host
    
    @property
    def server(self):
        return self._server
    
    @server.setter
    @verif_type(srv=str)
    def server(self, srv):
        self._server = srv
        self.headers["SERVER"] = srv
