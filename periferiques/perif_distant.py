# Importations
from .communication import Client

from arbresxml.thread import XMLThread
from arbresxml.upnp_serv import UPnPServiceXMLParser
from base.wrapper import ThreadSafeWrapper
from log.mixin import ThreadLogMixin
from services.serv_distant import Service

from datetime import datetime, timedelta
import threading as th

# Classe
class PeriferiqueDistant(ThreadLogMixin):
    # Attributs
    nom_log = "upnp"
    
    # Méthodes spéciales
    def __init__(self, uuid):
        self._uuid = uuid
        self._client = Client()
        
        if uuid != "":
            if not self._client.envoyer_requete("existe_perif", uuid=uuid):
                self._client.envoyer_requete("creer_perif", uuid=uuid)
    
    def __repr__(self):
        return "<PeriferiqueDistant {}>".format(self.infos.get("nom simple", self.uuid))
    
    # Méthodes privées
    def _recup_infos(self):
        return self._client.envoyer_requete("recup_infos", uuid=self._uuid)
    
    def _recup_services(self):
        return self._client.envoyer_requete("recup_services", uuid=self._uuid)
    
    def _mise_a_jour(self, infos):
        return self._client.envoyer_requete("mise_a_jour", uuid=self._uuid, infos=infos)
    
    # Méthodes de classe
    @classmethod
    def liste(cls, *uuids):
        if len(uuids) == 0:
            uuids = Client().envoyer_requete("recup_liste")
        
        return [cls(uuid) for uuid in uuids]
    
    # Méthodes
    def ajouter_notify(self, requete):
        infos = {}
        
        infos["uuid"]    = requete.uuid
        infos["adresse"] = requete.adresseClient
        infos["present"] = requete.nts == "ssdp:alive"
        infos["fin_validite"] = requete.dateReception + timedelta(seconds=requete.maxage)
        
        self._mise_a_jour(infos)
    
    def ajouter_rep_msearch(self, requete):
        infos = {}
        
        infos["uuid"]    = requete.uuid
        infos["adresse"] = requete.adresseClient
        infos["present"] = True
        infos["fin_validite"] = requete.dateReception + timedelta(seconds=requete.maxage)
        
        self._mise_a_jour(infos)
    
    def ajouter_xml(self, infos):
        services = infos["services"]
        del infos["services"]
        
        self._mise_a_jour(infos)
        
        for di in services.values():
            xth = XMLThread(di["description"], UPnPServiceXMLParser)
            xth.start()
            xth.join()
            
            try:
                self.ajouter_service(di, xth.parser.variables, xth.parser.actions)
            
            except Exception as err:
                self.error(repr(err))
    
    def ajouter_service(self, infos, variables, actions):
        return self._client.envoyer_requete("ajouter_service", uuid=self._uuid, infos={"infos": infos, "variables": variables, "actions": actions})
    
    # Propriétés
    @property
    def infos(self):
        return self._recup_infos()
    
    @property
    def services(self):
        services = self._recup_services()
        serv_obj = []
        
        for ident in services.keys():
            serv_obj.append(Service(self, ident))
        
        return serv_obj
    
    @property
    def uuid(self):
        return self.infos["uuid"]
    
    @property
    def id(self):
        return self.infos["id"]
    
    @property
    def adresse(self):
        return self.infos.get("adresse", None)
    
    @property
    def present(self):
        return self.infos.get("present", False)
    
    @property
    def fin_validite(self):
        return self.infos.get("fin_validite", datetime(1970, 1, 1))
    
    @property
    def valide(self):
        return datetime.now() <= self.fin_validite
