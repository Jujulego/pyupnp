# Importations
from .decorateurs import verif_type
from .exceptions import MD5CheckErreur, CommunicationErreur

from log.mixin import ThreadLogMixin

import hashlib
import pickle
import socket
import select

# Classe
class BaseServeur:
    # Méthodes spéciales
    def __init__(self, socket):
        self.socket = socket
    
    # Méthodes
    @verif_type(message=bytes)
    def envoyer(self, message):
        # Envoi
        envoye = 0
        
        while envoye < len(message):
            _, w, _ = select.select([], [self.socket], [], 1)
            
            if self.socket in w:
                envoye += self.socket.send(message[envoye:])
    
    @verif_type(taille=int, buffer=int)
    def recevoir(self, taille=1024, buffer=1024):
        # Réception
        message = b""
        
        while len(message) < taille:
            # Ajustement du buffer
            buffer = min(buffer, taille - len(message))
            
            # select
            r, _, _ = select.select([self.socket], [], [], 1)
            
            # Réception
            if self.socket in r:
                message += self.socket.recv(buffer)
        
        # Ajustement du message
        return message[:taille]
    
    def deconnecter(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        
        except OSError:
            pass
        
        self.socket.close()

class BaseClient(BaseServeur):
    # Attributs
    adresse = ("", 0)
    
    # Méthodes spéciales
    def __init__(self):
        self.connecte = False
    
    def __enter__(self):
        self.connecter()
    
    def __exit__(self, t,v,b):
        self.deconnecter()
    
    # Méthodes
    def connecter(self, sock=None):
        assert not self.connecte, "Le client est déjà connecté !"
        
        if sock == None:
            self.socket = socket.socket()
            self.socket.connect(self.adresse)
        
        else:
            self.socket = sock
        
        self.connecte = True
    
    @verif_type(message=bytes)
    def envoyer(self, message):
        assert self.connecte, "Le client n'est pas connecté !"
        
        super(BaseClient, self).envoyer(message)
    
    @verif_type(taille=int, buffer=int)
    def recevoir(self, taille=1024, buffer=1024):
        assert self.connecte, "Le client n'est pas connecté !"
        
        return super(BaseClient, self).recevoir(taille, buffer)
    
    def deconnecter(self):
        assert self.connecte, "Le client n'est pas connecté !"
        
        super(BaseClient, self).deconnecter()
        
        self.connecte = False

# Mixins
class TailleCheckMixin:
    # Méthodes
    @verif_type(message=bytes)
    def envoyer(self, message):
        # Calcul de la taille du message ramenée sur 16o
        taille = len(message).to_bytes(16, 'little') # 16o limite la taille du message à 256^16o soit 256To
        
        # Envoi
        super(TailleCheckMixin, self).envoyer(taille)
        super(TailleCheckMixin, self).envoyer(message)
    
    def recevoir(self):
        # Reception de la taille
        taille = int.from_bytes(super(TailleCheckMixin, self).recevoir(16), 'little')
        return super(TailleCheckMixin, self).recevoir(taille)

class MD5CheckMixin(TailleCheckMixin):
    # Méthodes
    @verif_type(message=bytes)
    def envoyer(self, message):
        # Calcul du hash
        hash = hashlib.md5(message).digest()
        
        # Envoi du hash
        super(MD5CheckMixin, self).envoyer(hash)
        
        # Envoi du message
        super(MD5CheckMixin, self).envoyer(message)
    
    def recevoir(self, buffer=1024):
        # Réception du hash
        hash = super(MD5CheckMixin, self).recevoir()
        
        # Réception du message
        message = super(MD5CheckMixin, self).recevoir()
        
        # Test
        if hashlib.md5(message).digest() != hash:
            raise MD5CheckErreur(message)
        
        return message

class PickleMixin(MD5CheckMixin):
    # Méthodes privées
    def envoyer(self, message):
        # Picklage
        message = pickle.dumps(message)
        
        # Envoi du message
        super(PickleMixin, self).envoyer(message)
    
    def recevoir(self):
        # Réception
        message = super(PickleMixin, self).recevoir()
        
        # Dépicklage
        return pickle.loads(message)
