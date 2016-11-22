# -*- coding: utf-8 -*-

# Importations
from base.utils import verif_type as verif_type_fonc

from base64 import b64encode
from copy import copy
from functools import wraps
import inspect
import pickle

# Décorateurs de fonctions
def verif_type(**kwtypes):
    """
        Ce décorateur prend en paramètre un ou une liste de types pour chaque argument de la fonction à vérifier.
        Ajoute un attribut à la fonction : l'attribut paramsType est un dictionnaire contenant les arguments et les types associés
        @attention: pour que la vérification des arguments non nommés se fasse correctement, il faut que touts les arguments soit définis.
        
        @note: Pour les arguments dont la vérification n'est pas nécessaire, la passage de object comme type acceptera tous les types.
        @note: utilisation de isinstance, la vérification vérifie donc si l'argument est du type ou d'un type dérivé
        
        exemples:
        @verificationTypes(nombre=int)          # Ceci vérifiera que le 1er argument, ou l'argument nommé "nombre" est du type int
        def compter(nombre):
            ...
        
        @verificationTypes(nombre=(int, float)) # Ceci vérifiera que le 1er argument, ou l'argument nommé "nombre" est du type int ou float
        def compter(nombre):
            ...
    """
    # On met les types seuls dans un tuple.
    old_kwtypes = kwtypes
    kwtypes = {}
    
    for cle, val in old_kwtypes.items():
        if not isinstance(val, tuple):
            try:
                val = tuple(val)
            except TypeError:
                val = (val,)
        
        kwtypes[cle] = val
    
    # Définition du décorateur
    def decorateur(fonction):
        """
            Le décorateur.
            @param fonction: la fonction à modifier
        """
        
        # On récupère les arguments dans l'ordre
        sig = inspect.signature(fonction)
        
        # On vérifie la présence de tous les arguments dans kwtypes
        for p in sig.parameters.keys():
            if not p in kwtypes:
                # Si un paramètre n'est pas présent, on l'ajoute avec object comme type
                kwtypes[p] = (object,)
        
        @wraps(fonction)
        def fonctionModifiee(*args, **kwargs):
            """
                La fonction avec la vérification en plus.
            """
            # Tri des arguments non nommés
            args = [(args.index(arg), arg) for arg in args]
            cles = list(sig.parameters.keys())
            
            # 1ere itération : les arguments nommés
            for c in kwargs.keys():
                for p in cles:
                    if c == p[1]:
                        # Vérifie le type de l'argument
                        verif_type_fonc(kwargs[c], c, *kwtypes[c])
                        
                        # Enlève le nom de l'argument de la liste : il ne peut être défini deux fois
                        cles.remove(p)
            
            # 2nd itération les arguments non nommés
            for arg, c in zip(args, cles):
                # Vérifie le type de l'argument
                verif_type_fonc(arg[1], c, *kwtypes[c])
            
            # La vérification est terminée, on peut executer la fonction
            return fonction(*[arg for _, arg in args], **kwargs)
        
        # Permet la modification des types après la définition
        fonctionModifiee.paramsTypes = kwtypes
        
        return fonctionModifiee
    
    return decorateur

def usageUnique(fonction):
    fonctions = []
    
    def fonctionModifiee(*args, **kwargs):
        if not fonctionModifiee in fonctions:
            fonctions.append(fonctionModifiee)
            
            return fonction(*args, **kwargs)
        
        else:
            raise Exception()

    return fonctionModifiee

def method(objet):
    def decorateur(fonction):
        def fonction_modif(*args, **kwargs):
            fonction(objet, *args, **kwargs)
    
        return fonction_modif
    return decorateur

# Décorateurs de classes
def singleton(classe):
    # Initialisation de la sauvegarde de l'instance
    classe.__instance__ = None
    
    # Sauvegarde des anciennes méthodes __new__ et __init__
    classe.__old_new__  = classe.__new__
    classe.__old_init__ = classe.__init__
    
    # Définition des nouvelles méthodes __new__ et __init__
    @wraps(classe.__new__)
    def nouv_new(cls, *args, **kwargs):
        # Test de l'existance d'une instance: si = None pas d'instance, si types différents : rapport à l'héritage, instance de la classe mère/fille
        if (cls.__instance__ != None) and isinstance(cls.__instance__, cls):
            return cls.__instance__
        
        # Création d'une instance
        try:
            self = cls.__old_new__(cls, *args, **kwargs)
        
        except TypeError:
            self = cls.__old_new__(cls)
        
        self.__creer__ = True
        
        # Sauvegarde de l'instance
        cls.__instance__ = self
        
        return self
    
    @wraps(classe.__init__)
    def nouv_init(self, *args, **kwargs):
        if self.__creer__:
            self.__old_init__(*args, **kwargs)
            self.__creer__ = False
    
    # Application des nouvelles méthodes
    classe.__new__  = nouv_new
    classe.__init__ = nouv_init
    
    return classe

def singleton_args(*args, reduce=lambda args: b64encode(pickle.dumps(args[0])).decode("utf-8") if len(args) == 1 else b64encode(pickle.dumps(args)).decode("utf-8")):
    """
    Crée une liste d'instances indexées selon les valeurs des arguments à leur création.
    L'utilisation des mêmes valeurs renverra la même instance.
    
    La fonction (lambda) 'reduce' doit prendre la liste des arguments et renvoyer un identifiant unique sous la forme d'un string
    """
    
    # Décorateur:
    def decorateur(classe):
        # Sauvegardes
        classe.__singleton_args__   = args            # Arguments choisis
        classe.__singleton_sig__    = inspect.signature(classe)
        classe.__singleton_reduce__ = reduce          # Fonction de création de l'identifiant
        classe.__singleton_new__    = classe.__new__  # Fonction __new__ originale
        classe.__singleton_init__   = classe.__init__ # Fonction __init__ originale
        
        # Sauvegarde des instances
        classe.__singleton_instances__ = {}
        
        # Définition des nouvelles méthodes
        @wraps(classe.__new__)
        def nouv_new(cls, *args, **kwargs):
            # Tri des valeurs
            sig  = copy(cls.__singleton_sig__).bind(*args, **kwargs)
            vals = []
            
            sig.apply_defaults()
            
            for n, v in sig.arguments.items():
                if n in cls.__singleton_args__:
                    vals.append(v)
            
            # Création de l'identifiant
            identifiant = cls.__singleton_reduce__(vals)
            
            # Test de l'existance de l'instance
            if identifiant in cls.__singleton_instances__:
                return cls.__singleton_instances__[identifiant]
            
            # Création d'une nouvelle instance
            try:
                self = cls.__singleton_new__(cls, *args, **kwargs)
            
            except TypeError:
                self = cls.__singleton_new__(cls)
            
            self.__creer__ = True
            self.__singleton_identifiant__ = identifiant
            
            # Sauvegarde de l'instance
            cls.__singleton_instances__[identifiant] = self
            
            return self
        
        @wraps(classe.__init__)
        def nouv_init(self, *args, **kwargs):
            if self.__creer__:
                self.__singleton_init__(*args, **kwargs)
                self.__creer__ = False
        
        # Application des nouvelles méthodes
        classe.__new__  = nouv_new
        classe.__init__ = nouv_init
        
        return classe
    return decorateur
