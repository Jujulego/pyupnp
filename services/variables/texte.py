# Importations
from .base import BaseVariable
from .exceptions import ValeurIllegale

import base64
import re

# Textes
class VariableTexte(BaseVariable):
    # Attributs
    defaut     = ""
    liste_vals = None
    
    # Méthodes spéciales
    def __init__(self, nom, events, defaut=None, liste_vals=None):
        if liste_vals != None:
            self.liste_vals = liste_vals
        
        super(VariableTexte, self).__init__(nom, events, defaut)
    
    # Méthodes privées
    def _check_valeur(self, valeur):
        if self.liste_vals != None:
            if not valeur in self.liste_vals:
                raise ValeurIllegale("Valeur '{}' interdite".format(valeur))

class CheckLongMixin:
    # Attributs
    longueur = 0
    
    # Méthodes privées
    def _check_long(self, valeur):
        if len(valeur) > self.longueur:
            raise ValeurIllegale()
    
    @classmethod
    def _pythoniser(cls, valeur):
        cls._check_long(valeur)
        return super(CheckLongMixin, cls)._pythoniser(valeur)
    
    def _check_valeur(self, valeur):
        super(CheckLongMixin, self)._check_valeur(valeur)
        self._check_long(valeur)

# Booléens
class Boolean(VariableTexte):
    # Attributs
    identifiant = "boolean"
    python_type = bool
    defaut      = False
    liste_vals  = ["0", "1", "yes", "no", "true", "false"]
    
    # Méthodes privées
    @classmethod
    def _pythoniser(cls, valeur):
        if valeur in ["0", "no", "false"]:
            return False
        
        elif valeur in ["1", "yes", "true"]:
            return True
        
        raise ValeurIllegale(valeur)
    
    def _xmliser(self):
        if self.valeur:
            return "true"
        
        return "false"
    
    def _check_valeur(self, valeur):
        if valeur not in [True, False]:
            raise ValeurIllegale("Soit True soit False pas '{!r}'".format(valeur))

# Chaîne
class String(VariableTexte):
    # Attributs
    identifiant = "string"
    python_type = str
    regex       = r".*"
    flags       = re.DOTALL
    base_format = "{:s}"

# Caractère
class Char(CheckLongMixin, String):
    # Attributs
    identifiant = "char"
    regex       = r"."
    longueur    = 1

# URI
class URI(String):
    # Attributs
    identifiant = "uri"

# UUID
class UUID(CheckLongMixin, String):
    # Attributs
    identifiant = "uuid"
    regex       = r"[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}"
    flags       = re.IGNORECASE
    longueur    = 36

# Binaire
class BinBase64(String):
    # Attributs
    identifiant = "bin.base64"
    python_type = bytes
    defaut      = b""
    regex       = r".*"
    flags       = re.DOTALL
    
    # Méthodes privées
    @classmethod
    def _pythoniser(cls, valeur):
        return base64.standard_b64decode(valeur)
    
    def _xmliser(self):
        return base64.standard_b64encode(self.valeur).decode("utf-8")

class BinHex(String):
    # Attributs
    identifiant = "bin.hex"
    python_type = bytes
    defaut      = b""
    regex       = r"[0-9a-f]*"
    flags       = re.DOTALL | re.IGNORECASE
    
    # Méthodes privées
    @classmethod
    def _pythoniser(cls, valeur):
        table  = {
            0x30: 0x0,
            0x31: 0x1,
            0x32: 0x2,
            0x33: 0x3,
            0x34: 0x4,
            0x35: 0x5,
            0x36: 0x6,
            0x37: 0x7,
            0x38: 0x8,
            0x39: 0x9,
            0x61: 0xa,
            0x62: 0xb,
            0x63: 0xc,
            0x64: 0xd,
            0x65: 0xe,
            0x66: 0xf,
        }
        
        depart = valeur.lower().encode("utf-8")
        valeur = b""
        i = 0
        
        while i < len(depart):
            b = (table[depart[i]] * 16) + table[depart[i+1]]
            valeur += b.to_bytes(1, "little")
            i += 2
        
        return valeur
    
    def _xmliser(self):
        valeur  = self.valeur
        arrivee = ""
        
        for c in valeur:
            arrivee += hex(c)[2:]
        
        return arrivee
