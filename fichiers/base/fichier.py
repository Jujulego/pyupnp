# Importations
from .base import Base
from .exceptions import FileOpenError, FileCloseError

from base.decorateurs import verif_type
from base.utils import joinext
from base.wrapper import ThreadSafeWrapper
from gardiens import RLock

import abc
import hashlib
import multiprocessing as mp
import os
from os import path

# Classe de base
class BaseFichier(Base):
    # Attributs
    extension = '*'
    bytes = False
    
    # Méthodes de classe
    @classmethod
    def _enregistrer_classe(cls, classe):
        with cls.__registre_classes__:
            cls.__registre_classes__.objet["fichiers"][classe.extension] = classe
    
    # Méthodes
    def supprimer(self):
        if self.ouvert:
            raise FileOpenError("Le fichier est ouvert !")
        
        super(BaseFichier, self).supprimer()

# MetaClasse
class MetaFichier(abc.ABCMeta):
    # Méthodes spéciales
    def __new__(metacls, nom, bases, attrs):
        cls = super(MetaFichier, metacls).__new__(metacls, nom, bases, attrs)
        
        BaseFichier._enregistrer_classe(cls)
        
        return cls

# Classe
class Fichier(BaseFichier, metaclass=MetaFichier):
    # Méthodes spéciales
    def __enter__(self):
        if self.ouvert:
            self.ouvrir("r+")
    
    def __exit__(self, t,v,b):
        self.fermer()
    
    # Méthodes privées
    @verif_type(contenu=(str, bytes))
    def _creer(self, chemin, contenu=None):
        if not contenu:
            if self.bytes:
                contenu = b""
            
            else:
                contenu = ""
        
        if self.bytes and isinstance(contenu, str):
            raise TypeError("Le contenu est doit être de type bytes !")
        
        elif not self.bytes and isinstance(contenu, bytes):
            raise TypeError("Le contenu est doit être de type str !")
        
        self._fichier = open(chemin, "w" + ("b" if self.bytes else ""))
        self._fichier.write(contenu)
        self._fichier.close()
    
    def _supprimer(self, chemin):
        os.remove(chemin)
    
    def _parametrer(self):
        self._ouvert = ThreadSafeWrapper(False)
        self._mode = ThreadSafeWrapper("")
    
    def _assertion(self):
        if not self.ouvert:
            raise FileCloseError("Le fichier est fermé")
    
    # Méthodes
    def ouvrir(self, mode="r"):
        if not self.existe:
            raise FileNotFoundError("Le fichier n'existe pas")
        
        if self.ouvert:
            raise FileOpenError("Le fichier est déjà ouvert")
        
        if self.bytes and not "b" in mode:
            mode += "b"
        
        chemin = self.chemin
        
        with self._ouvert:
            self._fichier = open(chemin, mode)
            self._ouvert.objet = True
    
    def open(self, mode="r"):
        return self.ouvrir(mode)
    
    def size(self):
        if not self.existe:
            raise FileNotFoundError("Le fichier n'existe pas")
        
        return os.stat(self.chemin)[8]
    
    def fileno(self):
        self._assertion()
        return self._fichier.fileno()
    
    def flush(self):
        self._assertion()
        return self._fichier.flush()
    
    def tell(self):
        self._assertion()
        return self._fichier.tell()
    
    @verif_type(position=int)
    def seek(self, position):
        self._assertion()
        return self._fichier.seek(position)
       
    def read(self, nb=None):
        self._assertion()
        if not self.lisible:
            raise PermissionError("Le fichier n'est pas ouvert en lecture")
        
        with self._lock_contenu:
            retour = self._fichier.read(nb)
        
        return retour
    
    @verif_type(contenu=(str, bytes))
    def write(self, contenu):
        if self.bytes and not isinstance(contenu, bytes):
            contenu = contenu.encode("utf-8")
        
        elif not self.bytes and not isinstance(contenu, str):
            contenu = contenu.decode("utf-8")
        
        self._assertion()
        if not self.modifiable:
            raise PermissionError("Le fichier n'est pas ouvert en écriture")
        
        with self._lock_contenu:
            retour = self._fichier.write(contenu)
        
        self._fichier.flush()
        
        return retour
    
    def fermer(self):
        if not self.ouvert:
            raise FileCloseError("Le fichier est déjà fermé")
        
        with self._ouvert:
            self._ouvert.objet = False
        
        self._fichier.close()
    
    def close(self):
        return self.fermer()
    
    # Property
    @property
    def nom(self):
        return path.splitext(path.basename(self.chemin))[0]
    
    @nom.setter
    def nom(self, nom):
        self.deplacer(path.join(path.dirname(self.chemin), joinext(nom, self.extension) if self.extension != "*" else nom))
    
    @property
    def ouvert(self):
        return self._ouvert.objet
    
    @property
    def mode(self):
        return self._mode.objet
    
    @property
    def lisible(self):
        if self.ouvert:
            return self._fichier.readable()
        
        return False
    
    def readable(self):
        return self.lisible
    
    @property
    def modifiable(self):
        if self.ouvert:
            return self._fichier.writable()
        
        return False
    
    def writable(self):
        return self.modifiable
