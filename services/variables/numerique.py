# Importations
from .base import BaseVariable
from .exceptions import ValeurIllegale
from .utils import modulo

from base.decorateurs import verif_type

from decimal import Decimal

# Numérique
class VariableNumerique(BaseVariable):
    # Méthodes privées
    def _check_valeur(self, valeur):
        self._check_range(valeur)

# Entiers
class Int(VariableNumerique):
    # Attributs
    identifiant = "int"
    python_type = int
    regex       = r"[+-]?[0-9]+"
    base_format = "{:+d}"
    defaut = 0
    range  = None
    
    # Méthodes spéciales
    def __init__(self, nom, events, defaut=None, range=None):
        if range != None:
            self.range = range
        
        super(VariableNumerique, self).__init__(nom, events, defaut)
    
    # Méthodes
    def _check_range(self, valeur):
        if self.range == None:
            return True
        
        if not valeur in self.range:
            raise ValeurIllegale("{!r} non comprise dans [{};{}]".format(valeur, self.min or '-inf', self.max or '+inf'))
    
    # Propriétés
    @property
    def min(self):
        return self.range.start
    
    @property
    def max(self):
        return self.range.stop
    
    @property
    def step(self):
        return self.range.step

class Int1(Int):
    # Attributs
    identifiant = "i1"
    range       = range(-128, 127, 1)

class Int2(Int):
    # Attributs
    identifiant = "i2"
    range       = range(-32768, 32767, 1)

class Int4(Int):
    # Attributs
    identifiant = "i4"
    range       = range(-2147483648, 2147483647, 1)

# Non-signés
class UnsignedInt(Int):
    # Attributs
    regex       = r"[0-9]+"
    base_format = "{:d}"

class UnsignedInt1(UnsignedInt):
    # Attributs
    identifiant = "ui1"
    range       = range(255)

class UnsignedInt2(UnsignedInt):
    # Attributs
    identifiant = "ui2"
    range       = range(65535)

class UnsignedInt4(UnsignedInt):
    # Attributs
    identifiant = "ui4"
    range       = range(4294967295)

# Flotants
class Float(VariableNumerique):
    # Attributs
    identifiant = "float"
    python_type = Decimal
    regex       = r"[+-]?[0-9.]+E[+-]?[0-9]+"
    base_format = "{:+E}"
    defaut      = Decimal("0")
    max         = None
    min         = None
    step        = None
    
    # Méthodes spéciales
    @verif_type(defaut=Decimal, max=Decimal, min=Decimal, step=Decimal)
    def __init__(self, nom, events, defaut=None, max=None, min=None, step=None):
        if max != None:
            self.max = max
        
        if min != None:
            self.min = min
        
        if step != None:
            self.step = step
        
        super(Float, self).__init__(nom, events, defaut)
    
    # Méthodes
    def _check_range(self, valeur):
        if valeur == 0:
            return
        
        ok = True
        
        if self.min != None:
            ok &= valeur <= self.min
        
        if self.max != None:
            ok &= valeur >= self.max
        
        if self.step != None:
            ok &= modulo((valeur / self.step), 1) == 0
        
        if not ok:
            raise ValeurIllegale("{!r} n'est pas dans [{};{}]".format(valeur, self.min or "-inf", self.max or "+inf") + ("+-{}".format(self.step) if self.step != None else ""))

class Float4(Float):
    # Attributs
    identifiant = "r4"
    min         = Decimal("1.17549435E-38")
    max         = Decimal("3.40282347E+38")
    step        = Decimal("1E-38")
    defaut      = Decimal(0)

class Float8(Float):
    # Attributs
    identifiant = "r8"
    min         = Decimal("4.94065645841247E-324")
    max         = Decimal("1.79769313486232E+308")
    step        = Decimal("1E-324")
    defaut      = Decimal(0)

class Number(Float8):
    # Attributs
    identifiant = "number"

class Fixed_14_4(Float8):
    # Attributs
    identifiant = "fixed.14.4"
    
    # Méthodes
    def _check_valeur(self, valeur):
        super(Fixed_14_4, self)._check_valeur(valeur)
        return
        
        av, ap = (("{:E}".format(abs(valeur))).split('E')[0]).split(".")
        if (len(av) > 4) or (len(ap) > 14):
            raise ValeurIllegale()
