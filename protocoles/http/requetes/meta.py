# Importations
from .exceptions import HTTPWarning

import warnings

# Classes (utilisées comme marqueurs)
class BaseRq:
    # Attributs
    __header__  = False
    __requete__ = True

class BaseHe:
    # Attributs
    __header__  = True
    __requete__ = False
    
    nom = None

# Métaclasse
class MetaRqHe(type):
    # Méthodes spéciales
    def __new__(metacls, nom, bases, namespace, **kwargs):
        # Test sur les classes de base :
        rq = False
        he = False
        
        for b in bases:
            if issubclass(b, BaseRq):
                rq = True
            
            elif issubclass(b, BaseHe):
                he = True
        
        if (not rq) and (not he):
            raise TypeError("Doit hériter soit de BaseRq et BaseHe !")
        
        # Cas Requete :
        if rq:
            # ne peux pas hériter d'un header non nommé
            noms = []
            
            for b in bases:
                if not issubclass(b, (BaseRq, BaseHe)):
                    continue
                
                if b.__header__:
                    if b.nom == None:
                        raise TypeError("Ne peux hériter d'un header non nommé !")
                    
                    if b.nom in noms:
                        warnings.warn("Hérite de 2 headers du même nom", HTTPWarning)
        
        # Cas Header :
        elif he:
            # ne peux hériter de + d'un header nommé (attribut nom != None)
            # ne peux hériter d'une requete
            nb = 0
            
            for b in bases:
                if not issubclass(b, (BaseRq, BaseHe)):
                    continue
                
                if not b.__header__:
                    continue
                
                if b.__requete__:
                    raise TypeError("Ne peux pas hériter d'une requête !")
                
                if b.nom == None:
                    continue
                
                if b.nom != (namespace.get("nom", None) or b.nom):
                    raise TypeError("Ne peut pas hériter d'un header nommé différement !")
        
        # Création de la classe
        cls = type.__new__(metacls, nom, bases, namespace, **kwargs)
        
        # Modifications :
        # cas des requetes
        if rq:
            # on stocke les noms headers
            cls._headers = []
            
            for b in bases:
                if not issubclass(b, (BaseRq, BaseHe)):
                    continue
                
                if b.__header__:
                    cls._headers.append(b.nom)
            
            cls._headers = tuple(cls._headers)
        
        # cas des headers
        elif he:
            # On vérifie l'existance des méthodes nécéssaires
            if cls.nom != None:
                cls.nom = cls.nom.upper()
                if not getattr(cls, "_check_{}".format(cls.nom), False):
                    raise TypeError("La classe {} nécessite une méthode _check_{}".format(nom, cls.nom))
                
                if not getattr(cls, "_modif_{}".format(cls.nom), False):
                    raise TypeError("La classe {} nécessite une méthode _modif_{}".format(nom, cls.nom))
        
        return cls
