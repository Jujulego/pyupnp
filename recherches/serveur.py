# Importations
from .dict import RecherchesDict

from socketserver import ThreadingTCPServer

# Classe
class RecherchesServeur(ThreadingTCPServer):
    # Méthodes spéciales
    def __init__(self, *args, **kwargs):
        self.recherches = RecherchesDict()
        
        super(RecherchesServeur, self).__init__(*args, **kwargs)
