# Importations
from fichiers.pymem import FichierPyMem, DossierPyMem

from base.decorateurs import verif_type
from base.exceptions import VerrouilleErreur
from fichiers.base.exceptions import FileOpenError

from copy import copy
import threading as th

# Classe
class Coffre:
    # Méthodes spéciales
    def __new__(cls, fichier):
        if isinstance(fichier, str):
            return super(Coffre, cls).__new__(cls)
        
        if cls == fichier.classe_coffre:
            return super(Coffre, cls).__new__(cls)
        
        else:
            return fichier.classe_coffre(fichier)
    
    @verif_type(fichier=(FichierPyMem, str))
    def __init__(self, fichier, contenu=None):
        if isinstance(fichier, str):
            fichier = FichierPyMem(fichier, objet=contenu)
        
        self._fichier = fichier
        self._lock = fichier._lock_contenu
        self._cond = th.Condition()
        
        self._recup = False
    
    def __repr__(self):
        return "<Coffre {}>".format(self.nom)
    
    def __enter__(self):
        
        with self._cond:
            self._cond.wait_for(lambda : not self.ouvert)
            self.ouvrir()
        
        return self.contenu
    
    def __exit__(self, t,v,b):
        self.fermer()
    
    # Méthodes privées
    def _ouvrir_fichier(self):
        try:
            if not self._fichier.ouvert:
                self._fichier.ouvrir('r+')
        
        except FileOpenError:
            pass
        
    # Méthodes
    def ouvrir(self, timeout=None):
        self._ouvrir_fichier()
        
        if self.stock:
            self.stock._prendre(self.nom)
        
        with self._cond:
            self._cond.wait_for(lambda : not self.ouvert)
            self._lock.acquire()
        
        self._fichier._objet = self._fichier.recuperer_objet()
   
    def fermer(self):
        if hasattr(self._fichier, "_objet"):
            self._fichier.enregistrer_objet(self._fichier._objet)
            del self._fichier._objet
        
        if self.stock:
            self.stock._lacher(self.nom)
        
        with self._cond:
            self._lock.release()
            self._cond.notify(1)
    
    # Propriétés
    @property
    def nom(self):
        return self._fichier.nom
    
    @property
    def ouvert(self):
        return self._lock.est_proprietaire()
    
    @property
    def contenu(self):
        self._ouvrir_fichier()
        objet = self._fichier.recuperer_objet()
        
        if self.ouvert:
            return self._fichier._objet
        
        else:
            return copy(objet)
    
    @contenu.setter
    def contenu(self, obj):
        if not self.ouvert:
            raise VerrouilleErreur()
        
        self._ouvrir_fichier()
        self._fichier.enregistrer_objet(obj)
        self._fichier._objet = obj
    
    @contenu.deleter
    def contenu(self):
        if not self.ouvert:
            raise VerrouilleErreur()
        
        self._ouvrir_fichier()
        self._fichier.enregistrer_objet(None)
        self._fichier._objet = None
    
    @property
    def stock(self):
        dos = self._fichier.parent
        
        if isinstance(dos, DossierPyMem):
            return dos.stock
        
        return None

class DateCoffre(Coffre):
    # Méthodes spéciales
    def __init__(self, fichier, contenu):
        if isinstance(fichier, str):
            fichier = "{}_{}".format(fichier, datetime.now().strftime("%H:%M:%S.%f %d %m %Y"))
        
        super(DateCoffre, self).__init__(fichier, contenu)
    
    # Propriétés
    @property
    def date_creation(self):
        return datetime.strptime("%H:%M:%S.%f %d %m %Y", self.nom.split("_")[-1])

class DateFichierPyMem(FichierPyMem):
    classe_coffre = DateCoffre
    extension = "datepymem"
