# Importations
from base.mixin import ThreadingServerMixin
from log.mixin import ServerThreadLogMixin

from socketserver import TCPServer

# Classe
class PartageServeur(ServerThreadLogMixin, ThreadingServerMixin, TCPServer):
    # Attributs
    nom_log = "upnp.partages"
