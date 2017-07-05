# Importations
from .base import SSDPRequete
from .exceptions import SSDPErreur

from base.decorateurs import verif_type
from base.objets import FStr
from helper import Helper

from datetime import datetime, timedelta
import re

# Variables
helper = Helper()

# Classes
class SSDPMSearch(SSDPRequete):
    '''
    Représente une requete MSEARCH
    '''
    
    # Attributs
    _default = {
        "methode": "M-SEARCH",
        "host": "239.255.255.250:1900",
    }
    
    # Regex
    _re_st_uuid = re.compile(r"^uuid:(?P<uuid>.+?)$", re.IGNORECASE)
    _re_st_urn  = re.compile(r"^urn:(?P<nom_domaine>[^:]+):(?P<objet>(device)|(service)):(?P<type>.+):(?P<version>[0-9]+)$", re.IGNORECASE)
    
    # Méthodes spéciales
    @verif_type(requete=(bytes, type(None)), ip_client=(tuple, type(None)), donnees=(dict, type(None)))
    def __init__(self, requete=None, ip_client=None, date=None, donnees=None):
        super(SSDPMSearch, self).__init__(requete, ip_client, date, donnees)
        
        if donnees:
            self.headers["MAN"] = '"ssdp:discover"'
        
        elif hasattr(self, "methode"):
            if self.methode == "M-SEARCH":
                self._analyse_msearch()
            
            else:
                raise SSDPErreur("Ceci n'est pas une requête M-SEARCH", self.message)
    
    def __repr__(self):
        try:
            return "<SSDPMSearch de {0[0]}:{0[1]} st={1}>".format(self.adresseClient, self.st)
        
        except AttributeError:
            return "<SSDPMSearch st='{0}'>".format(self.st)
    
    # Méthodes privées
    def _analyse_msearch(self):
        man = self.headers.get("MAN")
        mx  = self.headers.get("MX")
        st  = self.headers.get("ST")
        
        if not man or not mx or not st:
            raise ValueError("Requête invalide ! Le(s) header(s) {} est/sont nécessaires !".format(
                (("man, " if not man else "") + ("mx, " if not mx else "") + ("st, " if not st else ""))[:-2]),
            )
        
        if not "ssdp:discover" in man:
            raise ValueError("Requête invalide ! La valeur de MAN doit être '\"ssdp:discover\"'")
        
        self._man = man
        self.st = st
        self.mx = mx
    
    # Méthodes de classe
    @classmethod
    @verif_type(maxage=int, uuid=(str, type(None)), type=(str, type(None)), nom_domaine=str, version=str, all=bool, rootdevice=bool, service=bool)
    def generer(cls, maxage=helper.MSEARCH_MAX_AGE, uuid=None, type=None, nom_domaine="schemas-upnp-org", version="1", all=False, rootdevice=False, service=False):
        if type:
            st = "urn:{}:{}:{}:{}".format(nom_domaine, "service" if service else "device", type, version)
        
        elif uuid:
            st = "uuid:{}".format(uuid)
        
        elif all:
            st = "ssdp:all"
        
        elif rootdevice:
            st = "upnp:rootdevice"
        
        else:
            raise ValueError("Donnez soit 'type', 'uuid' ou mettez soit 'all' soit 'rootdevice' à True")
        
        return cls(donnees={
            "mx": str(maxage),
            "st": st,
        })
    
    # Propriétés
    # Headers
    @property
    def man(self):
        return '"ssdp:discover"'
    
    @property
    def mx(self):
        return self._mx
    
    @mx.setter
    @verif_type(mx=str)
    def mx(self, mx):
        if mx.isdigit():
            self._maxage = int(mx)
            self._mx = mx
            
            self.headers["MX"] = mx
        
        else:
            raise ValueError("Mauvaise valeur de MX")
    
    @property
    def st(self):
        if hasattr(self, "_st"):
            return self._st
        
        else:
            return None
    
    @st.setter
    @verif_type(st=str)
    def st(self, st):
        st_uuid = self._re_st_uuid.match(st)
        st_urn  = self._re_st_urn.match(st)
        
        self._ssdpall = False
        self._st_autre = False
        self._rootdevice = False
        self._st_uuid = False
        self._st_urn = False
        if st == "ssdp:all":
            self._ssdpall = True
        
        elif st in ("roku:ecp", "media:router"):
            self._st_autre = True
        
        elif st == "upnp:rootdevice":
            self._rootdevice = True
        
        elif st_uuid:
            self._uuid = st_uuid.groupdict().get("uuid")
            self._st_uuid = True
        
        elif st_urn:
            self._nom_domaine = st_urn.groupdict().get("nom_domaine")
            self._objet = st_urn.groupdict().get("objet")
            self._type = st_urn.groupdict().get("type")
            self._version = st_urn.groupdict().get("version")
            self._st_urn = True
        
        else:
            raise ValueError("Mauvaise valeur de ST " + st)
        
        self._st = st
        self.headers["ST"] = st
    
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
            return None
    
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
    def ssdpall(self):
        if hasattr(self, "_ssdpall"):
            return self._ssdpall
        
        else:
            return False
    
    @property
    def st_autre(self):
        if hasattr(self, "_st_autre"):
            return self._st_autre
        
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
        return datetime.now() <= self.dateReception + timedelta(seconds=self.maxage)

