# Importations
from base.threads.chargement import ChargementThread

# Fonctions
def init_stockage(arbre):
    from pystock import Structure
    
    ct = ChargementThread(Structure(arbre).creer, "Initialisation du système de stockage")
    ct.charger()

def init_logging(dictio):
    import logging
    from logging.config import dictConfig
    
    def fonc():
        logging.basicConfig(level=logging.DEBUG)
        return dictConfig(dictio)
    
    ct = ChargementThread(fonc, "Initialisation du système de journalisation")
    ct.charger()
