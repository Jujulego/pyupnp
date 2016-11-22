# Importations
from base.threads.queue_serveur import QueueServeurThread
from helper import Helper
from pystock import Stock
from pystock.mixins import CreationMixin

# Variables
helper = Helper()

# Classe
class PerifStockThread(QueueServeurThread, CreationMixin):
    # Attributs
    marque     = "perif"
    _blacklist = ["creer_stock", "creer_coffre"]
    
    # Méthodes spéciales
    def __init__(self, perif, levent, sevent):
        self.perif  = perif
        self.levent = levent
        self.sevent = sevent
        self.etat   = perif.etat -1
        
        super(PerifStockThread, self).__init__(perif.modifs)
    
    # Méthodes privées
    def _setup(self):
        # Récupération du stock et attente de la création du stock
        stock = helper.stock["periferiques"]
        self.levent.wait()
        self.stock = stock[self.perif._uuid]
        
        # Inscription
        self.stock.inscrire()
        
        # Création du contenu
        self.infos = self.creer_coffre("infos", self.perif._infos)
        self.etat += 1
        
        self.services = self.creer_stock("services")
        self.sevent.set()
    
    def _nettoyer(self):
        self.stock.desinscrire()
    
    def _handle_erreur(self, err):
        self.error("Erreur dans PerifStockThread : {!r}".format(err))
    
    # Méthodes
    def mise_a_jour(self, infos, etat):
        with self.infos as c:
            c.update(infos)
        
        self.etat = etat
