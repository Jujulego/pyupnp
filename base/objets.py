# -*- coding: utf-8 -*-

# Importations:
# Python3
from datetime import datetime, timedelta
import json

# Projet
from base.decorateurs import verif_type

# Classes
class Minuteur():
    """
    Compte le temps passé par soustraction entre la date de création et celle où on lui demande
    s'il à fini.
    """
    
    # Méthodes spéciales
    def __init__(self, duree):
        self._dateCreation = datetime.now()
        self._duree = timedelta(seconds=duree)
    
    def __repr__(self):
        return "<Minuteur: {} >".format(str(self.tempsRestant).split(".")[0])
    
    def __str__(self):
        return str(self.tempsRestant)
    
    # Propriétés
    @property
    def fini(self):
        return self._duree <= datetime.now() - self._dateCreation
    
    @property
    def enCours(self):
        return not self.fini
        
    @property
    def tempsEcoule(self):
        return datetime.now() - self._dateCreation if not self.fini else self._duree
    
    @property
    def tempsRestant(self):
        return self._duree - self.tempsEcoule

class Couleur():
    # Méthodes spéciales
    def __init__(self, rouge, vert, bleu):
        self.rouge = rouge
        self.vert = vert
        self.bleu = bleu
    
    def __len__(self):
        return len(str(self))
    
    def __str__(self):
        return '.'.join([str(self.rouge), str(self.vert), str(self.bleu)])
    
    # Méthodes
    def deconstruct(self):
        return ("base.objets.Couleur", [self.rouge, self.vert, self.bleu], {})
    
    def to_css(self):
        return "rgb({r:d}, {v:d}, {b:d})".format(r=self.rouge, v=self.vert, b=self.bleu)
        
    @verif_type(alpha=(float, int))
    def to_css_alpha(self, alpha):
        if alpha < 0 or alpha > 1:
            raise ValueError("Alpha doit avoir une valeur entre 0 et 1 inclus")
        
        return "rgba({r:d}, {v:d}, {b:d}, {a:f})".format(r=self.rouge, v=self.vert, b=self.bleu, a=alpha)
    
    def to_html(self):
        return "#{r:02X}{v:02X}{b:02X}".format(r=self.rouge, v=self.vert, b=self.bleu)
    
    def to_js(self):
        return "rgb({r:d}, {v:d}, {b:d})".format(r=self.rouge, v=self.vert, b=self.bleu)
        
    @verif_type(alpha=(float, int))
    def to_js_alpha(self, alpha):
        if alpha < 0 or alpha > 1:
            raise ValueError("Alpha doit avoir une valeur entre 0 et 1 inclus")
        
        return "rgba({r:d}, {v:d}, {b:d}, {a:f})".format(r=self.rouge, v=self.vert, b=self.bleu, a=alpha)
    
    # Propriétés
    @property
    def rouge(self):
        return self._rouge
    
    @rouge.setter
    @verif_type(n_valeur=(int, str))
    def rouge(self, n_valeur):
        if isinstance(n_valeur, str):
            if not n_valeur.isdecimal():
                raise ValueError("rouge doit être une valeur numerique décimale")
            n_valeur = int(n_valeur)
        
        self._rouge = n_valeur
    
    @property
    def vert(self):
        return self._vert
    
    @vert.setter
    @verif_type(n_valeur=(int, str))
    def vert(self, n_valeur):
        if isinstance(n_valeur, str):
            if not n_valeur.isdecimal():
                raise ValueError("vert doit être une valeur numerique décimale")
            n_valeur = int(n_valeur)
        
        self._vert = n_valeur
    
    @property
    def bleu(self):
        return self._bleu
    
    @bleu.setter
    @verif_type(n_valeur=(int, str))
    def bleu(self, n_valeur):
        if isinstance(n_valeur, str):
            if not n_valeur.isdecimal():
                raise ValueError("bleu doit être une valeur numerique décimale")
            n_valeur = int(n_valeur)
        
        self._bleu = n_valeur

# Json
class NoErrorsJSONEncoder(json.JSONEncoder):
    # Méthodes
    def default(self, o):
        pass

class OrdreDict(dict):
    # Méthodes
    def ordre_keys_items(self):
        # Générateur qui renvoie les items dans l'ordre alpha-numérique
        class OrdreGen:
            # Méthodes spéciales
            def __init__(self, dictio):
                self.dictio = dictio
                self.dernier = 0
                
                # Récupération et tri des clés
                self.cles = [x for x in self.dictio.keys()]
                self.cles.sort()
            
            def __iter__(self):
                return self
            
            def __next__(self):
                if self.dernier >= len(self.cles):
                    raise StopIteration
                elif self.dernier != None:
                    self.dernier += 1
                    return self.cles[self.dernier - 1], self.dictio[self.cles[self.dernier - 1]]
        
        return OrdreGen(self)

class FStr(str):
    # Méthodes spéciales
    def __bool__(self):
        return False

class Namespace:
    # Méthodes spéciales
    def __init__(self, base={}):
        self.__dict__.update(base)
