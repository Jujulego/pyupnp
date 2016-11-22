# Importations
from .handler import RecherchesHandler
from .serveur import RecherchesServeur

from helper import Helper
from log.mixin import ThreadLogMixin

import threading as th

# Variables
helper = Helper()

# Classes
class RecherchesThread(th.Thread, ThreadLogMixin):
    # Attributs
    nom_log = "upnp.recherches"
    
    # Méthodes spéciales
    def __init__(self, barriere):
        self.barriere = barriere
        
        super(RecherchesThread, self).__init__(name="RecherchesThread")
    
    # Méthodes
    def run(self):
        try:
            self.serveur = RecherchesServeur(('localhost', helper.PORT_RECHERCHES), RecherchesHandler)
            
            self.barriere.wait()
            self.info("Gestion des recherches lancée")
            self.serveur.serve_forever()
        
        except th.BrokenBarrierError:
            pass
        
        except OSError as err:
            if err.errno != 98:
                self.critical("Erreur dans le lancement du serveur de recherches : {!r}".format(err))
            
            else:
                self.critical("Adresse localhost:{:d} occupée !".format(helper.PORT_RECHERCHES))
            
            self.barriere.abort()
        
        except Exception as err:
            self.critical("Erreur dans le lancement du serveur de recherches : {!r}".format(err))
            self.barriere.abort()
        
        finally:
            self.arreter()
    
    def arreter(self):
        if hasattr(self, "serveur"):
            self.serveur.shutdown()
            self.serveur.server_close()
            self.info("Gestion des recherches arrêtée")
