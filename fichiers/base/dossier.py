# Importations
from .base import Base

from base.wrapper import ThreadSafeWrapper
from gardiens import RLock

import abc
import glob
import hashlib
import os
from os import path
import threading as th

# Classe de base
class BaseDossier(Base):
    """
    Implémente un registre de classes permettant de mettre la bonne classe sur le bon fichier, dynamiquement.
    """
    
    # Méthodes de classe
    @classmethod
    def _enregistrer_classe(cls, classe):
        with cls.__registre_classes__:
            cls.__registre_classes__.objet["dossiers"][classe.identifiant] = classe
    
    # Méthodes
    def _parametrer(self):
        """
        Crée le fichier __params__.pystock
        """
        
        return NotImplemented

# MetaClasse
class MetaDossier(abc.ABCMeta):
    """
    Enregistre dynamiquement les classes dossiers dans le registre de BaseDossier
    """
    
    # Méthodes spéciales
    def __new__(metacls, nom, bases, attrs):
        cls = super(MetaDossier, metacls).__new__(metacls, nom, bases, attrs)
        cls.identifiant = attrs.get("identifiant") or nom
        
        BaseDossier._enregistrer_classe(cls)
        
        return cls

# Classe
class Dossier(BaseDossier, metaclass=MetaDossier):
    """
    Implémente la gestion d'un dossier.
    """
    
    # Méthodes privées
    def _creer(self, chemin):
        os.makedirs(chemin)
    
    def _supprimer(self, chemin):
        os.rmdir(chemin)
    
    def _parametrer(self):
        self._accessible = th.Event()
        self._accessible.set()
        
        if self.existe_fichier("__params__.pystock"):
            return
        
        if self.existe_fichier("__params__.pystock"):
            return
        
        with self._lock_contenu:
            if not self.existe_fichier("__params__.pystock"):
                with open(self._chemin_absolu("__params__.pystock"), "w") as f:
                    f.write(self.identifiant)
    
    def _assertion(self):
        if not self.existe:
            raise FileNotFoundError("Le dossier n'existe pas")
        
        if not self.accessible and self._lock_contenu.bloque:
            raise PermissionError("Le dossier n'est pas accessible")
    
    def _liste(self):
        self._assertion()
        return os.listdir(self.chemin)
    
    def _chemin_absolu(self, nom):
        return path.join(self.chemin, nom)
    
    # Méthodes
    def supprimer(self):
        self.supprimer_fichier("__params__.pystock")
        super(Dossier, self).supprimer()
    
    def liste_noms(self):
        noms = self._liste()
        fichiers = []
        dossiers = []
        
        for n in noms:
            if path.isfile(self._chemin_absolu(n)):
                fichiers.append(n)
            
            elif path.isdir(self._chemin_absolu(n)):
                dossiers.append(n)
        
        return dossiers, fichiers
    
    def existe_fichier(self, nom):
        self._assertion()
        return path.exists(self._chemin_absolu(nom))
    
    def creer_fichier(self, nom, *args, classe=None, **kwargs):
        self._assertion()
        classe = classe or self.__registre_classes__.objet["fichiers"].get(path.splitext(nom)[1], self.__registre_classes__.objet["fichiers"]["*"])
        
        if self.existe_fichier(nom):
            raise FileExistsError("Ce nom est déjà pris")
        
        return classe(self._chemin_absolu(nom), *args, **kwargs)
    
    def creer_dossier(self, nom, *args, classe=None, **kwargs):
        self._assertion()
        
        if self.existe_fichier(nom):
            raise FileExistsError("Ce nom est déjà pris")
        
        classe = classe or Dossier
        return classe(self._chemin_absolu(nom), *args, **kwargs)
    
    def rechercher(self, nom):
        self._assertion()
        return [self._recuperer_classe(c)(c) for c in glob.glob(self._chemin_absolu(nom))]
    
    def recuperation(self, nom):
        chemin = self._chemin_absolu(nom)
        return self._recuperer_classe(chemin)(chemin)
    
    def supprimer_fichier(self, nom):
        self._assertion()
        
        with self._lock_contenu:
            if not self.existe_fichier(nom):
                raise FileNotFoundError("Le fichier n'existe pas")
            
            return self.recuperation(nom).supprimer()
    
    # Propriété
    @property
    def accessible(self):
        if self.existe:
            return self._accessible.is_set()
        
        return False
    
    @property
    def dossiers(self):
        dossiers, _ = self.liste_noms()
        dossobjs = []
        
        for d in dossiers:
            try:
                dossobjs.append(self.recuperation(d))
            
            except:
                pass
        
        return dossobjs
    
    @property
    def fichiers(self):
        _, fichiers = self.liste_noms()
        ficobjs = []
        
        for f in fichiers:
            try:
                ficobjs.append(self.recuperation(f))
            
            except:
                pass
       
        return ficobjs

class Racine(Dossier):
    # Propriétés
    @property
    def parent(self):
        return None
