# Importations
from base.decorateurs import verif_type
from log.mixin import ThreadLogMixin

from http.client import HTTPConnection
import re

# Classes :
class ClientHTTP(ThreadLogMixin):
    """
    Client HTTP
    """
    
    # Arguments
    nom_log = "upnp.http"
    
    # Méthodes spéciales
    @verif_type(hote=str, port=int, timeout=int)
    def __init__(self, hote, port=80, timeout=10):
        self.hote = hote
        self.port = port
        
        self.debug("Connection à {}:{:d}".format(hote, port))
        self.connection = HTTPConnection(host=hote, port=port, timeout=10)
    
    # Méthodes de classe
    @classmethod
    @verif_type(url=str, methode=str)
    def depuisAdresse(cls, url, methode="get"):
        regex = re.compile(r"http://(?P<hote>[a-zA-Z0-9.]+):?(?P<port>[0-9]{1,5})?(?P<url>/.*)")
        resultat = regex.match(url)
        
        if resultat:
            resultat = resultat.groupdict()
            client = cls(hote=resultat["hote"], port=int(resultat.get("port", "80")))
            
            return getattr(client, methode.lower())(resultat["url"])
        
        else:
            raise ValueError("Cette adresse n'est pas valide : {}".format(url))
    
    # Méthodes
    @verif_type(adresse=str)
    def get(self, adresse):
        self.debug("Envoi d'une requête GET à {}:{:d} pour {}".format(self.hote, self.port, adresse))
        
        try:
            self.connection.request("GET", url=adresse)
            
            reponse = self.connection.getresponse()
        
        except OSError as err:
            self.warning("Impossible de se connecter à http://{}:{:d}{} : {}".format(self.hote, self.port, adresse, (err.strerror or "timeout error")))
            return err, False
        
        except Exception as err:
            self.warning("Erreur pendant la connexion à http://{}:{:d}{} : {!r}".format(self.hote, self.port, adresse, err))
            return err, False
        
        self.info("Réponse reçue {} (code: {}, url: {})".format(reponse.reason, reponse.status, adresse))
        return reponse, True
    
    def fermer(self):
        self.connection.close()
