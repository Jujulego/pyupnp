# Importations
from .requetes.msearch import SSDPMSearch, SSDPReponseMSearch
from .requetes.notify import SSDPNotify
from .requetes.utils import analyseSSDPRequete

from arbresxml import XMLThread, UPnPDeviceXMLParser
from log.mixin import ThreadLogMixin
from periferiques import PeriferiqueDistant
from recherches import DistantRecherches

from datetime import datetime
from socketserver import BaseRequestHandler

# Classes
class SSDPHandler(BaseRequestHandler, ThreadLogMixin):
    # Attributs
    nom_log = "upnp.ssdp"
    
    # Méthodes
    def handle(self):
        self.reception = datetime.now()
        donnees = self.request[0].strip()
        
        try:
            self.requete = analyseSSDPRequete(donnees, self.client_address, self.reception)
        
        except Exception as err:
            self.warning("Erreur lors de l'analyse d'une requete :\n    {!r}\n    {!r}".format(donnees, err))
            return
        
        self.debug("réception de " + repr(self.requete))
        
        try:
            if isinstance(self.requete, SSDPNotify):
                self.handle_notify()
            
            elif isinstance(self.requete, SSDPMSearch):
                self.handle_msearch()
            
            elif isinstance(self.requete, SSDPReponseMSearch):
                self.handle_rep_msearch()
            
            else:
                self.warning("requête SSDP non traitée " + repr(self.requete))
        
        except Exception as err:
            self.error("Erreur dans le traitement d'une requete SSDP\n{!r}".format(err))
    
    def handle_notify(self):
        try:
            perif = PeriferiqueDistant(self.requete.uuid)
            
            xml_test = ((not perif.valide) or (not perif.present)) and (self.requete.nts != "ssdp:byebye")
            
            perif.ajouter_notify(self.requete)
            
            if xml_test:
                try:
                    xth = XMLThread(self.requete.location, UPnPDeviceXMLParser)
                    xth.start()
                    xth.join()
                
                except Exception as err:
                    self.warning("Impossible de lancer l'analyse de l'arbre XML : {!r}".format(err))
        
        except OSError as err:
            self.error("Problèmes de connexion au serveur periferiques : {!r}".format(err))
    
    def handle_msearch(self):
        pass
    
    def handle_rep_msearch(self):
        c_recherches = DistantRecherches()
        
        if self.requete.st in c_recherches:
            try:
                c_recherches.ajouter_reponse(self.requete.st, self.requete)
            
            except KeyError:
                pass
        
        if "ssdp:all" in c_recherches:
            try:
                c_recherches.ajouter_reponse("ssdp:all", self.requete)
            
            except KeyError:
                pass
        
        try:
            perif = PeriferiqueDistant(self.requete.uuid)
            
            xml_test = (not perif.valide) or (not perif.present)
            
            perif.ajouter_rep_msearch(self.requete)
            
            if xml_test:
                try:
                    xth = XMLThread(self.requete.location, UPnPDeviceXMLParser)
                    xth.start()
                    xth.join()
                
                except Exception as err:
                    self.warning("Impossible de lancer l'analyse de l'arbre XML : {!r}".format(err))
        
        except OSError as err:
            self.error("Problèmes de connexion au serveur periferiques : {!r}".format(err))
