# Importations
from base.wrapper import ThreadSafeWrapper
from base.table import Table
from log.mixin import ServerThreadLogMixin

from socketserver import ThreadingTCPServer

# Classe
class PerifServeur(ServerThreadLogMixin, ThreadingTCPServer):
    # Attributs
    nom_log = "upnp.periferiques"
    timeout = 0.1
    
    # Méthodes spéciales
    def __init__(self, *args, **kwargs):
        self.perifs = ThreadSafeWrapper(Table(("uuid", "id", "periferique")))
        self.events = {}
        super(PerifServeur, self).__init__(*args, **kwargs)
