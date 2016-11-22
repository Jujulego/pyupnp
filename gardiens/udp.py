# Importations
from .base import BaseGardien
from .requetes import BaseRequete
from .utils import identifiant_processus
from .thread import BaseThread

from base.decorateurs import verif_type
from base.wrapper import ThreadSafeWrapper
from base.utils import recupIp

from datetime import datetime
import multiprocessing as mp
import os
import select
import socket
import struct

# Setting
try:
    from settings import GARDIEN_NB_ENVOIS_UDP

except ImportError:
    GARDIEN_NB_ENVOIS_UDP = 5

# Classes
class UDPThread(BaseThread):
    # Méthodes spéciales
    def __init__(self, queue, pipe):
        self.queue = queue
        self.pipe  = pipe
        
        super(UDPThread, self).__init__(name="UDPGardien {}".format(identifiant_processus()), daemon=True)
    
    # Méthodes
    def run(self):
        sock = UDPGardien.creer_socket(*UDPGardien.multicast)
        fin    = False
        liste  = {}
        
        while not fin:
            try:
                rliste, _, _ = select.select([sock, self.pipe], [], [], 0.1)
                
                if sock in rliste:
                    requete, adresse = sock.recvfrom(1024)
                    
                    try:
                        requete = BaseRequete(requete)
                    
                    except ValueError:
                        continue
                    
                    self.debug("Reception de : {!r}".format(requete))
                    
                    if not requete.identifiant in liste:
                        liste[requete.identifiant] = 1
                        self.queue.put((adresse, requete))
                    
                    else:
                        liste[requete.identifiant] += 1
                        
                        if liste[requete.identifiant] >= GARDIEN_NB_ENVOIS_UDP:
                            del liste[requete.identifiant]
                
                if self.pipe in rliste:
                    message = self.pipe.recv()
                    
                    if message == "fin":
                        fin = True
            
            except select.error:
                pass
            
            except Exception as err:
                self.error("udp erreur : {!r}".format(err))
        
        mreq = struct.pack("=4sl", socket.inet_aton(UDPGardien.multicast[0]), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        
        sock.close()
        self.pipe.close()

class UDPGardien(BaseGardien):
    # Attributs
    multicast = ("239.0.0.255", 20000)
    
    # Méthodes spéciales
    def __init__(self):
        self._queue = mp.Queue()
        self._pipe, pipe = mp.Pipe()
        
        super(UDPGardien, self).__init__()
        
        self._thread = UDPThread(self._queue, pipe)
    
    # Méthodes statiques
    @staticmethod
    @verif_type(adresse=str, port=int)
    def creer_socket(adresse, port):
        """
        Crée un socket UDP, sur le multicast donné
        """
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
        
        sock.bind(('', port))
        
        mreq = struct.pack("=4sl", socket.inet_aton(adresse), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        return sock
    
    # Méthodes
    def lancer(self):
        super(UDPGardien, self).lancer()
        self._thread.start()
    
    def recevoir(self, block=True, timeout=None):
        assert self._status.objet == 1, "L'objet doit être actif"
        
        r = self._queue.get(block, timeout)
        
        return r
    
    @verif_type(message=BaseRequete, adresse=str, port=int, nb_envois=int)
    def envoyer(self, message, adresse=None, port=None, nb_envois=GARDIEN_NB_ENVOIS_UDP):
        adresse = adresse or self.multicast[0]
        port    = port or self.multicast[1]
        
        sock = self.creer_socket(*self.multicast)
        
        for _ in range(nb_envois):
            sock.sendto(message.requete, (adresse, port))
        
        sock.close()
    
    def arreter(self):
        super(UDPGardien, self).arreter()
        
        self._pipe.send("fin")
        
        self._thread.join()
        self._pipe.close()
