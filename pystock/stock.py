# Importations
from .exceptions import *
from .utils import thread_identifiant

from base.decorateurs import verif_type
from base.exceptions import VerrouilleErreur, AntiDeadLock
from base.utils import joinext
from fichiers.pymem import FichierPyMem, DossierPyMem

import multiprocessing as mp
from os import path

# Classes
class Stock:
    # Méthodes spéciales
    def __new__(cls, dossier):
        if isinstance(dossier, str):
            return super(Stock, cls).__new__(cls)
        
        if cls == dossier.classe_stock:
            return super(Stock, cls).__new__(cls)
        
        else:
            return dossier.classe_stock(dossier)
    
    @verif_type(dossier=(DossierPyMem, str))
    def __init__(self, dossier):
        if isinstance(dossier, str):
            dossier = DossierPyMem(dossier)
        
        self._dossier = dossier
        self._lock = dossier._lock_contenu
    
    def __repr__(self):
        return "<Stock {}>".format(self.nom)
    
    def __bool__(self):
        return True
    
    def __eq__(self, obj):
        if isinstance(obj, Stock):
            return obj._dossier == self._dossier
        
        return False
    
    def __ne__(self, obj):
        if isinstance(obj, Stock):
            return obj._dossier != self._dossier
        
        return True
    
    def __len__(self):
        return len(self.liste_noms())
    
    def __contains__(self, nom):
        return self.existe(nom)
    
    def __getitem__(self, nom):
        return self.recuperer(nom)
    
    def __enter__(self):
        self.inscrire()
    
    def __exit__(self, t,v,b):
        self.desinscrire()
    
    # Méthodes spéciales
    def _prendre(self, nom):
        if not self.existe(nom):
            raise CoffreIntrouvableErreur("Le coffre '{}' n'existe pas".format(nom))
        
        if nom == "__threads__":
            return
        
        if self.est_pris(nom) and self._dossier.existe_coffre(nom):
            raise VerrouilleErreur("Ce coffre est déjà pris")
        
        if self.est_possesseur():
            if self._recup_nom_possess() != nom:
                raise AntiDeadLock("Ce thread possède déjà un coffre")
        
        with self._threads as c:
            l = c.rechercher(nom=nom)
            
            if len(l) == 0:
                c.ajouter_valeurs(nom=nom, thread=[thread_identifiant()])
            
            else:
                l[0]["thread"].valeur.append(thread_identifiant())
    
    def _lacher(self, nom):
        if not self.existe(nom):
            raise CoffreIntrouvableErreur("Le coffre '{}' n'existe pas".format(nom))
        
        if nom == "__threads__":
            return
        
        with self._threads as c:
            l = c.rechercher(nom=nom)[0]
            l["thread"].valeur.remove(thread_identifiant())
    
    # Méthodes
    # gestion du stock (statut thread)
    def est_racine(self):
        return self._dossier.est_racine()
    
    def est_possesseur(self):
        result = self._threads.contenu.rechercher(thread__contain=thread_identifiant(), nom__ne="__threads__")
        return len(result) > 0
    
    def est_pris(self, nom):
        if not self.existe(nom):
            raise CoffreIntrouvableErreur("Le coffre '{}' n'existe pas".format(nom))
        
        l = self._threads.contenu.rechercher(nom=nom)
        
        if len(l) == 0:
            return False
        
        else:
            return len(l[0]["thread"].valeur) != 0
    
    def _recup_nom_possess(self):
        table = self._threads.contenu
        result = table.rechercher(thread__contain=thread_identifiant(), nom__ne="__threads__")
        assert len(result) > 0, "Ce thread ne possède rien dans ce stock"
        return result[0]["nom"].valeur
    
    @property
    def possession(self):
        return self.recuperer(self._recup_nom_possess())
    
    @property
    def _threads(self):
        return self._dossier.recuperation("__threads__.pymem").coffre
    
    @property
    def nom(self):
        return self._dossier.nom
    
    @property
    def parent(self):
        if self.est_racine():
            return None
        
        else:
            return self._dossier.parent.stock
    
    @property
    def chemin(self):
        if self.est_racine():
            return self.nom
        
        else:
            return path.join(self.parent.chemin, self.nom)
    
    # gestion du stock (statut inscriptions)
    def est_inscrit(self):
        if self.est_racine():
            return True
        
        try:
            return self.parent.possession == self
        
        except AssertionError:
            return False
    
    def inscrire(self, timeout=None):
        if self.est_racine():
            return True
        
        self.parent.inscrire()
        return self.parent._prendre(self.nom)
    
    def desinscrire(self):
        if self.est_racine():
            return True
        
        retour = self.parent._lacher(self.nom)
        self.parent.desinscrire()
        return retour
    
    def ouvrir(self, nom, timeout=None):
        obj = self.recuperer(nom)
        
        if isinstance(obj, Stock):
            obj.inscrire()
        
        else:
            obj.ouvrir()
    
    def fermer(self):
        obj = self.possession
        
        if isinstance(obj, Stock):
            obj.desinscrire()
        
        else:
            obj.fermer()
    
    # gestion coffres/stocks (contenu)
    def existe(self, nom):
        return self._dossier.existe_coffre(nom) or self._dossier.existe_stock(nom)
    
    def liste_noms(self):
        return [o.nom for o in self.coffres + self.stocks]
    
    def ajouter_coffre(self, nom, contenu=None):
        assert self.est_inscrit(), "Ce thread n'est pas inscrit !"
        
        if self.existe(nom):
            raise CoffreExisteErreur("Le coffre '{}' existe déjà".format(nom))
        
        return self._dossier.creer_coffre(nom, contenu=contenu).coffre
    
    def supprimer_coffre(self, nom):
        assert self.est_inscrit(), "Ce thread n'est pas inscrit !"
        
        if not self.existe(nom):
            raise CoffreIntrouvableErreur("Le coffre '{}' n'existe pas".format(nom))
        
        return self._dossier.suppr_coffre(nom)
    
    def ajouter_stock(self, nom):
        assert self.est_inscrit(), "Ce thread n'est pas inscrit !"
        
        if self.existe(nom):
            raise StockExisteErreur("Le stock '{}' existe déjà".format(nom))
        
        return self._dossier.creer_stock(nom).stock
    
    def supprimer_stock(self, nom):
        assert self.est_inscrit(), "Ce thread n'est pas inscrit !"
        
        if not self.existe(nom):
            raise StockIntrouvableErreur("Le stock '{}' existe déjà".format(nom))
        
        return self._dossier.suppr_stock(nom)
    
    def recuperer(self, nom):
        if self._dossier.existe_coffre(nom):
            return self._dossier.recuperation(joinext(nom, FichierPyMem.extension)).coffre
        
        elif self._dossier.existe_stock(nom):
            try:
                return self._dossier.recuperation(nom).stock
            
            except AttributeError as err:
                err.args = (err.args[0] + " " + repr(self._dossier.recuperation(nom)),)
        
        else:
            raise CoffreIntrouvableErreur("Ce nom n'est pas pris")
    
    @property
    def coffres(self):
        fics = self._dossier.fichiers
        coffres = []
        
        for f in fics:
            if isinstance(f, FichierPyMem) and f.nom != "__threads__":
                coffres.append(f.coffre)
        
        return coffres
    
    @property
    def stocks(self):
        doss = self._dossier.dossiers
        stocks = []
        
        for d in doss:
            if isinstance(d, DossierPyMem):
                 stocks.append(d.stock)
        
        return stocks
