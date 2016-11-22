# Importations
from base.communication import PickleMixin, BaseServeur

from socketserver import BaseRequestHandler

# Classe
class RecherchesHandler(BaseRequestHandler, PickleMixin, BaseServeur):
    # Méthodes
    def handle(self):
        self.socket = self.request
        
        try:
            # Réception
            action, kwargs = self.recevoir()
            
            # Action
            try:
                self.envoyer(getattr(self.server.recherches, action)(**kwargs))
            
            except Exception as err:
                self.envoyer(err)
        
        except ConnectionResetError:
            pass
    
    def finish(self):
        self.deconnecter()
