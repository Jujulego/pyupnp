# Imporatations
from .base import SSDPRequete
from .exceptions import SSDPErreur

from base.decorateurs import verif_type
from base.objets import FStr
from helper import Helper

from datetime import timedelta, datetime
import re

# Variables
helper = Helper()

# Fonction
def get_uuid(reg):
    if reg.groupdict().get("uuid") != None:
        return reg.groupdict().get("uuid").split('::')[0]
    else:
        return reg.groupdict().get("uuid")

# Classes
class SSDPNotify(SSDPRequete):
    '''
    Représente une requête d'avertissement (notify)
    '''
    
    # Attributs
    _default = {
        "methode": "NOTIFY",
        "host": "239.255.255.250:1900",
    }
    
    # Regex
    _re_nt_uuid = re.compile(r"^uuid:(?P<uuid>.+)$", re.IGNORECASE)
    _re_nt_urn  = re.compile(r"^urn:(?P<nom_domaine>.+):(?P<objet>(device)|(service)):(?P<type>[^:]+):(?P<version>[0-9]+)$", re.IGNORECASE)
    
    _re_usn = re.compile(r"^uuid:(?P<uuid>.+?)(::upnp:rootdevice)?$", re.IGNORECASE)
    _re_usn_urn  = re.compile(r"^uuid:(?P<uuid>.+?)::urn:(?P<nom_domaine>[^:]+):(?P<objet>(device)|(service)):(?P<type>[^:]+):(?P<version>[0-9]+)$", re.IGNORECASE)
    
    _re_cachecontrol = re.compile(r"^max-age ?= ?(?P<maxage>[0-9]+)", re.IGNORECASE)
    
    # Méthodes spéciales
    @verif_type(requete=(bytes, type(None)), ip_client=(tuple, type(None)), donnees=(dict, type(None)))
    def __init__(self, requete=None, ip_client=None, date=None, donnees=None):
        super(SSDPNotify, self).__init__(requete, ip_client, date, donnees)
        
        if donnees:
            pass
        
        elif hasattr(self, "methode"):
            if self.methode == "NOTIFY":
                self._analyse_notify()
            
            else:
                raise SSDPErreur("Ceci n'est pas une requête NOTIFY", self.message)
    
    def __repr__(self):
        try:
            return "<SSDPNotify {2} de {0[0]}:{0[1]} a {1}>".format(self.adresseClient, self.dateReception, self.nts)
        
        except AttributeError:
            return "<SSDPNotify nt='{0}'>".format(self.nt)
    
    # Méthodes privées
    def _analyse_notify(self):
        # Vérification de la présence de NT, NTS & USN
        nts = self.headers.get("NTS")
        nt = self.headers.get("NT")
        usn = self.headers.get("USN")
        
        if not nts or not nt or not usn:
            raise ValueError("Requête invalide ! Le(s) header(s) {} est/sont nécessaires !".format(
                (("nts, " if not nts else "") + ("nt, " if not nt else "") + ("usn, " if not usn else ""))[:-2]),
            )
            
        self.nt = nt
        self.usn = usn
        self.nts = nts
        
        if nts == "ssdp:alive":
            # Vérification de la présence de CACHE-CONTROL, SERVER & LOCATION
            cc = self.headers.get("CACHE-CONTROL")
            srv = self.headers.get("SERVER")
            loc = self.headers.get("LOCATION")
            
            if not cc or not srv or not loc:
                raise ValueError("Requête invalide ! Le(s) header(s) {} est/sont nécessaires !".format(
                    (("cc, " if not cc else "") + ("srv, " if not srv else "") + ("loc, " if not loc else ""))[:-2]),
                )
            
            self.cache_control = cc
            self.location = loc
            self.server = srv
        
        elif nts == "ssdp:byebye":
            pass
    
    # Méthodes de classe
    @classmethod
    @verif_type(location=str, nts=str, uuid=str, type=(str, type(None)), maxage=int, rootdevice=bool, nt_uuid=bool, nom_domaine=str, service=bool, version=str)
    def generer(cls, location, nts, uuid, type=None, maxage=helper.NOTIFY_MAX_AGE, rootdevice=False, nt_uuid=False, nom_domaine="schemas-upnp-org", service=False, version="1"):
        if rootdevice:
            nt = "upnp:rootdevice"
        
        elif nt_uuid:
            nt = "uuid:{}".format(uuid)
        
        else:
            if not type:
                raise ValueError("Argument type nécessaire")
            
            nt = "urn:{}:{}:{}:{}".format(nom_domaine, "service" if service else "device", type, version)
        
        if nts not in ("ssdp:alive", "ssdp:byebye"):
            raise ValueError("L'argument nts doit valoir soit 'ssdp:alive', soit 'ssdp:byebye'")
        
        donnees = {
            "nt": nt,
            "nts": nts,
            "usn": nt if nt_uuid else "uuid:{}::{}".format(uuid, nt),
        }
        
        if nts == "ssdp:alive":
            donnees["cache_control"] = "max-age = {:d}".format(maxage)
            donnees["location"] = location
        
        return cls(donnees=donnees)
    
    # Propriétés
    # Headers
    @property
    def nts(self):
        return self._nts
    
    @nts.setter
    @verif_type(nts=str)
    def nts(self, nts):
        if nts not in ("ssdp:alive", "ssdp:byebye"):
            raise ValueError("Mauvaise valeur de NTS")
        
        self._nts = nts
        self.headers["NTS"] = nts
    
    @property
    def nt(self):
        return self._nt
    
    @nt.setter
    @verif_type(nt=str)
    def nt(self, nt):
        nt_uuid = self._re_nt_uuid.match(nt)
        nt_urn  = self._re_nt_urn.match(nt)
        
        self._rootdevice = False
        self._nt_uuid = False
        self._nt_urn = False
        if nt == "upnp:rootdevice":
            self._rootdevice = True
        
        elif nt_urn:
            if self.uuid:
                if self.uuid != get_uuid(nt_urn):
                    raise ValueError("Valeurs de NT et de USN incohérentes : UUID différents")
            
            else:
                self._uuid = get_uuid(nt_urn)
            
            if self.nom_domaine:
                if self.nom_domaine != nt_urn.groupdict().get("nom_domaine"):
                    raise ValueError("Valeurs de NT et de USN incohérentes : Nom de Domaine différents")
            else:
                self._nom_domaine = nt_urn.groupdict().get("nom_domaine")
            
            if self.objet:
                if self.objet != nt_urn.groupdict().get("objet"):
                    raise ValueError("Valeurs de NT et de USN incohérentes : Objets différents")
            else:
                self._objet = nt_urn.groupdict().get("objet")
            
            if self.type:
                if self.type != nt_urn.groupdict().get("type"):
                    raise ValueError("Valeurs de NT et de USN incohérentes : Types différents")
            else:
                self._type = nt_urn.groupdict().get("type")
            
            if self.version:
                if self.version != nt_urn.groupdict().get("version"):
                    raise ValueError("Valeurs de NT et de USN incohérentes : Versions différents")
            else:
                self._version = nt_urn.groupdict().get("version")
        
        elif nt_uuid:
            if self.uuid:
                if self.uuid != get_uuid(nt_uuid):
                    raise ValueError("Valeurs de NT et de USN incohérentes : UUID différents")
            
            else:
                self._uuid = get_uuid(nt_uuid)
            
            if self.rootdevice != ("upnp:rootdevice" in nt):
                raise ValueError("Valeurs de NT et de USN incohérentes")
        
        else:
            raise ValueError("Mauvaise valeur de NT " + nt)
        
        self._nt = nt
        self.headers["NT"] = nt
    
    @property
    def usn(self):
        return self._usn
    
    @usn.setter
    @verif_type(usn=str)
    def usn(self, usn):
        re_usn  = self._re_usn.match(usn)
        usn_urn = self._re_usn_urn.match(usn)
        
        if usn_urn:
            if self.uuid:
                if self.uuid != get_uuid(usn_urn):
                    raise ValueError("Valeurs de NT et de USN incohérentes : UUID différents")
            
            else:
                self._uuid = get_uuid(usn_urn)
            
            if self.nom_domaine:
                if self.nom_domaine != usn_urn.groupdict().get("nom_domaine"):
                    raise ValueError("Valeurs de NT et de USN incohérentes : Nom de Domaine différents")
            else:
                self._nom_domaine = usn_urn.groupdict().get("nom_domaine")
            
            if self.objet:
                if self.objet != usn_urn.groupdict().get("objet"):
                    raise ValueError("Valeurs de NT et de USN incohérentes : Objets différents")
            else:
                self._objet = usn_urn.groupdict().get("objet")
            
            if self.type:
                if self.type != usn_urn.groupdict().get("type"):
                    raise ValueError("Valeurs de NT et de USN incohérentes : Types différents")
            else:
                self._type = usn_urn.groupdict().get("type")
            
            if self.version:
                if self.version != usn_urn.groupdict().get("version"):
                    raise ValueError("Valeurs de NT et de USN incohérentes : Versions différents")
            else:
                self._version = usn_urn.groupdict().get("version")
        
        elif re_usn:
            if self.uuid:
                if self.uuid != get_uuid(re_usn):
                    raise SSDPErreur("Requêtes invalide ! Valeurs de NT et de USN incohérentes : UUID différents", self.message)
            
            else:
                self._uuid = get_uuid(re_usn)
            
            if self.rootdevice != ("upnp:rootdevice" in usn):
                raise ValueError("Valeurs de NT et de USN incohérentes")
        
        else:
            raise ValueError("Mauvaise valeur de USN " + usn)
        
        self._usn = usn
        self.headers["USN"] = usn
    
    @property
    def cache_control(self):
        return self._cache_control
    
    @cache_control.setter
    @verif_type(cc=str)
    def cache_control(self, cc):
        re_cc = self._re_cachecontrol.match(cc)
        if re_cc:
            self._maxage = int(re_cc.groupdict().get("maxage"))
        
        else:
            raise ValueError("Mauvaise valeur pour CACHE-CONTROL")
        
        self._cache_control = cc
        self.headers["CACHE-CONTROL"] = cc
    
    @property
    def location(self):
        return self._location
    
    @location.setter
    @verif_type(loc=str)
    def location(self, loc):
        self._location = loc
        self.headers["LOCATION"] = loc
    
    @property
    def server(self):
        return self._server
    
    @server.setter
    @verif_type(srv=str)
    def server(self, srv):
        self._server = srv
        self.headers["SERVER"] = srv
    
    # Valeurs
    @property
    def uuid(self):
        if hasattr(self, "_uuid"):
            return self._uuid
        
        else:
            return None
    
    @property
    def nom_domaine(self):
        if hasattr(self, "_nom_domaine"):
            return self._nom_domaine
        
        else:
            return FStr("schemas-upnp-org")
    
    @property
    def objet(self):
        if hasattr(self, "_objet"):
            return self._objet
        
        else:
            return None
    
    @property
    def type(self):
        if hasattr(self, "_type"):
            return self._type
        
        else:
            return None
    
    @property
    def version(self):
        if hasattr(self, "_version"):
            return self._version
        
        else:
            return None
    
    @property
    def rootdevice(self):
        if hasattr(self, "_rootdevice"):
            return self._rootdevice
        
        else:
            return False
    
    @property
    def maxage(self):
        if hasattr(self, "_maxage"):
            return self._maxage
        
        else:
            return 0
    
    @property
    def valide(self):
        if self.nts == "ssdp:byebye":
            return True
        
        return datetime.now() <= self.dateReception + timedelta(seconds=self.maxage)
