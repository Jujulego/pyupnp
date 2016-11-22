# Importations
from .actions.base import MetaAction
from .communication import CommunicationMixin, SocketFile

from log.mixin import ThreadLogMixin

import pickle
from socketserver import BaseRequestHandler

# Classes
class PartageHandler(BaseRequestHandler, CommunicationMixin, ThreadLogMixin):
    # Attributs
    actions = MetaAction.__registre_classes__
    nom_log = "upnp.partages"
    
    # Méthodes
    def handle(self):
        self.socket = self.request
        
        try:
            # Réception
            action, args = self.recevoir()
            self.info("Requete {0} de {1[0]}:{1[1]}".format(action, self.client_address))
            
            # Action
            action = self.actions[action](args, stdout=SocketFile(self.socket), bytes=True)
            action.lancer()
            
            # Fin
            self.envoyer(b"fini")
        
        except ConnectionResetError:
            pass
    
    def finish(self):
        self.deconnecter()
