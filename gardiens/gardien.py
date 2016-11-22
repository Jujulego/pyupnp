# Importations
from .base import BaseGardien
from .checker import AdresseIP, CheckerGardien, check
from .exceptions import *
from .requetes import *
from .tcp import TCPGardien, TCPConnexion
from .thread import BaseThread, PreparationThread
from .udp import UDPGardien
from .utils import identifiant_processus

from base.decorateurs import verif_type
from base.exceptions import AntiDeadLock
from base.threads.chargement import AnimationChargement
from base.wrapper import ThreadSafeWrapper

from datetime import datetime
import multiprocessing as mp
import pickle
import queue
import socket
import threading as th
from time import sleep

# Classes
class Garde:
    # Méthodes spéciales
    def __init__(self):
        self._dict = {}
    
    def __repr__(self):
        return repr(self._dict)
    
    def __len__(self):
        return len(self._dict)
    
    def __getitem__(self, item):
        return self._dict[item]
    
    def __setitem__(self, item, valeur):
        self._dict[item] = valeur
    
    def __delitem__(self, item):
        del self._dict[item]
    
    def __contains__(self, obj):
        return obj in self._dict
    
    def __iter__(self):
        return self._dict.__iter__()
    
    # Méthodes
    def keys(self):
        return self._dict.keys()
    
    def items(self):
        return self._dict.items()
    
    def values(self):
        return self._dict.values()
    
    def ajouter(self, id_lock):
        self[id_lock] = {"adresse": None, "propriétaire": "aucun", "statut": 0}
    
    def statut(self, id_lock):
        assert id_lock in self, "{} inconnu".format(id_lock)
        
        if self[id_lock].get("adresse"):
            if self[id_lock]["adresse"].valide:
                return self[id_lock]["statut"]
            
            else:
                self[id_lock] = {"adresse": None, "propriétaire": "aucun", "statut": 0}
        
        return 0
        
    def proprio(self, id_lock):
        assert id_lock in self, "{} inconnu".format(id_lock)
        
        if self.statut(id_lock) == 0:
            return "aucun"
        
        else:
            return self[id_lock]["propriétaire"]
    
    @verif_type(adresse=AdresseIP)
    def bloquer(self, id_lock, proprio, adresse):
        assert id_lock in self, "{} inconnu".format(id_lock)
        
        if self.statut(id_lock) == 0 or self.proprio(id_lock) == proprio:
            self[id_lock]["adresse"] = adresse
            self[id_lock]["propriétaire"] = proprio
            self[id_lock]["statut"] += 1
            
            return True
        
        return False
    
    def debloquer(self, id_lock, proprio):
        assert id_lock in self, "{} inconnu".format(id_lock)
        
        if self.proprio(id_lock) == proprio:
            self[id_lock]["statut"] -= 1
            
            if self.statut(id_lock) == 0:
                self[id_lock]["adresse"] = None
                self[id_lock]["propriétaire"] = "aucun"
            
            return True
        
        return False

