# Importations
from base.communication import PickleMixin, BaseClient
from helper import Helper

from datetime import datetime, timedelta

# Variables
helper = Helper()

# Classe
class RecherchesClient(PickleMixin, BaseClient):
    # Méthodes spéciales
    def __init__(self, adresse='localhost', port=helper.PORT_RECHERCHES):
        self.adresse = (adresse, port)
        
        super(RecherchesClient, self).__init__()
    
    # Méthodes
    def methode(self, nom, kwargs):
        with self:
            self.envoyer((nom, kwargs))
            retour = self.recevoir()
            
            if isinstance(retour, Exception):
                raise retour
            
            else:
                return retour

class DistantRecherches:
    # Méthodes spéciales
    def __init__(self):
        self._client = RecherchesClient()
    
    def __getitem__(self, nom):
        return self._client.methode("__getitem__", {"nom": nom})
    
    def __contains__(self, nom):
        return self._client.methode("__contains__", {"nom": nom})
    
    # Méthodes
    def creer_recherche(self, requete):
        return self._client.methode("creer_recherche", {"requete": requete, "date_limite": datetime.now() + timedelta(seconds=requete.maxage)})
    
    def ajouter_reponse(self, nom, requete):
        return self._client.methode("ajouter_reponse", {"nom": nom, "requete": requete})
    
    def recup_recherche(self, nom):
        return self._client.methode("recup_recherche", {"nom": nom})
