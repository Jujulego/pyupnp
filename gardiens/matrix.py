# Importations
from .checker import AdresseIP
from .requetes import MatrixRequete
from .tcp import TCPConnexion

import pickle

# Classes
class MatrixClient:
    # Méthodes spéciales
    def __init__(self, adresse):
        self.connexion = TCPConnexion(adresse)
    
    # Méthodes
    def connecter(self):
        self.connexion.connecter()
    
    def recup_statuts(self):
        self.connexion.envoyer(MatrixRequete.generer(message=b"matrix !").requete)
        return pickle.loads(self.connexion.recevoir())
    
    def deconnecter(self):
        self.connexion.deconnecter()
