# Importation
from base.decorateurs import verif_type
from base.utils import joinext
from base.wrapper import ThreadSafeWrapper
from gardiens import RLock

import abc
import hashlib
import os
from os import path
import multiprocessing as mp

# Classe
class Base(metaclass=abc.ABCMeta):
    # Attributs spéciaux
    __registre__  = ThreadSafeWrapper({})         # Registre des instances
    __pid_registre__ = None                       # Pour détecter les copies lors des passages entres processus
    __registre_classes__ = ThreadSafeWrapper({    # Registre des classes, permet de choisir la bonne classe pour le bon fichier
        "fichiers": {},
        "dossiers": {},
    })
    
    # Attributs
    auto_creation = True    # Si True, __init__ crée le fichier s'il n'existe pas
    
    # Méthodes spéciales
    def __new__(cls, chemin, *args, **kwargs):
        chemin = path.abspath(chemin)
        
        if cls.__pid_registre__ == None:
            cls.__pid_registre__ = mp.current_process().pid
        
        elif cls.__pid_registre__ != mp.current_process().pid:
            cls.__pid_registre__ = mp.current_process().pid
            cls.__registre__ = ThreadSafeWrapper({})
	
        if not chemin in cls.__registre__.objet:
            instance = super(Base, cls).__new__(cls)
            instance._initier = True
            
            with cls.__registre__:
                cls.__registre__.objet[chemin] = instance
        
        return cls.__registre__.objet[chemin]
    
    @verif_type(chemin=str)
    def __init__(self, chemin, *args, **kwargs):
        chemin = path.abspath(chemin)
        
        if self._initier:
            if hasattr(self, "extension"):
                if self.extension != '*':
                    chemin = joinext(chemin, self.extension)
            
            self._lock_contenu = RLock(hashlib.md5("{}:{}".format(os.uname()[1], chemin).encode("utf-8")).hexdigest())
            self._chemin       = ThreadSafeWrapper(chemin)
            self._lock_fichier = ThreadSafeWrapper(path.exists, self._lock_parent)
            self._creation     = False
            self._suppression  = False
            
            if not path.exists(self.chemin) and self.auto_creation:
                self.creer(*args, **kwargs)
            
            self._initier = False
            self._parametrer()
    
    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.chemin)
    
    def __eq__(self, obj):
        if isinstance(obj, Base):
            return self._lock_contenu == obj._lock_contenu
        
        return False
    
    def __ne__(self, obj):
        if isinstance(obj, Base):
            return self._lock_contenu != obj._lock_contenu
        
        return True
    
    # Méthodes de classe
    @classmethod
    @abc.abstractmethod
    def _enregistrer_classe(cls, classe):
        return NotImplemented
    
    @classmethod
    def _recuperer_classe(cls, chemin):
        if not path.exists(chemin):
            raise FileNotFoundError("Le fichier n'existe pas")
        
        if path.isdir(chemin):
            params = path.join(chemin, "__params__.pystock")
            
            if path.exists(params):
                with open(params, "r") as f:
                    iddos = f.read().strip()
            
            else:
                iddos = "Dossier"
            
            if iddos not in cls.__registre_classes__.objet["dossiers"]:
                iddos = "Dossier"
            
            return cls.__registre_classes__.objet["dossiers"][iddos]
        
        elif path.isfile(chemin):
            extension = path.splitext(chemin)[1] or '*'
            
            if extension not in cls.__registre_classes__.objet["fichiers"]:
                extension = '*'
            
            return cls.__registre_classes__.objet["fichiers"][extension]
        
        else:
            raise TypeError("Le fichier n'est pas géré")
    
    # Méthodes privées
    @abc.abstractmethod
    def _creer(self, chemin):
        return NotImplemented
    
    @abc.abstractmethod
    def _supprimer(self, chemin):
        return NotImplemented
    
    def _parametrer(self):
        pass
    
    def _lock_parent(self):
        try:
            chemin = path.dirname(self.chemin)
            return self._recuperer_classe(chemin)(chemin)._lock_contenu
        
        except OSError:
            return self._lock_contenu
        
        except TypeError:
            return self._lock_contenu

    # Méthodes
    def creer(self, *args, **kwargs):
        chemin = self.chemin
        
        with self._lock_fichier:
            if self.existe:
                raise FileExistsError("Le fichier existe déjà")
            
            self._creation = True
            self._creer(chemin, *args, **kwargs)
            self._creation = False
    
    @verif_type(nouveau_chemin=str)
    def deplacer(self, nouveau_chemin, ecrase=False):
        if path.exists(nouveau_chemin) and not ecrase:
            raise FileExistsError("Le nouveau chemin est déjà utilisé")
        
        chemin = self.chemin
        
        with self._chemin:
            self._chemin.objet = nouveau_chemin
        
        if not self.existe:
            with self._lock_fichier:
                os.replace(chemin, nouveau_chemin)
    
    def supprimer(self):
        chemin = self.chemin
        
        with self._lock_fichier:
            if not self.existe:
                raise FileNotFoundError("Le fichier n'existe pas")
            
            self._supression = True
            self._supprimer(chemin)
            self._suppression = False
    
    # Propriétés
    @property
    def chemin(self):
        return self._chemin.objet
    
    @chemin.setter
    def chemin(self, chemin):
        self.deplacer(path.abspath(chemin))
    
    @property
    def nom(self):
        return path.basename(self.chemin)
    
    @nom.setter
    def nom(self, nom):
        self.deplacer(path.join(path.dirname(self.chemin), nom))
    
    @property
    def existe(self):
        if self._creation:
            return True
        
        elif self._suppression:
            return False
        
        return self._lock_fichier.objet(self.chemin)
    
    @property
    def parent(self):
        if not self.existe:
            raise FileNotFoundError("Le fichier n'existe pas il n'a pas de parent")
        
        try:
            chemin = path.dirname(self.chemin)
            return self._recuperer_classe(chemin)(chemin)
        
        except OSError:
            return None
        
        except TypeError:
            return None
