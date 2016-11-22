# Importations
from .base import BaseAction
from .mixin import ListeMixin

from periferiques import PeriferiqueDistant

# Classe
class ListeAction(BaseAction, ListeMixin):
    # Attributs
    nom = "liste"
    
    # Méthodes
    def executer(self):
        self.afficher(self.generer_liste(PeriferiqueDistant.liste()))
