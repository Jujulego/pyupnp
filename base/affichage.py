"""
Created on 31 juillet 2015

@author: julien
"""

# Importations
from .mixin import SingletonMixin

from threading import RLock
import sys

# Classes
class AffichageWrapper(SingletonMixin):
    # Attributs
    stdout = sys.stdout
    lock = RLock()
    
    # Méthodes spéciales
    def __init__(self):
        sys.stdout = self
    
    def __getattribute__(self, nom):
        if nom not in ("stdout", "lock", "nb", "write", "writelines"):
            return getattr(self.stdout, nom)
        
        return super(AffichageWrapper, self).__getattribute__(nom)
    
    # Méthodes
    def write(self, *args, **kwargs):
        with self.lock:
            return self.stdout.write(*args, **kwargs)
    
    def writelines(self, *args, **kwargs):
        with self.lock:
            return self.stdout.writelines(*args, **kwargs)
