# Importations
from .base import BaseXMLParser, XMLInterrupt

# Classe
class UPnPBaseXMLParser(BaseXMLParser):
    # Attributs
    nom_log   = "upnp"
    _base_url = ""
    
    # Méthodes privées
    def _join_url(self, url):
        if url.startswith("http://"):
            return url
        
        while self._base_url.endswith('/'):
            self._base_url = self._base_url[:-1]
        
        while url.startswith('/'):
            url = url[1:]
        
        return '/'.join((self._base_url, url))
    
    # Méthodes
    def check_specVersion(self):
        elem  = self.find(self.racine, "specVersion", True)
        major = self.find(elem, "major", True)
        minor = self.find(elem, "minor", True)
        
        if major.text != "1":
            raise XMLInterrupt("Arbre invalide : mauvaise version de la spécification", "warning")
        
        self.spec_version = ".".join((major.text, minor.text))
