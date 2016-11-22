# Importations
from base.objets import Namespace
from base.threads.queue_serveur import QueueServeurThread
from helper import Helper
from pystock.mixins import CreationMixin

# Variables
helper = Helper()

# Classe
class ServiceThreadStock(QueueServeurThread, CreationMixin):
    # Attributs
    marque     = "perif"
    nom_log    = "upnp"
    _blacklist = ["creer_stock", "creer_coffre"]
    
    # Méthodes spéciales
    def __init__(self, uuid, modifs, event):
        self.uuid    = uuid
        self.event   = event
        self.etat    = 0
        self.coffres = Namespace()
        self.liste   = []
        
        super(ServiceThreadStock, self).__init__(modifs)
    
    # Méthodes privées
    def _setup(self):
        self.event.wait() # On attend la création du stock
        self.stock = helper.stock["periferiques"][self.uuid]["services"]
        
        self.stock.inscrire()
    
    def _nettoyer(self):
        self.stock.desinscrire()
    
    def _handle_erreur(self, err):
        self.error("Erreur dans ServiceThreadStock : {!r}".format(err))
    
    # Méthodes
    def ajouter(self, infos, etat):
        self.liste.append(infos["infos"]["identifiant"])
        setattr(self.coffres, infos["infos"]["identifiant"], self.creer_coffre(infos["infos"]["identifiant"], infos))
        
        self.etat = etat
    
    def mise_a_jour(self, nom, infos, etat):
        coffre = getattr(self.coffres, nom)
        
        with coffre:
            coffre.contenu.update(infos)
        
        self.etat = etat
    
    # Propriétés
    @property
    def infos(self):
        infos = {}
        
        for n in self.liste:
            infos[n] = getattr(self.coffres, n).contenu
        
        return infos
