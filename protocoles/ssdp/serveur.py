# Importations
from base.mixin import ThreadingServerMixin
from base.wrapper import ThreadSafeWrapper
from log.mixin import ServerThreadLogMixin

import socket
from socketserver import UDPServer
import struct

# Classes
class SSDPServeur(ServerThreadLogMixin, ThreadingServerMixin, UDPServer):
    # Attributs
    nom_log = "upnp.ssdp"
    
    multicast  = "239.255.255.250"
    port       = 1900
    timetolive = 4
    
    allow_reuse_address = True
    
    # Méthodes spéciales
    def __init__(self, *args, **kwargs):
        self.periferiques = ThreadSafeWrapper({})
        super(SSDPServeur, self).__init__(*args, **kwargs)
    
    # Méthodes privées
    def _prepare_socket(self, sock):
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.timetolive)
        
        mreq = struct.pack('4sl', socket.inet_aton(self.multicast), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    # Méthodes
    def server_bind(self):
        super(SSDPServeur, self).server_bind()
        self._prepare_socket(self.socket)