class SSDPReponseMSearch(SSDPRequete):
    """
    Représente une réponse à une requête MSearch
    """
    
    # Attributs
    _default = {
        "methode": "Reponse M-SEARCH",
        "ext": "",
        "host": "239.255.255.250:1900",
    }
    
    _date_format = "%a, %d %b %Y %H:%M:%S %Z" # Selon RFC 1123
    
    # Regex
    _re_st_uuid = re.compile(r"^uuid:(?P<uuid>.+?)$", re.IGNORECASE)
    _re_st_urn  = re.compile(r"^urn:(?P<nom_domaine>.+?):(?P<objet>(device)|(service)):(?P<type>.+):(?P<version>[0-9]+)$", re.IGNORECASE)
    
    _re_usn = re.compile(r"^uuid:(?P<uuid>.+?)(::upnp:rootdevice)?$", re.IGNORECASE)
    _re_usn_urn  = re.compile(r"^uuid:(?P<uuid>.+?)::urn:(?P<nom_domaine>[^:]+):(?P<objet>(device)|(service)):(?P<type>.+):(?P<version>[0-9]+)$", re.IGNORECASE)
    
    _re_cachecontrol = re.compile(r"^max-age ?= ?(?P<maxage>[0-9]+)", re.IGNORECASE)
    
    # Méthodes spéciales
    @verif_type(requete=(bytes, type(None)), ip_client=(tuple, type(None)), donnees=(dict, type(None)))
    def __init__(self, requete=None, ip_client=None, date=None, donnees=None):
        super(SSDPReponseMSearch, self).__init__(requete, ip_client, date, donnees)
        
        if donnees:
            self.headers["EXT"] = ""
        
        elif hasattr(self, "methode"):
            if self.methode == "Reponse M-SEARCH":
                self._analyse_repmsearch()
            
            else:
                raise SSDPErreur("Ceci n'est pas une requête Reponse M-SEARCH", self.message)
    
    def __repr__(self):
        try:
            return "<SSDPReponseMSearch de {0[0]}:{0[1]} le {1}>".format(self.adresseClient, self.dateReception)
        
        except AttributeError:
            return "<SSDPReponseMSearch st='{0}'>".format(self.st)
    
    # Méthodes privées
    def _analyse_repmsearch(self):
        st  = self.headers.get("ST")
        usn = self.headers.get("USN")
        date  = self.headers.get("DATE")
        ext = self.headers.get("EXT")
        cc = self.headers.get("CACHE-CONTROL")
        srv = self.headers.get("SERVER")
        loc = self.headers.get("LOCATION")
        
        if not st or not usn or ext != '' or not cc or not srv or not loc:
            raise SSDPErreur("Requête invalide ! Le(s) header(s) {} est/sont nécessaires !".format(
                (("st, " if not st else "") + ("usn, " if not usn else "") + ("ext, " if not ext else "") + ("cc, " if not cc else "") + ("srv, " if not srv else "") + ("loc, " if not loc else ""))[:-2]),
                self.message,
            )
        
        self.st = st
        self.usn = usn
        self.cache_control = cc
        self.location = loc
        self.serveur = srv
        
        if date:
            self.date = date
    
    # Méthodes de classe
    @classmethod
    @verif_type(location=str, st=(str, type(None)), uuid=str, type=(str, type(None)), maxage=int, nom_domaine=str, version=str, rootdevice=bool, st_uuid=bool, service=bool)
    def generer(cls, location, uuid, st=None, type=None, maxage=helper.NOTIFY_MAX_AGE, nom_domaine="schemas-upnp-org", version="1", rootdevice=False, st_uuid=False, service=False):
        if type:
            st = "urn:{}:{}:{}:{}".format(nom_domaine, "service" if service else "device", type, version)
        
        elif rootdevice:
            st = "upnp:rootdevice"
        
        elif st_uuid:
            st = "uuid:{}".format(uuid)
        
        elif st:
            st_uuid = st.startswith("uuid")
        
        else:
            raise ValueError("Donnez 'st' ou 'uuid' ou 'type' ou mettez 'rootdevice' à True")
        
        return cls(donnees={
            "location": location,
            "cache_control": "max-age={:d}".format(maxage),
            "st": st,
            "usn": st if st_uuid else "uuid:{}::{}".format(uuid, st),
        })
    
    # Propriétés
    # Headers
    @property
    def ext(self):
        return ''
    
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
    def date(self):
        return self._date
    
    @date.setter
    @verif_type(date=str)
    def date(self, date):
        try:
            self._dateCreation = datetime.strptime(date, self._date_format)
        
        except ValueError:
            raise ValueError("Mauvaise valeur de DATE")
        
        self._date = date
        self.headers["DATE"] = date
    
    @property
    def st(self):
        if hasattr(self, "_st"):
            return self._st
        
        else:
            return None
    
    @st.setter
    @verif_type(st=str)
    def st(self, st):
        st_uuid = self._re_st_uuid.match(st)
        st_urn  = self._re_st_urn.match(st)
        
        self._ssdpall = False
        self._rootdevice = False
        self._st_uuid = False
        self._st_urn = False
        if st == "ssdp:all":
            self._ssdpall = True
        
        elif st == "upnp:rootdevice":
            self._rootdevice = True
        
        elif st_urn:
            if self.nom_domaine:
                if self.nom_domaine != st_urn.groupdict().get("nom_domaine"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : Nom de Domaine différents")
            else:
                self._nom_domaine = st_urn.groupdict().get("nom_domaine")
            
            if self.objet:
                if self.objet != st_urn.groupdict().get("objet"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : Objets différents")
            else:
                self._objet = st_urn.groupdict().get("objet")
                
            if self.type:
                if self.type != st_urn.groupdict().get("type"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : Types différents")
            else:
                self._type = st_urn.groupdict().get("type")
                
            if self.version:
                if self.version != st_urn.groupdict().get("version"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : Versions différents")
            else:
                self._version = st_urn.groupdict().get("version")
        
        elif st_uuid:
            if self.uuid:
                if self.uuid != st_uuid.groupdict().get("uuid"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : UUID différents")
            
            else:
                self._uuid = st_uuid.groupdict().get("uuid")
            
            if self.rootdevice != ("upnp:rootdevice" in st):
                raise ValueError("Valeurs de ST et de USN incohérentes")
        
        else:
            raise ValueError("Mauvaise valeur de ST " + st)
        
        self._st = st
        self.headers["ST"] = st
    
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
                if self.uuid != usn_urn.groupdict().get("uuid"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : UUID différents")
            
            else:
                self._uuid = usn_urn.groupdict().get("uuid")
            
            if self.nom_domaine:
                if self.nom_domaine != usn_urn.groupdict().get("nom_domaine"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : Nom de Domaine différents")
            else:
                self._nom_domaine = usn_urn.groupdict().get("nom_domaine")
            
            if self.objet:
                if self.objet != usn_urn.groupdict().get("objet"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : Objets différents")
            else:
                self._objet = usn_urn.groupdict().get("objet")
                
            if self.type:
                if self.type != usn_urn.groupdict().get("type"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : Types différents")
            else:
                self._type = usn_urn.groupdict().get("type")
                
            if self.version:
                if self.version != usn_urn.groupdict().get("version"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : Versions différents")
            else:
                self._version = usn_urn.groupdict().get("version")
        
        elif re_usn:
            if self.uuid:
                if self.uuid != re_usn.groupdict().get("uuid"):
                    raise ValueError("Valeurs de ST et de USN incohérentes : UUID différents")
            
            else:
                self._uuid = re_usn.groupdict().get("uuid")
            
            if self.rootdevice != ("upnp:rootdevice" in usn):
                raise ValueError("Valeurs de ST et de USN incohérentes")
        
        else:
            raise ValueError("Mauvaise valeur de USN " + usn)
        
        self._usn = usn
        self.headers["USN"] = usn
    
    @property
    def location(self):
        return self._location
    
    @location.setter
    @verif_type(loc=str)
    def location(self, loc):
        self._location = loc
        self.headers["LOCATION"] = loc
    
    # Valeurs
    @property
    def uuid(self):
        if hasattr(self, "_uuid"):
            return self._uuid
        
        else:
            return None
    
    @property
    def dateCreation(self):
        if hasattr(self, "_dateCreation"):
            return self._dateCreation
        
        else:
            return None
    
    @property
    def maxage(self):
        if hasattr(self, "_maxage"):
            return self._maxage
        
        else:
            return 0
    
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
    def ssdpall(self):
        if hasattr(self, "_ssdpall"):
            return self._ssdpall
        
        else:
            return False
    
    @property
    def valide(self):
        return datetime.now() <= self.dateReception + timedelta(seconds=self.maxage)
