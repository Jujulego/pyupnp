# Importations
from base.communication import PickleMixin, BaseClient, BaseServeur
from base.exceptions import ErreurDistante
from helper import Helper

import socket

# Variables
helper = Helper()

# Classes
class Client(PickleMixin, BaseClient):
    # Attributs
    adresse = ("localhost", helper.PORT_PERIFERIQUES)
    
    # Méthodes
    def envoyer_requete(self, requete, *opts, **nopts):
        with self:
            # Envoi
            self.envoyer((requete, opts, nopts))
            
            # Réception
            reponse = self.recevoir()
            
            # Cas d'erreur
            if isinstance(reponse, Exception):
                raise ErreurDistante() from reponse
            
            return reponse

class Serveur(PickleMixin, BaseServeur):
    pass
