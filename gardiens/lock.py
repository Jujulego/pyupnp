# Importations
from .exceptions import PasDeReponse
from .gardien import Gardien
from .utils import identifiant_processus
from .thread import PreparationThread

from base.wrapper import ThreadSafeWrapper

from datetime import datetime
import hashlib
import multiprocessing as mp
import threading as th
from time import time

# Classes
class RLock:
    # Attributs
    __instances__ = ThreadSafeWrapper({})
    __pid_instances__ = None
    
    # Méthodes spéciales
    def __new__(cls, identifiant=None):
        if not identifiant:
            identifiant = hashlib.md5(("{}{}".format(identifiant_processus(), time())).encode("utf-8")).hexdigest()
        
        if cls.__pid_instances__ == None:
            cls.__pid_instances__ = mp.current_process().pid
        
        elif cls.__pid_instances__ != mp.current_process().pid:
            cls.__pid_instances__ = mp.current_process().pid
            cls.__instances__ = ThreadSafeWrapper({})
        
        if identifiant in cls.__instances__.objet:
            return cls.__instances__.objet[identifiant]
        
        self = super(RLock, cls).__new__(cls)
        self.identifiant = identifiant
        self._creer = True
        
        with cls.__instances__:
            cls.__instances__.objet[identifiant] = self
        
        return self
    
    def __init__(self, identifiant=None):
        if not self._creer:
            return
        
        self._lock = ThreadSafeWrapper(None, mp.RLock())
        
        if self.gardien.status == "initial":
            self.gardien.lancer()
        
        self._pret = th.Event()
        
        if not self.gardien.connait(self.identifiant):
            self._thread = PreparationThread(target=self._elir)
            self._thread.start()
        
        else:
            self._pret.set()
        
        self._creer = False
    
    def __del__(self):
        with self.__instances__:
            del self.__instances__.objet[self.identifiant]
    
    def __repr__(self):
        return "<RLock {}>".format(self.identifiant)
    
    def __eq__(self, obj):
        if isinstance(obj, RLock):
            return self.identifiant == obj.identifiant
        
        else:
            return False
    
    def __ne__(self, obj):
        self._wait_pret()
        
        if isinstance(obj, RLock):
            return self.identifiant != obj.identifiant
        
        else:
            return True
    
    def __enter__(self):
        while not self.acquire():
            pass
    
    def __exit__(self, t,v,b):
        self.release()
    
    # Méthodes privées
    def _elir(self):
        while True:
            try:
                self.gardien.election(self.identifiant)
                break
            
            except PasDeReponse:
                pass
        
        self._pret.set()
    
    def _wait_pret(self):
        self._pret.wait()
        
        try:
            self._thread.join()
            del self._thread
        
        except AttributeError:
            pass
    
    # Méthodes
    def acquire(self, block=True, timeout=0):
        self._wait_pret()
        
        if timeout == None:
            timeout = 0
        
        while not self._lock.prendre():
            pass
        
        with self._lock:
            self._lock.objet = th.get_ident()
        
        if not self.gardien.connait(self.identifiant):
            self.gardien.election(self.identifiant)
        
        datedeb = datetime.now()
        
        while True:
            try:
                retour = self.gardien.bloquer(self.identifiant)
            
            except Exception as err:
                retour = False
            
            if retour or not block:
                break
            
            elif timeout == 0:
                continue
            
            elif (datetime.now() - datedeb).total_seconds() > timeout:
                break
        
        if not retour:
            if self.identifiant in self.gardien.possession:
                with self._lock:
                    self._lock.objet = None
            
            self._lock.lacher()
        
        return retour
    
    def release(self):
        self._wait_pret()
        
        if not self.est_proprietaire():
            return False
        
        if not self.gardien.connait(self.identifiant):
            self.gardien.election(self.identifiant)
        
        retour = self.gardien.debloquer(self.identifiant)
        
        if retour:
            if not self.identifiant in self.gardien.possession:
                with self._lock:
                    self._lock.objet = None
            
            self._lock.lacher()
        
        return retour
    
    def est_bloque(self):
        self._wait_pret()
        
        return self.gardien.est_bloque(self.identifiant)
    
    def est_proprietaire(self):
        self._wait_pret()
        
        return self._lock.objet == th.get_ident()
    
    # Propriétés
    @property
    def gardien(self):
        return Gardien()
