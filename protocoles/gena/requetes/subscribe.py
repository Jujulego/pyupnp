# Importations
from .base import BaseRequete
from .exceptions import GENAErreur

from base.decorateurs import verif_type
from helper import Helper
from protocoles.http.requetes.codes import str_code

from datetime import datetime
from os import uname
import re

# Variables
helper = Helper()

# Classe
class SubscribeRequete(BaseRequete):
    # Attributs
    methode = "SUBSCRIBE"
    _regex_host = re.compile(r"(?P<hote>.+)(:(?P<port>[0-9]{,5}))?")
    
    # Méthodes de classes
    @classmethod
    def _check_requete(cls, resultat, requete):
        headers = {}
        
        for nom in resultat["headers"]:
            if nom == "SID":
                headers[nom] = 2
            
            elif nom in ["HOST", "CALLBACK", "NT", "TIMEOUT"]:
                headers[nom] = 1
            
            else:
                raise GENAErreur("Requete Subscribe invalide, Header inconnu : {}".format(nom), requete)
        
        if sum(headers.values()) != 4:
            raise GENAErreur("Requete Subscribe invalide", requete)
    
    @classmethod
    @verif_type(pub_url=str, del_urls=list, duree=(int, str))
    def generer(cls, pub_url, del_urls, duree):
        # Analyse de l'URL de publication
        result = re.match(r"(http://)?(?P<hote>[^:]+)(:(?P<port>[0-9]{1,5}))?(?P<chemin>/.+)", pub_url)
        
        if result == None:
            raise GENAErreur("URL de publication invalide !")
        
        # Génération du CALLBACK
        callback = ""
        
        for d in del_urls:
            r = re.match(r"(http://)?(?P<hote>[^:]+)(:(?P<port>[0-9]{1,5}))?(?P<chemin>/.+)", pub_url)
            
            if r == None:
                raise GENAErreur("URL de reception invalide !")
        
            callback += "<{}{}>".format("" if d.startswith("http://") else "http://", d)
        
        # Génération de la requete
        rq = "SUBSCRIBE {pub_path} HTTP/1.1\nHOST: {pub_hote}:{pub_port}\nCALLBACK: {callback}\nNT: upnp:event\nTIMEOUT: Second-{duree}\n\n".format(
            pub_path = result.groupdict()["chemin"],
            pub_hote = result.groupdict()["hote"],
            pub_port = result.groupdict()["port"] or "80",
            callback = callback,
            duree    = str(duree),
        )
        
        return cls.analyser(rq)
    
    # Propriétés
    @property
    def chemin_publication(self):
        return self._entete["url"]
    
    @property
    def hote(self):
        l = self._headers["HOST"].split(':')
        hote = l[0].strip()
        port = 80
        
        if len(l) > 1:
            port = int(l[1].strip())
        
        return hote, port
    
    @property
    def callback(self):
        return self._headers.get("CALLBACK", None)[1:-1].split("><")
    
    @property
    def sid(self):
        if "SID" in self._headers:
            return self._headers["SID"][5:]
        
        return None
    
    @property
    def timeout(self):
        return int(self._headers["TIMEOUT"][7:])

class SubscribeReponse(BaseRequete):
    # Attributs
    date_format = "%a, %d %b %Y %H:%M:%S %Z" # RFC 1123
    
    # Méthodes de classes
    @classmethod
    def _check_requete(cls, resultat, requete):
        headers = {}
        
        if resultat["entete"]["code"] == "200":
            for nom in resultat["headers"]:
                if nom in ["DATE", "SERVER", "SID", "TIMEOUT"]:
                    headers[nom] = 1
                
                else:
                    raise GENAErreur("Requete Subscribe invalide, Header inconnu : {}".format(nom), requete)
            
            if sum(headers.values()) != 4:
                raise GENAErreur("Requete Subscribe invalide", requete)
    
    @classmethod
    @verif_type(sid=str, timeout=(int, str), code=int)
    def generer(cls, sid, timeout, code=200):
        # Gestion du code d'erreur
        if code != 200:
            message = str_code(code)
            
            return cls.analyser("HTTP/1.1 {:d} {}\n\n".format(code, message))
        
        # Check SID
        if not sid.startswith("uuid:"):
            sid = "uuid:" + sid
        
        # Check Timeout
        timeout = str(timeout)
        if re.match(r"([0-9]+)|(infinite)", timeout) == None:
            raise GENAErreur("Timeout invalide ! soit un nombre, soit 'infinite'")
        
        # Generer Server
        server = "{0[0]}, UPnP/1.0, pyUPnP/{1}".format(uname(), helper.VERSION)
        
        # Generer Date
        date   = datetime.now().strftime(cls.date_format)
        
        # Génération réponse
        rq = "HTTP/1.1 200 OK\nDATE: {date}\nSERVER: {server}\nSID: {sid}\nTIMEOUT: Second-{timeout}\n\n".format(**locals())
        
        return cls.analyser(rq)
    
    # Propriétés
    @property
    def code(self):
        return int(self._entete["code"])
    
    @property
    def message(self):
        return self._entete["message"]
    
    @property
    def date(self):
        if self.code == 200:
            return datetime.strptime(self._headers["DATE"], self.date_format)
    
    @property
    def server(self):
        if self.code == 200:
            return self._headers["SERVER"]
    
    @property
    def sid(self):
        if self.code == 200:
            return self._headers["SID"][5:]
    
    @property
    def timeout(self):
        if self.code == 200:
            return self._headers["TIMEOUT"][7:]
