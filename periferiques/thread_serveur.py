# Importations
from .handler import PerifHandler
from .perif_distant import PeriferiqueDistant
from .serveur import PerifServeur
from .thread_liste import PerifListeThread

from base.threads.chargement import AnimationChargement, PourcentageChargement
from helper import Helper
from log.mixin import ThreadLogMixin

from queue import Queue
import threading as th

# Variables
helper = Helper()

# Classe
class PerifServeurThread(ThreadLogMixin, th.Thread):
    # Attributs
    nom_log = "upnp.periferiques"
    
    # Méthodes spéciales
    def __init__(self, barriere, chg_event):
        self.barriere = barriere
        self.chg_event = chg_event
        
        super(PerifServeurThread, self).__init__()
    
    # Méthodes
    def run(self):
        try:
            self.serveur = PerifServeur(('localhost', helper.PORT_PERIFERIQUES), PerifHandler)
            
            self.serveur.liste = PerifListeThread(Queue(), self.serveur.events)
            self.serveur.liste.start()
            
            while self.chg_event.is_set() and not self.barriere.broken:
                self.serveur.handle_request()
            
            self.barriere.wait()
            self.serveur.serve_forever()
        
        except th.BrokenBarrierError:
            pass
        
        except OSError as err:
            if err.errno != 98:
                self.critical("Erreur lors du démarrage du serveur de périferiques : {!r}".format(err))
            
            else:
                self.critical("Adresse localhost:{:d} occupée !".format(helper.PORT_PERIFERIQUES))
            
            self.barriere.abort()
        
        except KeyboardInterrupt:
            self.barriere.abort()
        
        except Exception as err:
            self.critical("Erreur lors du démarrage du serveur de périferiques : {!r}".format(err))
            self.barriere.abort()
        
        finally:
            self.arreter()
    
    def arreter(self):
        if hasattr(self, "serveur"):
            self.serveur.shutdown()
            self.serveur.server_close()
        
        tp  = PourcentageChargement("Arrêt de la gestion des périfériques")
        ths = [t for t in th.enumerate() if getattr(t, "marque", None) == "perif"]
        
        tp.start()
        i = 0
        
        for t in ths:
            t.arreter()
            
            i += 1
            tp.etat = i/len(ths)
        
        tp.arreter()

class Periferiques(ThreadLogMixin):
    # Atrributs
    nom_log = "upnp.periferiques"
    
    # Méthodes spéciales
    def __init__(self, barriere):
        self._chg_event = th.Event()
        self._chg_event.set()
        self._thread = PerifServeurThread(barriere, self._chg_event)
    
    # Méthodes
    def lancer(self):
        self._thread.start()
        self.info("Gestion des périfériques lancée")
        
        ta = AnimationChargement("Chargement des données")
        ta.start()
        
        liste = [(l["id"].valeur, l["uuid"].valeur) for l in helper.stock["periferiques"]["liste"].contenu.lignes()]
        liste.sort()
        
        for id_p, uuid in liste:
            PeriferiqueDistant(uuid)
        
        self._chg_event.clear()
        ta.arreter()
    
    def arreter(self):
        self._thread.arreter()
        self._thread.join()
        self.info("Gestion des périfériques arrêtée")
