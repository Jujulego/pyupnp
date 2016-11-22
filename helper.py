# Importations
from base.decorateurs import singleton
from base.objets import Namespace
from pystock import Stock
import settings

# Classe
@singleton
class Helper(Namespace):
    # Méthodes spéciales
    def __init__(self):
        self.__dict__.update({n: v for n, v in settings.__dict__.items() if n.isupper()})
    
    def __repr__(self):
        return "<Settings>"
    
    # Méthodes
    def recup_setting(self, nom, defaut=None):
        nom = nom.upper()
        
        return getattr(self, nom, defaut)
    
    # Propriétés
    @property
    def stock(self):
        return Stock(self.DOSSIER_RACINE)[self.RESEAU]
