# Importations
from .requetes.notify import SSDPNotify

from base.decorateurs import verif_type

from datetime import datetime

# Classes
class SSDPGestion:
    # Méthodes spéciales
    def __init__(self):
        self.requetes = {}
        self.root_rq = None
    
    # Méthodes
    @verif_type(requete=SSDPNotify)
    def requete_notify(self, requete):
        if not requete.usn in self.requetes:
            self.requetes[requete.usn] = requete
        
        elif requete.dateReception > self.requetes[requete.usn].dateReception:
            self.requetes[requete.usn] = requete
        
        if requete.rootdevice:
            if self.root_rq == None:
                self.root_rq = requete
            
            elif requete.dateReception > self.root_rq.dateReception:
                self.root_rq = requete
    
    # Propriétés
    @property
    def present(self):
        return self.root_rq.nts == "ssdp:alive"
    
    @property
    def valide(self):
        return (datetime.now() - self.root_rq.dateReception).total_seconds() < self.root_rq.maxage
