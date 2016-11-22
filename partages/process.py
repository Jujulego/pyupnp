# Importations
from .serveur import PartageServeur
from .handler import PartageHandler

from settings import PORT_PARTAGE

from gardiens import Gardien
from log.mixin import ThreadLogMixin

import multiprocessing as mp
import threading as th

# Classe
class PartageProcess(mp.Process, ThreadLogMixin):
    # Attributs
    nom_log = "upnp.partages"
    
    # Méthodes spéciales
    def __init__(self, matrix_addr, barriere):
        self.barriere = barriere
        self.matrix_addr = matrix_addr
        super(PartageProcess, self).__init__(name="PartageProcess")
    
    # Méthodes
    def run(self):
        try:
#            Gardien().lancer(False)
            self.srv = PartageServeur(('', PORT_PARTAGE), PartageHandler)
            
            self.barriere.wait()
            self.info("Serveur Partage démaré ({:d})".format(self.pid))
            self.srv.serve_forever()
        
        except KeyboardInterrupt:
            self.barriere.abort()
        
        except th.BrokenBarrierError:
            pass
        
        except OSError as err:
            if err.errno == 98:
                self.critical("Port {:d} occupé !".format(PORT_PARTAGE))
            
            else:
                self.critical("Erreur lors du lancement du serveur de partage : {!r}".format(err))
            
            self.barriere.abort()
        
        except Exception as err:
            self.critical("Erreur lors du lancement du serveur de partage : {!r}".format(err))
            self.barriere.abort()
        
        finally:
            if hasattr(self, "srv"):
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
            
            if hasattr(self, "srv"):
                self.srv.shutdown()
                self.srv.server_close()
            
            self.info("Serveur Partage arrêté")
#            self.gardien.arreter(add_texts="Partage")

class Partage(ThreadLogMixin):
    # Attributs
    nom_log = "upnp.partages"
    
    # Méthodes spéciales
    def __init__(self, matrix_addr, barriere):
        self._process = PartageProcess(matrix_addr, barriere)
    
    # Méthodes
    def lancer(self):
        self._process.start()
    
    def arreter(self):
        self._process.join()
    
    # Propriétés
    @property
    def actif(self):
        return self._process.is_alive()
