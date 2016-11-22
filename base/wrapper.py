# Importations
from base.exceptions import VerrouilleErreur

from copy import copy
import threading as th
import multiprocessing as mp

# Wrappers
class ThreadSafeWrapper:
    """
    ThreadSafeWrapper : protège un objet quelconque contre les accès multithread
    
    version 2.0:
      Utilisiation d'un objet threading.Condition pour supprimer les boucles 'crammeuses de CPU'
    """
    
    # Méthodes spéciales
    def __init__(self, objet, lock=None):
        self._lock_obj = lock or th.RLock()
        self._objet    = objet
        self._cond     = th.Condition()
        self._thread   = None
        self._nb       = 0
    
    def __repr__(self):
        return "<ThreadSafeWrapper {!r}>".format(self.objet)
    
    def __enter__(self):
        self.prendre()
    
    def __exit__(self, t,v,b):
        self.lacher()
    
    # Méthodes
    def prendre(self):
        retour = False
        
        with self._cond:
            while True:
                if not self.est_pris():
                    self._thread = th.get_ident()
                    self._nb    += 1
                    retour = True
                    break
                
                else:
                    if self.est_proprietaire():
                        retour = True
                        self._nb    += 1
                        break
                    
                    else:
                        self._cond.wait_for(lambda : not self.est_pris())
            
            if retour:
                self._cond.notify(1)
        
        if retour:
            self._lock.acquire()
        
        return retour
    
    def est_pris(self):
        with self._cond:
            return self._thread != None
    
    def est_proprietaire(self):
        with self._cond:
            return self._thread == th.get_ident()
    
    def lacher(self):
        if not self.est_proprietaire():
            return
        
        self._lock.release()
        
        with self._cond:
            self._nb -= 1
            
            if self._nb == 0:
                self._thread = None
            
            self._cond.notify(1)
    
    # Propriétés
    @property
    def _lock(self):
        if callable(self._lock_obj):
            return self._lock_obj()
        
        return self._lock_obj
    
    @property
    def objet(self):
        if self.est_proprietaire():
            return self._objet
        
        else:
            with self._cond:
                self._cond.wait_for(lambda : not self.est_pris())
                obj = copy(self._objet)
                self._cond.notify()
            
            return obj
    
    @objet.setter
    def objet(self, obj):
        if self.est_proprietaire():
            self._objet = obj
        
        else:
            raise VerrouilleErreur("Vous ne possédez pas cette ressource")
    
    @objet.deleter
    def objet(self, obj):
        if self.est_proprietaire():
            self._objet = None
        
        else:
            raise VerrouilleErreur("Vous ne possédez pas cette ressource")