class GardienThread(BaseThread):
    # Méthodes
    def __init__(self, pipe):
        self.udp = UDPGardien()
        self.tcp = TCPGardien()
        
        self.pipe = pipe
        self.recherches = ThreadSafeWrapper({})
        self.garde = ThreadSafeWrapper(Garde())
        self.eligible = ThreadSafeWrapper(True)
        
        super(GardienThread, self).__init__(name="GardienTread " + identifiant_processus())
    
    # Méthodes
    def run(self):
        self.udp.lancer()
        self.tcp.lancer()
        
        while True:
            try:
                try:
                    self.handle_udp(*(self.udp.recevoir(timeout=0.005)))
                
                except queue.Empty:
                    pass
                
                except EOFError:
                    self.error("Arrêt du thread UDP ... redémarrage")
                    self.udp = UDPGardien()
                    self.udp.lancer()
                
                try:
                    self.handle_tcp(*(self.tcp.recevoir_modif(timeout=0.005)))
                
                except queue.Empty:
                    pass
                
                except EOFError:
                    self.error("Arrêt du thread TCP ... redémarrage")
                    self.tcp = TCPGardien()
                    self.tcp.lancer()
                
                if self.pipe.poll(0.005):
                    message = self.pipe.recv()
                    
                    if message == "fin":
                        break
            
            except Exception as err:
                self.error("gardien erreur : " + repr(err))
        
        self.udp.arreter()
        self.tcp.arreter()
    
    def handle_tcp(self, sock, rq):
        if rq.id_lock in self.garde.objet:
            if rq.objet == "bloquer":
                message = "erreur: lock déjà pris".encode("utf-8")
                
                with self.garde:
                    if self.garde.objet.bloquer(rq.id_lock, rq.auteur, rq.adresse):
                        message = b"ok"
                
                sock.send(message)
            
            elif rq.objet == "debloquer":
                message = "erreur: lock possédé par un autre".encode("utf-8")
                
                with self.garde:
                    if self.garde.objet.debloquer(rq.id_lock, rq.auteur):
                        message = b"ok"
                
                sock.send(message)
            
            elif rq.objet == "ajout":
                sock.send(b"ok")
                
        else:
            if rq.objet == "ajout":
                with self.garde:
                    self.garde.objet.ajouter(rq.id_lock)
                
                if rq.id_lock == self.possession:
                    self.garde.objet.bloquer(rq.id_lock, identifiant_processus(), self.tcp.adresse)
                    self.garde.objet[rq.id_lock]["statut"] = self.statut
                
                sock.send(b"ok")
            
            else:
                sock.send("erreur: Ne possède pas ce lock".encode("utf-8"))
    
    def handle_udp(self, adresse, rq):
        rq = rq.requete
        
        if ElectionRequete.test(rq) and self.eligible.objet:
            rq = ElectionRequete(rq)
            
            if rq.id_lock.decode("utf-8") in self.garde.objet:
                self.udp.envoyer(ReponseRequete.generer(rq.identifiant, "possédé", self.tcp.adresse))
            
            elif rq.id_lock.decode("utf-8") == self.possession:
                self.udp.envoyer(ReponseRequete.generer(rq.identifiant, "propriétaire", self.tcp.adresse))
            
            elif (rq.id_lock.decode("utf-8") in self.elections.objet) and (identifiant_processus() != rq.auteur):
                self.udp.envoyer(ReponseRequete.generer(rq.identifiant, "en cours", self.tcp.adresse))
            
            else:
                self.udp.envoyer(ReponseRequete.generer(rq.identifiant, "candidat " + str(len(self.garde.objet)), self.tcp.adresse))
        
        elif ReponseRequete.test(rq):
            rq = ReponseRequete(rq)
            
            if rq.id_requete in self.recherches.objet:
                with self.recherches:
                    liste = self.recherches.objet[rq.id_requete][0]
                    cond  = self.recherches.objet[rq.id_requete][1]
                    
                    with cond:
                        liste.append(rq)
                        cond.notify_all()
    
    # Propriétés
    @property
    def gardien(self):
        return mp.current_process().gardien
        return self._gardien
    
    @property
    def elections(self):
        return self.gardien._elections
    
    @property
    def possession(self):
        return self.gardien.possession
    
    @property
    def statut(self):
        return self.gardien._statut.objet

