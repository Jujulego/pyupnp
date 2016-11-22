
# Importations
from .communication import Serveur
from .perif_stock import PeriferiqueStock

from base.exceptions import CommunicationErreur
from base.decorateurs import verif_type
from log.mixin import ThreadLogMixin

from socketserver import BaseRequestHandler
import threading as th

# Classe
class PerifHandler(ThreadLogMixin, BaseRequestHandler):
    # Attributs
    nom_log = "upnp.periferiques"
    
    # Méthodes
    def setup(self):
        self.conn = Serveur(self.request)
    
    def handle(self):
        try:
            # Réception de la requête
            requete, opts, nopts = self.conn.recevoir()
            
            # Traitement
            if hasattr(self, requete):
                self.conn.envoyer(getattr(self, requete)(*opts, **nopts))
            
            else:
                raise KeyError("Requête inconnue : {}".format(requete))
        
        except EOFError:
            self.error("Periferique handler : EOFError")
        
        except OSError as err:
            self.error("Periferique handler : {!r}".format(err))
        
        except Exception as err:
            self.conn.envoyer(err)
            raise
    
    @verif_type(uuid=(int, str))
    def recup_perif(self, uuid):
        if isinstance(uuid, int):
            return self.perifs.objet.rechercher(id=uuid)[0]["periferique"].valeur
        
        return self.perifs.objet.rechercher(uuid=uuid)[0]["periferique"].valeur
    
    # Requetes :
    @verif_type(uuid=str)
    def creer_perif(self, uuid):
        if not uuid in self.uuids:
            with self.perifs:
                if not uuid in self.uuids:
                    id_p = len(self.perifs.objet) + 1
                    
                    with self.server.liste.events:
                        event = self.server.liste.events.objet[uuid] = th.Event()
                    
                    self.perifs.objet.ajouter_valeurs(uuid=uuid, id=id_p, periferique=PeriferiqueStock(uuid, id_p, event))
                    self.server.liste.queue.put(("ajout", [], {"uuid": uuid, "id_p": id_p}))
        
        return None
    
    @verif_type(uuid=(int, str))
    def existe_perif(self, uuid):
        if isinstance(uuid, int):
            return uuid in self.ids
        
        return uuid in self.uuids
    
    @verif_type(uuid=(int, str), infos=dict)
    def mise_a_jour(self, uuid, infos):
        perif = self.recup_perif(uuid)
        perif.mise_a_jour(infos)
        return None
    
    @verif_type(uuid=(int, str))
    def recup_infos(self, uuid):
        perif = self.recup_perif(uuid)
        return perif.infos
    
    def recup_liste(self):
        return [u.valeur for u in self.perifs.objet["uuid"].donnees()]
    
    @verif_type(uuid=(int, str))
    def ajouter_service(self, uuid, infos):
        perif = self.recup_perif(uuid)
        perif.ajouter_service(infos)
    
    @verif_type(uuid=(int, str))
    def maj_service(self, uuid, nom, infos):
        perif = self.recup_perif(uuid)
        perif.maj_service(nom, infos)
    
    @verif_type(uuid=(int, str))
    def recup_services(self, uuid):
        perif = self.recup_perif(uuid)
        return perif.services.infos
    
    def finish(self):
        self.conn.deconnecter()
    
    # Propriétés
    @property
    def perifs(self):
        return self.server.perifs
    
    @property
    def uuids(self):
        return [u.valeur for u in self.perifs.objet["uuid"].donnees()]
    
    @property
    def ids(self):
        return [u.valeur for u in self.perifs.objet["id"].donnees()]
