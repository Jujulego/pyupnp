# Importations
from .base import BaseAction
from .mixin import ListeMixin

from helper import Helper
from protocoles.ssdp.requetes.msearch import SSDPMSearch
from periferiques import PeriferiqueDistant
from recherches import DistantRecherches

import socket
import struct
from time import sleep

# Variables
helper = Helper()

# Classe
class DecouverteAction(BaseAction, ListeMixin):
    # Attributs
    nom = "decouverte"
    
    multicast  = "239.255.255.250"
    port       = 1900
    timetolive = helper.TTL_REQUETES
    
    # Méthodes
    def creer_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.timetolive)
        
        sock.bind(('', 1900))
        
        mreq = struct.pack('4sl', socket.inet_aton(self.multicast), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        return sock
    
    def fermer_socket(self, sock):
        mreq = struct.pack('4sl', socket.inet_aton(self.multicast), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        
        sock.close()
    
    def executer(self):
        sock = self.creer_socket()
        
        try:
            recherches = DistantRecherches()
            requete = SSDPMSearch(donnees=vars(self.args))
            recherches.creer_recherche(requete)
            
            self.info("Envoi d'une recherche : {}".format(requete.st))
            self.afficher("Envoi de la requête ...")
            
            for _ in range(self.args.envois):
                sock.sendto(requete.message, (self.multicast, self.port))
            
        finally:
            self.fermer_socket(sock)
        
        self.afficher("\033[A\033[KCollecte des réponses ...")
        retour = recherches.recup_recherche(requete.st)
        
        self.info("Total de {} reponses pour {}".format(len(retour["reponses"]), requete.st))
        
        if len(retour["reponses"]) == 0:
            self.afficher("Pas de réponses ...")
            return
        
        self.afficher("\033[A\033[KAnalyse des réponses ...")
        sleep(5)
        
        # Récupération des différents uuids de périfériques
        uuids = []
        for u in retour["reponses"]:
            if not u.uuid in uuids:
                uuids.append(u.uuid)
        
        self.afficher(self.generer_liste(PeriferiqueDistant.liste(*uuids)))
