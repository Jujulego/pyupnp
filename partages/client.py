# Importations
from .namespace import Namespace

from settings import PORT_PARTAGE

from base.communication import PickleMixin, BaseClient

import pickle
import socket

# Classes
class Client(PickleMixin, BaseClient):
    # Méthodes spéciales
    def __init__(self, adresse, port=PORT_PARTAGE):
        self.adresse = (adresse, port)
        
        super(Client, self).__init__()
    
    # Méthodes
    def lancer(self, action, args):
        # Connexion
        with self:
            # Envoi requête
            self.envoyer((action, Namespace(args)))
            
            # Affichage du retour
            while True:
                try:
                    retour = self.recevoir()
                    
                    if retour == b"fini":
                        break
                    
                    print(retour.decode('utf-8'), end='')
                
                except KeyboardInterrupt:
                    self.envoyer(b"arret");
