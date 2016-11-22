# Importations
from decimal import Decimal as D

# Fonctions
def divent(x, y):
    px = x.as_tuple()[2]
    py = y.as_tuple()[2]
    
    x /= D("1E" + str(px))
    y /= D("1E" + str(py))
    
    return (x//y) * D("1E" + str(px - py))

def modulo(x, y):
    return x - (divent(x, y) * y)
