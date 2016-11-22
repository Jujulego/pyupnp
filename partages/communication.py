# Importations
from base.communication import PickleMixin, BaseServeur
from base.decorateurs import verif_type

import pickle

# Mixins
class CommunicationMixin(PickleMixin, BaseServeur):
    pass

# Wrapper
class SocketFile(CommunicationMixin):
    # Méthodes spéciales
    def __init__(self, socket):
        self.socket = socket
    
    # Méthodes
    def read(self):
        return self.recevoir()
    
    def write(self, message):
        self.envoyer(message)
    
    def fileno(self):
        return self.socket.fileno()
    
    def close(self):
        pass
