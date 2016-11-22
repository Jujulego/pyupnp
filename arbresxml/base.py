# Importations
from helper import Helper
from log.mixin import ThreadLogMixin

import abc
from xml.etree import ElementTree as ET

# Variables
helper = Helper()

# Execption :
class XMLInterrupt(Exception):
    # Méthodes spéciales
    def __init__(self, message, niveau):
        self.message = message
        self.niveau  = niveau

# Classe
class BaseXMLParser(ThreadLogMixin, metaclass=abc.ABCMeta):
    # Attributs
    namespaces = helper.XML_NAMESPACES
    namespace  = None
    
    # Méthodes spéciales
    def __init__(self, arbre):
        self.arbre = ET.fromstring(arbre)
    
    # Méthodes privées
    @abc.abstractmethod
    def _analyser(self):
        pass
    
    # Méthodes
    def find(self, element, tag, err=False):
        if self.namespace:
            elem = element.find(":".join((self.namespace, tag)), self.namespaces)
        
        else:
            elem = element.find(tag, self.namespaces)
        
        if err and (elem == None):
            raise XMLInterrupt("Pas d'element '{}' dans l'element '{}'".format(tag, element.tag), "warning")
        
        return elem
    
    def findall(self, element, tag):
        if self.namespace:
            return element.findall(":".join((self.namespace, tag)), self.namespaces)
        
        return element.findall(tag, self.namespaces)
    
    def findtext(self, element, tag, defaut=None):
        if self.namespace:
            return element.findtext(":".join((self.namespace, tag)), defaut, self.namespaces)
        
        return element.findtext(tag, defaut, self.namespaces)
    
    def iterfind(self, element, tag):
        if self.namespace:
            return element.iterfind(":".join((self.namespace, tag)), self.namespaces)
        
        return element.iterfind(tag, self.namespaces)
    
    def analyser(self):
        try:
            self._analyser()
        
        except XMLInterrupt as err:
            if hasattr(self, err.niveau):
                getattr(self, err.niveau)(err.message)
            
            else:
                self.warning(err.message)
    
    # Propriétés
    @property
    def racine(self):
        return self.arbre
