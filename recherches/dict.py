# Importations
from base.wrapper import ThreadSafeWrapper

from datetime import datetime
from time import sleep

# Classe
class RecherchesDict:
    # Méthodes spéciales
    def __init__(self):
        self._recherches = ThreadSafeWrapper({})
    
    def __getitem__(self, nom):
        return self._recherches.objet[nom]
    
    def __setitem__(self, nom, val):
        with self._recherches:
            self._recherches.objet[nom] = val
    
    def __delitem__(self, nom):
        with self._recherches:
            del self._recherches.objet[nom]
    
    def __contains__(self, nom):
        return nom in self._recherches.objet
    
    # Méthodes
    def creer_recherche(self, requete, date_limite):
        contenu = {
            "date_limite": date_limite,
            "recherche"  : requete,
            "reponses"   : [],
        }
        
        self[requete.st] = ThreadSafeWrapper(contenu)
    
    def ajouter_reponse(self, nom, requete):
        if requete.dateReception > self[nom].objet["date_limite"]:
            return
        
        with self[nom]:
            self[nom].objet["reponses"].append(requete)
    
    def recup_recherche(self, nom):
        assert nom in self, "Recherche {} inconnue".format(nom)
        
        temps_attente = (self[nom].objet["date_limite"] - datetime.now()).total_seconds() + 1
        
        if temps_attente >= 0:
            sleep(temps_attente)
        
        contenu = self[nom].objet
        del self[nom]
        
        return contenu
