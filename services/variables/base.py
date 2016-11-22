# Importations
from .exceptions import ValeurIllegale
from .utils import modulo

from base.utils import verif_type
from base.decorateurs import verif_type as dec_verif_type

import abc
import re

# Metaclasse
class MetaVariable(abc.ABCMeta):
    # Attributs
    _types = {}
    
    # Méthodes spéciales
    def __new__(metacls, nom, bases, attrs):
        cls = super(MetaVariable, metacls).__new__(metacls, nom, bases, attrs)
        
        if "identifiant" in attrs:
            metacls._types[attrs["identifiant"]] = cls
        
        return cls
    
    # Méthodes
    def recup_type(cls, identifiant):
        return cls._types[identifiant]

# Classes
class BaseVariable(metaclass=MetaVariable):
    # Attributs
    python_type = None
    identifiant = None
    defaut      = None
    regex       = None
    flags       = 0
    base_format = None
    
    # Méthodes spéciales
    @dec_verif_type(nom=str, events=bool)
    def __init__(self, nom, events, defaut=None):
        verif_type(defaut, "defaut", self.python_type, type(None))
        
        self.nom    = nom
        self.events = events
        
        if defaut != None:
            self.defaut = defaut
            self._check_valeur(self.defaut)
    
    def __repr__(self):
        return "<{} {}={!r}>".format(self.__class__.__name__, self.nom, self.valeur)
    
    # Méthodes privées
    @classmethod
    def _pythoniser(cls, valeur):
        if not re.match(cls.regex, valeur, cls.flags):
            raise ValeurIllegale("Mauvais format")
        
        return cls.python_type(valeur)
    
    def _xmliser(self):
        return self.base_format.format(self.valeur)
    
    @abc.abstractmethod
    def _check_valeur(self, valeur):
        pass
    
    # Propriétés
    @property
    def xml(self):
        return self._xmliser()
    
    @xml.setter
    def xml(self, val):
        verif_type(val, 'valeur', str)
        val = self._pythoniser(val)
        self._check_valeur(val)
        self._valeur = val
    
    @property
    def valeur(self):
        if hasattr(self, "_valeur"):
            return self._valeur
        
        return self.defaut
    
    @valeur.setter
    def valeur(self, val):
        verif_type(val, 'valeur', self.python_type)
        self._check_valeur(val)
        self._valeur = val

# Fonctions
def recup_type(identifiant):
    return BaseVariable.recup_type(identifiant)

def creer_var_xml(nom, type, defaut=None, max=None, min=None, step=None, liste=None):
    # Récupération de la classe
    cls = recup_type(type)
    
    # Transformation des valeurs
    if defaut != None:
        defaut = cls._pythoniser(defaut)
    
    if max != None:
        max = cls._pythoniser(max)
    
    if min != None:
        min = cls._pythoniser(min)
    
    if step != None:
        step = cls._pythoniser(step)
    
    if liste != None:
        nliste = []
        
        for v in liste:
            nliste.append(cls._pythoniser(v))
        
        liste = nliste
