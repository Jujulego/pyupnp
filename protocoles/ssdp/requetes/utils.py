# -*- coding: utf-8 -*-

# Importations
# Projet
from .base import SSDPRequete
from .exceptions import SSDPTypeErreur
from .msearch import SSDPMSearch, SSDPReponseMSearch
from .notify import SSDPNotify

from base.decorateurs import verif_type

from datetime import datetime

# Fonctions
@verif_type(message=bytes, adresse=tuple, dateReception=datetime)
def analyseSSDPRequete(message, adresse, dateReception):
    """
        Renvoie un objet enfant de SSDPRequete.
    """
    
    rq = SSDPRequete(message, adresse, dateReception)
    
    if rq.methode == "NOTIFY":
        return SSDPNotify(message, adresse, dateReception)
    
    elif rq.methode == "M-SEARCH":
        return SSDPMSearch(message, adresse, dateReception)
    
    elif rq.methode == "Reponse M-SEARCH":
        return SSDPReponseMSearch(message, adresse, dateReception)
    
    raise SSDPTypeErreur("Type de message inconnu", message)
