# Importations
from chargement import *
from helper import Helper
from protocoles.ssdp.process import SSDP
from partages.process import Partage
from periferiques import Periferiques
from recherches import Recherches

from gardiens import Gardien
from gardiens.thread import PreparationThread

import multiprocessing as mp

# Variables
helper = Helper()

# Classe
class Starter:
    # Méthodes
    def parametrer(self, reseau=helper.RESEAU, gardien_verbose=False, **kwargs):
        arbre    = helper.ARBRE_STOCKAGE
        logging  = helper.LOGGING
        reseau_s = helper.RESEAU
        
        # Changement du reseau
        if reseau != reseau_s:
            arbre["contenu"][reseau] = arbre["contenu"][reseau_s]
            del arbre["contenu"][reseau_s]
            
            helper.ARBRE_STOCKAGE = arbre
            helper.RESEAU = reseau
        
        # Ajustement des logs
        if not gardien_verbose:
            logging["loggers"]["gardien"]["handlers"] = ('null',)
            
            helper.LOGGING = logging
    
    def executer(self):
        g = Gardien()
        g.lancer()
        
        init_logging(helper.LOGGING)         # Chargement du logging
        init_stockage(helper.ARBRE_STOCKAGE) # Chargement du stockage
        
        barriere = mp.Barrier(4)
        
        # Lancement du serveur des périfériques
        periferiques = Periferiques(barriere)
        periferiques.lancer()
        
        # Lancement du serveur des recherches
        recherches = Recherches(barriere)
        recherches.lancer()
        
        # Lancement du serveur SSDP
        ssdp = SSDP(barriere)
        ssdp.lancer()
        
        # Lancement du serveur de Partage
        partage = Partage(g.adresse_tcp, barriere)
        partage.lancer()
        
        if barriere.broken:
            partage.arreter()
            ssdp.arreter()
            recherches.arreter()
            periferiques.arreter()
            return
        
        try:
            while True:
                input()
        
        except KeyboardInterrupt:
            pass
        
        finally:
            partage.arreter()
            ssdp.arreter()
            recherches.arreter()
            periferiques.arreter()
