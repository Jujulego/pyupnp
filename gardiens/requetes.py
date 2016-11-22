# Importations
from .checker import AdresseIP
from .exceptions import RequeteInvalide
from .utils import identifiant_processus

from base.decorateurs import verif_type

import re
from time import time

# Classes
class BaseRequete:
    # Attributs
    _id_rq_cls  = "base"
    _base_regex = re.compile(rb"Requete Gardien\nauteur: (?P<auteur>[0-9a-f-]{30})\nidentifiant: (?P<identifiant>[0-9a-f-]{47})\ntype: (?P<type>.+?)\n\n(?P<message>.+?)\n\n", re.DOTALL)
    _base_plan  = "Requete Gardien\nauteur: {auteur}\nidentifiant: {auteur}-{epoch:016x}\ntype: {type}\n\n"
    
    # Méthodes spéciales
    @verif_type(requete=bytes)
    def __init__(self, requete):
        self.analyse(requete)
    
    # Méthodes de classe
    @classmethod
    @verif_type(message=(bytes, str))
    def _generer(cls, message):
        if isinstance(message, str):
            message = message.encode("utf-8")
        
        return cls._base_plan.format(auteur=identifiant_processus(), epoch=int(time() * pow(10, 7)), type=cls._id_rq_cls).encode("utf-8") + message + b"\n\n"
    
    @classmethod
    def generer(cls, *args, **kwargs):
        return cls(cls._generer(*args, **kwargs))
    
    @classmethod
    @verif_type(requete=bytes)
    def test(cls, requete):
        try:
            return requete.split(b"\n")[3][6:].decode("utf-8") == cls._id_rq_cls
        
        except:
            return False
    
    # Méthodes
    @verif_type(requete=bytes)
    def analyse(self, requete):
        resultat = self._base_regex.match(requete)
        
        if not resultat:
            raise RequeteInvalide(requete)
        
        resultat = resultat.groupdict()
        self._requete     = requete
        self._auteur      = resultat["auteur"].decode("utf-8")
        self._identifiant = resultat["identifiant"].decode("utf-8")
        self._message     = resultat["message"]
    
    # Propriétés
    @property
    def requete(self):
        return self._requete
    
    @property
    def auteur(self):
        return self._auteur
    
    @property
    def identifiant(self):
        return self._identifiant
    
    @property
    def message(self):
        return self._message

class InfoRequete(BaseRequete):
    # Attributs
    _id_rq_cls  = "info"
    _info_regex = re.compile(rb"(?P<objet>.+?) de (?P<id_lock>.+)\nadresse: (?P<adresse>([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5})")
    _info_plan  = "{objet} de {id_lock}\nadresse: {adresse.adresse}:{adresse.port:d}"
    
    # Méthodes de classes
    @classmethod
    @verif_type(objet=str, id_lock=str, adresse=AdresseIP)
    def _generer(cls, objet, id_lock, adresse):
        return super(InfoRequete, cls)._generer(cls._info_plan.format(objet=objet, id_lock=id_lock, adresse=adresse))
    
    # Méthodes
    def analyse(self, requete):
        super(InfoRequete, self).analyse(requete)
        resultat = self._info_regex.match(self.message)
        
        if not resultat:
            raise RequeteInvalide(self.message)
        
        resultat = resultat.groupdict()
        self._objet   = resultat["objet"].decode("utf-8")
        self._id_lock = resultat["id_lock"].decode("utf-8")
        self._adresse = resultat["adresse"].decode("utf-8")
    
    # Propriétés
    @property
    def adresse(self):
        adresse, port = self._adresse.split(':')
        return AdresseIP(adresse, int(port))
    
    @property
    def objet(self):
        return self._objet
    
    @property
    def id_lock(self):
        return self._id_lock

class ModificationRequete(InfoRequete):
    # Attributs
    _id_rq_cls   = "modif"

class ElectionRequete(BaseRequete):
    # Attributs
    _id_rq_cls      = "election"
    _election_regex = re.compile(rb"election pour (?P<id_lock>.+)")
    _election_plan  = "election pour {}"
    
    # Méthodes de classes
    @classmethod
    @verif_type(id_lock=str)
    def _generer(cls, id_lock):
        return super(ElectionRequete, cls)._generer(cls._election_plan.format(id_lock))
    
    # Méthodes
    def analyse(self, requete):
        super(ElectionRequete, self).analyse(requete)
        resultat = self._election_regex.match(self.message)
        
        if not resultat:
            raise RequeteInvalide(self.message)
        
        resultat = resultat.groupdict()
        self._id_lock = resultat["id_lock"]
    
    # Propriétés
    @property
    def id_lock(self):
        return self._id_lock

class ReponseRequete(BaseRequete):
    # Attributs
    _id_rq_cls     = "reponse"
    _reponse_regex = re.compile(rb"adresse: (?P<adresse>([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5})\nreponse a (?P<id_requete>[0-9a-f-]{47})\n(?P<reponse>.+)", re.DOTALL)
    _reponse_plan  = "adresse: {adresse}\nreponse a {id_requete}\n"
    
    # Méthodes de classes
    @classmethod
    @verif_type(id_requete=str, reponse=(bytes, str), adresse=AdresseIP)
    def _generer(cls, id_requete, reponse, adresse):
        if isinstance(reponse, str):
            reponse = reponse.encode("utf-8")
        
        return super(ReponseRequete, cls)._generer(cls._reponse_plan.format(adresse=("{}:{:d}".format(*(adresse.tuple))), id_requete=id_requete).encode("utf-8") + reponse)
    
    # Méthodes
    def analyse(self, requete):
        super(ReponseRequete, self).analyse(requete)
        
        resultat = self._reponse_regex.match(self.message)
        if not resultat:
            raise RequeteInvalide(self.message)
        
        resultat = resultat.groupdict()
        self._adresse    = resultat["adresse"].decode("utf-8")
        self._id_requete = resultat["id_requete"].decode("utf-8")
        self._reponse    = resultat["reponse"]
    
    # Propriétés
    @property
    def adresse(self):
        adresse, port = self._adresse.split(':')
        return AdresseIP(adresse, int(port))
    
    @property
    def id_requete(self):
        return self._id_requete
    
    @property
    def reponse(self):
        return self._reponse

class MatrixRequete(BaseRequete):
    # Attributs
    _id_rq_cls = "matrix"
