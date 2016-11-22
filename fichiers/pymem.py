# Importations
from .base import Fichier, Dossier, Racine
from .base.fichier import MetaFichier

from base.table import Table
from base.utils import joinext

import pickle

# Classes
class FichierPyMem(Fichier):
    # Attributs
    bytes = True
    extension = ".pymem"
    classe_coffre = None
    
    # Méthodes
    def __new__(cls, *args, **kwargs):
        if cls.classe_coffre == None:
            from pystock import Coffre
            cls.classe_coffre = Coffre
        
        return super(FichierPyMem, cls).__new__(cls, *args, **kwargs)
    
    def __init__(self, *args, **kwargs):
        self._coffre = None
        
        super(FichierPyMem, self).__init__(*args, **kwargs)
    
    def creer(self, contenu=None):
        return super(FichierPyMem, self).creer(contenu=pickle.dumps(contenu))
    
    def recuperer_objet(self):
        with self._lock_contenu:
            self.seek(0)
            return pickle.loads(self.read().strip())
    
    def enregistrer_objet(self, objet):
        with self._lock_contenu:
            self.seek(0)
            self.write(pickle.dumps(objet))
            self.flush()
    
    # Propriétés
    @property
    def coffre(self):
        if self._coffre == None:
            self._coffre = self.classe_coffre(self)
        
        return self._coffre

class DossierPyMem(Dossier):
    # Attributs
    classe_stock = None
    
    # Méthodes
    def __new__(cls, *args, **kwargs):
        if cls.classe_stock == None:
            from pystock import Stock
            cls.classe_stock = Stock
        
        return super(DossierPyMem, cls).__new__(cls, *args, **kwargs)
    
    def __init__(self, *args, **kwargs):
        self._stock = None
        
        super(DossierPyMem, self).__init__(*args, **kwargs)
    
    # Méthodes privées
    def _parametrer(self):
        Dossier._parametrer(self)
        
        if not self.existe_coffre("__threads__"):
            table = Table()
            table.ajouter_colonne("nom")
            table.ajouter_colonne("thread")
            
            try:
                self.creer_coffre("__threads__", contenu=table)
            
            except FileExistsError:
                pass
    
    # Méthodes
    def supprimer(self):
        self.suppr_coffre("__threads__")
        super(DossierPyMem, self).supprimer()
    
    def existe_coffre(self, nom):
        return self.existe_fichier(joinext(nom, FichierPyMem.extension))
    
    def creer_coffre(self, nom, *args, **kwargs):
        return self.creer_fichier(nom, *args, classe=FichierPyMem, **kwargs)
    
    def suppr_coffre(self, nom):
        return self.supprimer_fichier(joinext(nom, FichierPyMem.extension))
    
    def existe_stock(self, nom):
        return self.existe_fichier(nom)
    
    def creer_stock(self, nom, *args, **kwargs):
        return self.creer_dossier(nom, *args, classe=DossierPyMem, **kwargs)
    
    def suppr_stock(self, nom):
        return self.supprimer_fichier(nom)
    
    def est_racine(self):
        return not isinstance(self.parent, DossierPyMem)
    
    # Propriétés
    @property
    def stock(self):
        if self._stock == None:
            self._stock = self.classe_stock(self)
        
        return self._stock