class Gardien(BaseGardien):
    # Méthodes
    def __new__(cls):
        proc = mp.current_process()
        
        if not hasattr(proc, "gardien"):
            instance = super(Gardien, cls).__new__(cls)
            instance._creer = True
            proc.gardien = instance
        
        return proc.gardien
    
    def __init__(self):
        if self._creer:
            super(Gardien, self).__init__()
            
            self.checker = CheckerGardien()
            self.checker.lancer()
            
            self._pipe, pipe = mp.Pipe()
            
            self._possession = ThreadSafeWrapper([])
            self._statut     = ThreadSafeWrapper({})
            self._lock_ip    = ThreadSafeWrapper({})
            self._elections  = ThreadSafeWrapper({})
            
            self.thread = GardienThread(pipe)
            self.thread._gardien = self
            
            self._creer = False
    
    def __repr__(self):
        return "<Gardien {}, {}>".format(identifiant_processus(), self.status)
    
    def _envoyer_udp(self, requete):
        return self.thread.udp.envoyer(requete)
    
    def _rechercher(self, requete, attente=5, test_fin=None):
        cond = th.Condition()
        
        with self.recherches:
            self.recherches.objet[requete.identifiant] = ([], cond)
        
        self._envoyer_udp(requete)
        
        if test_fin != None:
            with cond:
                cond.wait_for(lambda : test_fin(self.recherches.objet[requete.identifiant][0]), attente)
        
        else:
            sleep(attente)
        
        with cond:
            reponses = self.recherches.objet[requete.identifiant][0]
        
        with self.recherches:
            del self.recherches.objet[requete.identifiant]
        
        return reponses
    
    def _infos(self, id_lock, objet):
        rq = InfoRequete.generer(objet, id_lock, self.thread.tcp.adresse)
        
        conn = TCPConnexion(self._lock_ip.objet[id_lock])
        
        with conn:
            conn.envoyer(rq.requete)
            retour = pickle.loads(conn.recevoir())
        
        if isinstance(retour, Exception):
            raise retour
        
        return retour
    
    @verif_type(addr=AdresseIP)
    def _ajouter(self, addr, idlock):
        with self._lock_ip:
            self._lock_ip.objet[idlock] = addr
    
    def _recuperer(self, id_lock):
        addr = self._lock_ip.objet[id_lock]
        check(addr)
        
        if not addr.valide:
            self.checker.supprimer(addr)
            _, addr = self.election(id_lock)
        
        return addr
    
    # Méthodes
    def lancer(self, eligible=True):
        super(Gardien, self).lancer()
        
        with self.thread.eligible:
            self.thread.eligible.objet = eligible
        
        self.thread.start()
    
    def connait(self, id_lock):
        return id_lock in self._lock_ip.objet
    
    def election(self, id_lock):
        assert self._status.objet == 1, "N'est pas lancé"
        
        try:
            # On vérifie que l'élection ne soit pas déjà en cours
            en_cours = False
            event    = th.Event()
            
            with self._elections:
                if id_lock in self._elections.objet:
                    en_cours = True
                    event    = self._elections.objet[id_lock]
                
                else:
                    self._elections.objet[id_lock] = event
            
            # Si elle est déjà en cours, on attend et on récupère le résultat
            if en_cours:
                event.wait()
                return "", self._recuperer(id_lock)
            
            # Envoi de la recherche
            requete = ElectionRequete.generer(id_lock)
            reponses = self._rechercher(requete, attente=5, test_fin=lambda reps: any([r.reponse.decode("utf-8") == "possédé" for r in reps]))
            
            if len(reponses) == 0:
                # S'il n'y a pas de réponses :
                raise PasDeReponse()
            
            # Analyse des réponses
            en_cours = False
            for r in reponses:
                if r.reponse.decode("utf-8") == "possédé":
                    # Si le lock à déjà un gardien
                    self._ajouter(r.adresse, id_lock)
                    return r.auteur, r.adresse
                
                elif r.reponse.decode("utf-8") == "en cours":
                    # Si l'élection à déjà lieu dans un autre processus
                    en_cours = True
            
            if en_cours:
                with self._elections:
                    if id_lock in self._elections.objet:
                        self._elections.objet.remove(id_lock)
                
                # On attend 6 secondes (l'élection en prend 5, on est donc sûr que c'est fini) et on recommence !
                sleep(6)
                return self.election(id_lock)
            
            # On choisi parmis les candidats, si le lock est possédé par un processus, mais qu'il n'y a plus de gardien, il devient ce gardien
            elu = min([(r.reponse, r.auteur, r) for r in reponses])[2]
            
            for r in reponses:
                if r.reponse.decode("utf-8") == "propriétaire":
                    elu = r
            
            # On notifie l'élection à l'élu
            conn = TCPConnexion(elu.adresse)
            
            with conn:
                conn.envoyer(ModificationRequete.generer("ajout", id_lock, self.thread.tcp.adresse).requete)
                
                retour = b""
                while retour != b"ok":
                    retour = conn.recevoir()
            
            self._ajouter(r.adresse, id_lock)
            return elu.auteur, elu.adresse
        
        finally:
            with self._elections:
                if id_lock in self._elections.objet:
                    del self._elections.objet[id_lock]
            
            event.set()
    
    def est_bloque(self, id_lock):
        assert self._status.objet == 1, "L'objet n'est pas lancé"
        assert self.connait(id_lock), "Ne connait pas ce lock, procédez à l'élection"
        
        return self._infos(id_lock, "statut") != 0
    
    def bloquer(self, id_lock):
        rq = ModificationRequete.generer("bloquer", id_lock, self.thread.tcp.adresse)
        
        while True:
            try:
                conn = TCPConnexion(self._lock_ip.objet[id_lock])
                break
            
            except AdresseInvalideErreur:
                self.election(id_lock)
        
        with conn:
            conn.envoyer(rq.requete)
            retour = conn.recevoir().decode("utf-8")
        
        if retour.startswith("erreur"):
            message = retour[8:]
            
            if message == "Ne possède pas ce lock":
                self.election(id_lock)
                return self.bloquer(id_lock)
            
            else:
                raise ErreurDistante(retour[8:])
        
        if retour == "ok":
            with self._possession:
                if not id_lock in self.possession:
                    self._possession.objet.append(id_lock)
            
            with self._statut:
                self._statut.objet[id_lock] = 1
            
            t = th.current_thread()
            
            if hasattr(t, "possesseur"):
                t.possesseur += 1
            
            else:
                t.possesseur = 1
            
            return True
        
        else:
            return False
    
    def debloquer(self, id_lock):
        assert self._status.objet == 1, "L'objet n'est pas lancé"
        assert self.connait(id_lock), "Ne connait pas ce lock, procédez à l'élection"
        
        if self.possession == None:
            return False
        
        rq = ModificationRequete.generer("debloquer", id_lock, self.thread.tcp.adresse)
        
        conn = TCPConnexion(self._lock_ip.objet[id_lock])
        with conn:
            conn.envoyer(rq.requete)
            retour = conn.recevoir().decode("utf-8")
        
        if retour.startswith("erreur"):
            message = retour[8:]
            
            if message == "Ne possède pas ce lock":
                self.election(id_lock)
                return self.debloquer(id_lock)
            
            elif message == "lock possédé par un autre":
                retour = "ok"
            
            else:
                raise ErreurDistante(retour[8:])
        
        if retour == "ok":
            if self._infos(id_lock, "statut") == 0:
                try:
                    with self._possession:
                        self._possession.objet.remove(id_lock)
                
                except ValueError:
                    pass
                
                with self._statut:
                    self._statut.objet[id_lock] -= 1
            try:
                t = th.current_thread()
                t.possesseur -= 1
            
            except AttributeError:
                t.possesseur = self._statut.objet[id_lock]
            
            return True
        
        else:
            return False
    
    def arreter(self, verbose=True, add_texts=None):
        # Attente de l'arrêt des threads possédant un lock
        if verbose:
            ta = AnimationChargement("Arrêt des threads possédant un lock" + (" ({})".format(add_texts) if add_texts else ""))
            ta.start()
        
        with self.thread.eligible:
            self.thread.eligible.objet = False
        
        for t in PreparationThread.__registre__.objet:
            if t.is_alive():
                t.join()
        
        for t in th.enumerate():
            if not hasattr(t, "possesseur"):
                continue
            
            if t.is_alive() and t.possesseur > 0:
                t.join()
        
        if verbose:
            ta.fini = True
            ta.join()
        
        # Libération des locks actuellement possédés
        if verbose:
            ta = AnimationChargement("Libération des locks" + (" ({})".format(add_texts) if add_texts else ""))
            ta.start()
            
        for p in self.possession:
            try:
                while not self.debloquer(p):
                    pass
            
            except OSError:
                pass
        
        garde = list(self.garde.objet.keys())
        
        with self.garde:
            self.garde.objet = Garde()
        
        if len(garde) > 0:
            # Dispertion des locks dont ce thread est le gardien
            threads = []
            
            def liberation(self, id_lock):
                try:
                    self.election(id_lock)
                
                except PasDeReponse:
                    pass
            
            for id_lock in garde:
                t = th.Thread(target=liberation, args=(self, id_lock))
                t.start()
                threads.append(t)
            
            for t in threads:
                t.join()
            
        if verbose:
            ta.fini = True
            ta.join()
        
        # Fin du programme
        super(Gardien, self).arreter()
        
        self._pipe.send("fin")
        self.thread.join()
        
        self.checker.arreter()
    
    # Propriétés
    @property
    def garde(self):
        return self.thread.garde
    
    @property
    def possession(self):
        return self._possession.objet
    
    @property
    def recherches(self):
        return self.thread.recherches
    
    @property
    def adresse_tcp(self):
        return self.thread.tcp.thread.adresse
