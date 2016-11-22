# Importations
from . import exceptions
from .base import recup_type
from .numerique import Int, Int1, Int2, Int4, UnsignedInt1, UnsignedInt2, UnsignedInt4, Float, Float4, Float8, Number, Fixed_14_4
from .texte import String, URI, UUID, Char, Boolean, BinHex, BinBase64
from .date import Date, DateTime, DateTimeTz, Time, TimeTz

# Fonction
def creer_var_xml(nom, type, events, defaut=None, max=None, min=None, step=None, liste=None):
    # Récupération de la classe
    cls = recup_type(type)
    
    # Transformation des valeurs
    if defaut != None:
        defaut = cls._pythoniser(defaut)
    
    if max != None:
        max = cls._pythoniser(max)
    
    if min != None:
        min = cls._pythoniser(min)
    
    if step != None:
        step = cls._pythoniser(step)
    
    if liste != None:
        nliste = []
        
        for v in liste:
            nliste.append(cls._pythoniser(v))
        
        liste = nliste
    
    # Creation de la variable
    kwargs = {
        "nom"   : nom,
        "defaut": defaut,
        "events": events,
    }
    
    if issubclass(cls, Int) and ((max != None) and (min != None)):
        kwargs["range"] = range(min, max+1, step or 1)
    
    elif issubclass(cls, Float):
        kwargs.update({
            "max" : max,
            "min" : min,
            "step": step,
        })
    
    elif issubclass(cls, String):
        kwargs["liste_vals"] = liste
    
    return cls(**kwargs)
