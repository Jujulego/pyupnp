# -*- coding: utf-8 -*-

# Importations
# Python3
import abc

# Classe
class BaseAccesseur(metaclass=abc.ABCMeta):
    """
        Permet l'accès à un objet sans l'avoir vraiment.
    """
    
    # Méthodes spéciales :
    # accès aux attributs
    @abc.abstractmethod
    def __getattribute__(self, nom):
        return NotImplemented
    
    def __setattr__(self, nom, val):
        self.__setattr__(nom, val)
    
    def __delattr__(self, nom):
        self.__delattr__(nom)
    
    # accès aux items
    @abc.abstractmethod
    def __getitem__(self, cle):
        return NotImplemented
    
    def __setitem__(self, cle, val):
        self.__setitem__(cle, val)
    
    def __delitem__(self, cle):
        self.__delitem__(cle)
    
    # Comparaison
    def __lt__(self, autre):
        return self.__lt__(autre)
    
    def __le__(self, autre):
        return self.__le__(autre)
    
    def __eq__(self, autre):
        return self.__eq__(autre)
    
    def __ne__(self, autre):
        return self.__ne__(autre)
    
    def __ge__(self, autre):
        return self.__ge__(autre)
    
    def __gt__(self, autre):
        return self.__gt__(autre)
    
    # calcul
    # opérateurs
    def __add__(self, autre):
        return self.__add__(autre)
    
    def __sub__(self, autre):
        return self.__sub__(autre)
    
    def __mul__(self, autre):
        return self.__mul__(autre)
    
    def __truediv__(self, autre):
        return self.__truediv__(autre)
    
    def __floordiv__(self, autre):
        return self.__floordiv__(autre)
    
    def __mod__(self, autre):
        return self.__mod__(autre)
    
    def __divmod__(self, autre):
        return self.__divmod__(autre)
    
    def __pow__(self, autre, modulo=None):
        return self.__pow__(autre, modulo)
    
    def __lshift__(self, autre):
        return self.__rlshift__(autre)
    
    def __rshift__(self, autre):
        return self.__rshift__(autre)
    
    def __and__(self, autre):
        return self.__and__(autre)
    
    def __xor__(self, autre):
        return self.__xor__(autre)
    
    def __or__(self, autre):
        return self.__or__(autre)
    
    # opérateurs réfléchis
    def __radd__(self, autre):
        return self.__radd__(autre)
    
    def __rsub__(self, autre):
        return self.__rsub__(autre)
    
    def __rmul__(self, autre):
        return self.__rmul__(autre)
    
    def __rtruediv__(self, autre):
        return self.__rtruediv__(autre)
    
    def __rfloordiv__(self, autre):
        return self.__rfloordiv__(autre)
    
    def __rmod__(self, autre):
        return self.__rmod__(autre)
    
    def __rdivmod__(self, autre):
        return self.__rdivmod__(autre)
    
    def __rpow__(self, autre, modulo=None):
        return self.__rpow__(autre, modulo)
    
    def __rlshift__(self, autre):
        return self.__rrlshift__(autre)
    
    def __rrshift__(self, autre):
        return self.__rrshift__(autre)
    
    def __rand__(self, autre):
        return self.__rand__(autre)
    
    def __rxor__(self, autre):
        return self.__rxor__(autre)
    
    def __ror__(self, autre):
        return self.__ror__(autre)
    
    # opérateurs augmentés (ex: +=)
    def __iadd__(self, autre):
        return self.__iadd__(autre)
    
    def __isub__(self, autre):
        return self.__isub__(autre)
    
    def __imul__(self, autre):
        return self.__imul__(autre)
    
    def __itruediv__(self, autre):
        return self.__itruediv__(autre)
    
    def __ifloordiv__(self, autre):
        return self.__ifloordiv__(autre)
    
    def __imod__(self, autre):
        return self.__imod__(autre)
    
    def __idivmod__(self, autre):
        return self.__idivmod__(autre)
    
    def __ipow__(self, autre, modulo=None):
        return self.__ipow__(autre, modulo)
    
    def __ilshift__(self, autre):
        return self.__irlshift__(autre)
    
    def __irshift__(self, autre):
        return self.__irshift__(autre)
    
    def __iand__(self, autre):
        return self.__iand__(autre)
    
    def __ixor__(self, autre):
        return self.__ixor__(autre)
    
    def __ior__(self, autre):
        return self.__ior__(autre)
    
    # opérateurs unaires
    def __neg__(self):
        return self.__neg__()
    
    def __pos__(self):
        return self.__pos__()
    
    def __invert__(self):
        return self.__invert__()
    
    # fonctions builtins
    def __abs__(self):
        return self.__abs__()
    
    def __bool__(self):
        return self.__bool__()
    
    def __bytes__(self):
        return self.__bytes__()
    
    def __complex__(self):
        return self.__complex__()
    
    def __del__(self):
        try:
            self.__del__()
        
        except AttributeError:
            return NotImplemented
    
    def __float__(self):
        self.__float__()
    
    def __format__(self, format_spec):
        return self.__format__(format_spec)
    
    def __hash__(self):
        return self.__hash__()
    
    def __int__(self):
        return self.__int__()
    
    def __index__(self):
        return self.__index__()
    
    def __len__(self):
        return self.__len__()
    
    def __repr__(self):
        return "<Accesseur pour " + self.__repr__() + ">"
    
    def __round__(self, n=0):
        return self.__round__(n)
    
    def __str__(self):
        return self.__str__()
    
    # Autres
    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        return NotImplemented
    
    def __contains__(self, item):
        return self.__contains__(item)
    
    def __enter__(self):
        return self.__enter__()
    
    def __exit__(self, t=None, v=None, tr=None):
        return self.__exit__(t, v, tr)
    
    def __iter__(self):
        return self.__iter__()
    
    def __next__(self):
        return self.__next__()
    
    def __reversed__(self):
        return self.__reversed__()

# fonction
def accesseur(objet):
    class Accesseur(BaseAccesseur):
        def __getattribute__(self, nom):
            retour = getattr(objet, nom)
            
            if retour is objet:
                return self
            
            else:
                return retour
        
        def __getitem__(self, cle):
            return objet[cle]
        
        def __call__(self, *args, **kwargs):
            return objet.__call__(*args, **kwargs)
        
    return Accesseur()