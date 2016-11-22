# Importations
from .stock import Stock
from .coffre import Coffre

from base.utils import joinext
from fichiers.pymem import FichierPyMem

from os import path
import threading as th

# Classe
class Structure:
    """
    Crée une structure de stockage, décrite dans un 'dict'
    
    Syntaxe:
    Structure({
        "racine": chemin jusqu'au dossier racine,
        
        "contenu": {
            nom stock: {
                "type": "stock",
                "contenu": {
                    ... (contenu (stock/coffre) du stock, ajouté en fonction du contenu)
                },
            },
            
            nom coffre: {
                "type": "coffre",
                "contenu": objet contenu (mis seulement si le coffre est créé)
            },
        },
    })
    """
    
    # Méthodes spéciales
    def __init__(self, structure, racine=None, nom=None):
        self._racine = racine
        self._structure = structure
        
        if racine != None:
            if nom == None:
                raise ValueError("Le nom doit être défini, si cette structure n'est pas racine")
            
            self._nom = nom
        
        else:
            self._nom = path.basename(structure["racine"])
            self._chemin = path.abspath(structure["racine"])
        
        self._preparation()
    
    # Méthodes privées
    def _preparation(self):
        self._structs = []
        self._coffres = {}
        
        for nom, obj in self.structure["contenu"].items():
            if obj["type"] == "stock":
                obj["contenu"] = obj.get("contenu", {})
                self._structs.append(Structure(obj, self, nom))
            
            else:
                self._coffres[nom] = obj
                self._coffres[nom]["contenu"] = obj.get("contenu", None)
    
    # Méthodes
    def creer(self):
        if self.racine == None:
            self.stock = Stock(self.chemin)
        
        else:
            parent = self.racine.stock
            
            if parent.existe(self.nom):
                self.stock = parent.recuperer(self.nom)
                
                if not isinstance(self.stock, Stock):
                    raise ValueError("{} n'est pas un stock !".format(self.chemin))
            
            else:
                with parent:
                    self.stock = parent.ajouter_stock(self.nom)
        
        with self.stock:
            for nom, obj in self._coffres.items():
                parent = self.stock
                
                if parent.existe(nom):
                    coffre = parent.recuperer(nom)
                    
                    if not isinstance(coffre, Coffre):
                        raise ValueError("{} n'est pas un coffre !".format(path.join(self.chemin, joinext(nom, FichierPyMem.extension))))
                
                else:
                    parent.ajouter_coffre(nom, obj["contenu"])
        
        threads = []
        
        for struct in self._structs:
            t = th.Thread(target=struct.creer)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
    
    # Propriétés
    @property
    def racine(self):
        return self._racine
    
    @property
    def nom(self):
        return self._nom
    
    @property
    def chemin(self):
        if self.racine == None:
            return self._chemin
        
        return path.join(self.racine.chemin, self.nom)
    
    @property
    def structure(self):
        return self._structure
