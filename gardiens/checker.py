# Importations
from .base import BaseGardien
from .utils import identifiant_processus
from .thread import BaseThread

from base.decorateurs import verif_type
from base.mixin import SingletonMixin
from base.wrapper import ThreadSafeWrapper

import multiprocessing as mp
import socket
import threading as th

# Classes
class AdresseIP:
    # Attibuts
    __instances__ = {}
    __pid_instances__ = mp.current_process().pid
    
    # Méthodes spéciales
    def __new__(cls, adresse, port, check=True):
        # Check PID
        if not cls.__pid_instances__ == mp.current_process().pid:
            cls.__pid_instances__ = mp.current_process().pid
            cls.__instances__ = {}
        
        # Check existance
        if (adresse, port) in cls.__instances__:
            return cls.__instances__[(adresse, port)]
        
        # Création
        self = super(AdresseIP, cls).__new__(cls)
        
        cls.__instances__[(adresse, port)] = self
        
        self._lock = th.RLock()
        self._creer = True
        
        return self
    
    def __init__(self, adresse, port, check=True):
        with self._lock:
            if self._creer:
                self._adresse = ThreadSafeWrapper(adresse)
                self._port = ThreadSafeWrapper(port)
                self._erreur = ThreadSafeWrapper(None)
                
                if check:
                    CheckerGardien().ajouter(self)
                
                self._creer = False
    
    def __getnewargs__(self):
        return self._adresse, self._port, CheckerGardien().est_connue(self)
    
    def __repr__(self):
        return "<AdresseIP {}>".format(repr(self.tuple))
    
    # Propriétés
    @property
    def adresse(self):
        return self._adresse.objet
    
    @property
    def port(self):
        return self._port.objet
    
    @port.setter
    def port(self, port):
        with self._port:
            self._port.objet = port
    
    @property
    def tuple(self):
        return (self.adresse, self.port)
    
    @property
    def erreur(self):
        return self._erreur.objet
    
    @erreur.setter
    def erreur(self, err):
        assert self.valide, "Possède déjà une erreur."
        
        with self._erreur:
            self._erreur.objet = err
    
    @property
    def valide(self):
        return self._erreur.objet == None

# Fonction
def check(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect(addr.tuple)
        sock.send(b"check")
        
        mess = b""
        while mess != b"ok":
            mess = sock.recv(1024)
    
    except OSError as err:
        addr.erreur = err
        
        with self.checklist:
            self.checklist.objet.remove(addr)
    
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
    
    return addr.valide

# Classes
class CheckerThread(BaseThread):
    # Méthodes spéciales
    def __init__(self, pipe, attente=10):
        self.pipe = pipe
        self.checklist = ThreadSafeWrapper([])
        self.erreurs = ThreadSafeWrapper({})
        self.attente = attente
        
        super(CheckerThread, self).__init__(name="CheckerThread " + identifiant_processus())
    
    # Méthodes
    def run(self):
        while True:
            try:
                # Phase tests
                for addr in list(self.checklist.objet):
                    if not addr.valide:
                        with self.checklist:
                            self.checklist.objet.remove(addr)
                        
                        continue
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    
                    try:
                        sock.connect(addr.tuple)
                        sock.send(b"check")
                        
                        mess = b""
                        while mess != b"ok":
                            mess = sock.recv(1024)
                    
                        sock.shutdown(socket.SHUT_RDWR)
                    
                    except OSError as err:
                        addr.erreur = err
                        
                        with self.checklist:
                            self.checklist.objet.remove(addr)
                    
                    finally:
                        sock.close()
                    
                    if self.pipe.poll(0.05):
                        if self.pipe.recv() == "fin":
                            self.pipe.close()
                            return
                
                # Phase attente
                if self.pipe.poll(self.attente):
                    if self.pipe.recv() == "fin":
                        self.pipe.close()
                        return
        
            except Exception as err:
                self.error("checker erreur : {!r}".format(err))

class CheckerGardien(BaseGardien, SingletonMixin):
    # Méthodes spéciales
    def __init__(self, attente=20):
        if self._creer:
            super(CheckerGardien, self).__init__()
            
            self._pipe, pipe = mp.Pipe()
            self._thread = CheckerThread(pipe, attente)
            self._creer = False
    
    # Méthodes
    def lancer(self):
        super(CheckerGardien, self).lancer()
        self._thread.start()
    
    @verif_type(adresse_ip=AdresseIP)
    def ajouter(self, adresse_ip):
        with self._thread.checklist:
            self._thread.checklist.objet.append(adresse_ip)
    
    @verif_type(adresse_ip=AdresseIP)
    def est_connue(self, adresse_ip):
        return adresse_ip in self._thread.checklist.objet
    
    @verif_type(adresse_ip=AdresseIP)
    def supprimer(self, adresse_ip):
        with self._thread.checklist:
            self._thread.checklist.objet.remove(adresse_ip)
    
    def arreter(self):
        super(CheckerGardien, self).arreter()
        self._pipe.send("fin")
        self._pipe.close()
        self._thread.join()
