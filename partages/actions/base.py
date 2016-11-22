# Importations
from log.mixin import ThreadLogMixin

import abc
import threading as th
import traceback
import sys

# Metaclasses
class MetaAction(abc.ABCMeta):
    # Attributs
    __registre_classes__ = {}
    
    # Méthodes
    def __new__(metacls, nom, bases, attrs):
        cls = super(MetaAction, metacls).__new__(metacls, nom, bases, attrs)
        
        metacls.__registre_classes__[attrs.get("nom", nom.lower())] = cls
        
        return cls

# Classes
class BaseAction(ThreadLogMixin, metaclass=MetaAction):
    # Attributs
    nom_log = "upnp.partages"
    
    # Méthodes spéciales
    def __init__(self, args, stdout=sys.stdout, bytes=False):
        self.args   = args
        self.lock   = th.RLock()
        self.stdout = stdout
        self.bytes  = bytes
    
    # Méthodes
    def afficher(self, message):
        if self.bytes:
            with self.lock:
                self.stdout.write(str(message).encode('utf-8') + b"\n")
        
        else:
            with self.lock:
                self.stdout.write(message + "\n")
    
    def lancer(self):
        try:
            return self.executer()
        
        except Exception as err:
            self.handle_erreur(err)
        
        finally:
            self.clean_up()
    
    @abc.abstractmethod
    def executer(self):
        return NotImplemented
    
    def handle_erreur(self, err):
        tb = "".join(traceback.format_exception(*sys.exc_info()))[:-1]
        self.error("Erreur pendant l'execution de l'action {} :\n{}\n".format(self.__class__.__name__, tb))
    
    def clean_up(self):
        if self.stdout != sys.stdout:
            self.stdout.close()

class ThreadingAction(BaseAction):
    # Méthodes spéciales
    def __init__(self, args):
        self._threads = []
        super(ThreadingAction, self).__init__(args)
    
    # Méthodes
    def creer_thread(self, *args, **kwargs):
        t = th.Thread(*args, **kwargs)
        self._threads.append(t)
        return t
   
    def clean_up(self):
        for t in self._threads:
            t.join()
        
        super(ThreadingAction, self).clean_up()
