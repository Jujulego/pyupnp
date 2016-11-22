# Importations
from .serveur import SSDPServeur
from .handler import SSDPHandler

from gardiens import Gardien
from log.mixin import ThreadLogMixin
from recherches.recherches import Recherches

import multiprocessing as mp
import threading as th

# Classe
class SSDPProcess(mp.Process, ThreadLogMixin):
    # Attributs
    nom_log = "upnp.ssdp"
    
    # Méthodes spéciales
    def __init__(self, barriere):
        self.barriere = barriere
        
        super(SSDPProcess, self).__init__(name="SSDPProcess")
    
    # Méthodes
    def run(self):
        try:
            Gardien().lancer(False)
            self.srv = SSDPServeur(('', 1900), SSDPHandler)
            
            self.barriere.wait()
            self.info("Serveur SSDP démaré ({:d})".format(self.pid))
            self.srv.serve_forever()
        
        except KeyboardInterrupt:
            self.barriere.abort()
        
        except th.BrokenBarrierError:
            pass
        
        except Exception as err:
            self.critical("Erreur dans le lancement du serveur SSDP : {!r}".format(err))
            self.barriere.abort()
        
        finally:
            if hasattr(self.srv, "threads"):
                for t in self.srv.threads:
                    t.join()
            
            for t in th.enumerate():
                if not hasattr(t, "marque"):
                    continue
                
                if t.marque in ("perif", "recher"):
                    t.fini = True
                
                if t.marque == "perif":
                    t.modifs.put(("fini", "", {}))
            
                elif t.marque == "recher":
                    t.actions.put(("fini", "", {}))
            
            self.srv.shutdown()
            self.srv.server_close()
            self.info("Serveur SSDP arrêté")
            self.gardien.arreter(add_texts="SSDP")

class SSDP(ThreadLogMixin):
    # Attributs
    nom_log = "upnp.ssdp"
    
    # Méthodes spéciales
    def __init__(self, barriere):
        self._process = SSDPProcess(barriere)
    
    # Méthodes
    def lancer(self):
        self._process.start()
    
    def arreter(self):
        self._process.join()
    
    # Propriétés
    @property
    def actif(self):
        return self._process.is_alive()
