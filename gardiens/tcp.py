# Importations
from .base import BaseGardien
from .checker import AdresseIP
from .exceptions import AdresseInvalideErreur
from .requetes import BaseRequete, InfoRequete, ModificationRequete, MatrixRequete
from .utils import identifiant_processus
from .thread import BaseThread

from base.utils import recupIp
from base.wrapper import ThreadSafeWrapper

import multiprocessing as mp
import pickle
import select
import socket
import threading as th

# Classes
class TCPThread(BaseThread):
    # Méthodes spéciales
    def __init__(self, port, queue, pipe):
        self.queue = queue
        self.pipe = pipe
        self.adresse = AdresseIP(recupIp(), port, False)
        
        super(TCPThread, self).__init__(name="TCPThread " + identifiant_processus())
    
    # Méthodes
    def creer_socket(self):
        sock_srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        while True:
            try:
                sock_srv.bind(self.adresse.tuple)
                break
            
            except OSError as err:
                if err.errno != 98:
                    raise
                
                self.adresse.port += 1
            
            except LookupError as err:
                err.args = (err.args[0] + " " + str(self.adresse.tuple),)
                raise err
        
        sock_srv.listen(5)
        
        return sock_srv
    
    def run(self):
        sock_srv = self.creer_socket()
        connexions = []
        
        while True:
            try:
                rliste, _, _ = select.select([sock_srv, self.pipe], [], [], 0.005)
                
                if self.pipe in rliste:
                    message = self.pipe.recv()
                    
                    if message == "fin":
                        break
                
                if sock_srv in rliste:
                    sock_c, _ = sock_srv.accept()
                    connexions.append(sock_c)
                
                rliste, _, _ = select.select(connexions, [], [], 0.005)
                
                for sock in rliste:
                    rq = sock.recv(1024)
                    
                    if InfoRequete.test(rq):
                        rq = InfoRequete(rq)
                        self.debug("Reception de {!r}".format(rq))
                        
                        try:
                            sock.send(pickle.dumps(getattr(self.gardien.garde.objet, rq.objet)(rq.id_lock)))
                        
                        except Exception as err:
                            sock.send(pickle.dumps(err))
                    
                    elif ModificationRequete.test(rq):
                        rq = ModificationRequete(rq)
                        self.debug("Reception de {!r}".format(rq))
                        
                        self.queue.put((sock, rq))
                    
                    elif MatrixRequete.test(rq):
                        rq = MatrixRequete(rq)
                        self.debug("Reception de {!r}".format(rq))
                        
                        sock.send(pickle.dumps([x["statut"] for x in self.gardien.garde.objet.values()]))
                    
                    elif rq in [b"fin connexion", b"check"]:
                        self.debug("Reception de {!r}".format(rq))
                        
                        sock.send(b"ok")
                        
                        sock.shutdown(socket.SHUT_RDWR)
                        sock.close()
                        
                        connexions.remove(sock)
            
            except Exception as err:
                self.error("tcp erreur : " + repr(err))
        
        for sock in connexions:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        
        sock_srv.close()
        self.pipe.close()
    
    # Propriétés
    @property
    def gardien(self):
        return mp.current_process().gardien

class TCPGardien(BaseGardien):
    # Méthodes spéciales
    def __init__(self, port=20001):
        self.queue = mp.Queue()
        self.pipe, pipe = mp.Pipe()
        
        super(TCPGardien, self).__init__()
        
        self.thread = TCPThread(port, self.queue, pipe)
    
    def __repr__(self):
        return "<TCPGardien {0[0]}:{0[1]} {1}>".format(self.thread.adresse, self.statut)
    
    # Méthodes
    def lancer(self):
        super(TCPGardien, self).lancer()
        
        self.thread.start()
    
    def recevoir_modif(self, block=True, timeout=None):
        assert self._status.objet == 1, "L'objet doit être actif"
        return self.queue.get(block, timeout)
    
    def arreter(self):
        super(TCPGardien, self).arreter()
        
        self.pipe.send("fin")
        self.thread.join()
        self.pipe.close()
    
    # Propriétés
    @property
    def adresse(self):
        return self.thread.adresse

class TCPConnexion:
    # Méthodes spéciales
    def __init__(self, adresse):
        if isinstance(adresse, tuple):
            adresse = AdresseIP(*adresse, check=False)
        
        if not adresse.valide:
            raise AdresseInvalideErreur()
        
        self._adresse  = ThreadSafeWrapper(adresse)
        self._connecte = ThreadSafeWrapper(False)
    
    def __enter__(self):
        self.connecter()
    
    def __exit__(self, t,v,b):
        self.deconnecter()
    
    # Méthodes
    def connecter(self):
        with self._connecte:
            assert not self._connecte.objet, "Déjà connecté"
            self._connecte.objet = True
        
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(self.adresse.tuple)
    
    def envoyer(self, requete):
        assert self._connecte.objet, "Pas connecté"
        self._socket.send(requete)
    
    def recevoir(self, buffer=1024):
        assert self._connecte.objet, "Pas connecté"
        return self._socket.recv(buffer)
        
    def deconnecter(self):
        with self._connecte:
            assert self._connecte.objet, "Pas connecté"
            self._connecte.objet = False
        
        self._socket.send(b"fin connexion")
        
        rq = b""
        while rq != b"ok":
            rq = self._socket.recv(1024)
        
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()
    
    # Propriétés
    @property
    def adresse(self):
        return self._adresse.objet
    
    @adresse.setter
    def adresse(self, addr):
        assert not self.connecte, "Impossible si connecté"
        
        with self._adresse:
            self._adresse.objet = addr
    
    @property
    def connecte(self):
        return self._connecte.objet
