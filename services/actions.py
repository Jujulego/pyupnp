# Importations
from . import variables
from .variables.base import BaseVariable

from base.decorateurs import verif_type

# Classe
class Argument:
    # Méthodes spéciales
    @verif_type(nom=str, varLiee=BaseVariable)
    def __init__(self, nom, varLiee, direction):
        self.nom        = nom
        self._direction = direction
        self.varLiee    = varLiee
        self._valeur    = varLiee.valeur
    
    def __repr__(self):
        return "<Argument {} lié à {!r}>".format(self.nom, self.varLiee)
    
    # Propriétés
    @property
    def valeur(self):
        return self._valeur
    
    @valeur.setter
    def valeur(self, val):
        self._valeur = self.varLiee._pythoniser(val)
    
    @property
    def direction(self):
        return self._direction
    
    @property
    def xml(self):
        return self.varLiee._xmliser(val)

class Action:
    # Méthodes spéciales
    def __init__(self, nom, arguments, standard):
        self.nom       = nom
        self.arguments = arguments
        self.standard  = standard
    
    def __repr__(self):
        return "<Action {}>".format(self.nom)
