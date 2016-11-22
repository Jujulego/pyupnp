"""
Created on 25 juillet 2015

@author: julien
"""

# Erreur
class XMLErreur(Exception):
    # Méthodes spéciales
    def __init__(self, message):
        self.message = message

# Mixin
class XMLMixin():
    # Attributs
    xml_ns = {}
    
    # Méthodes
    def recupXMLElem(self, element, nom, no_erreur=False):
        e = element.find(nom, self.xml_ns)
        
        if e == None and not no_erreur:
            raise XMLErreur("Pas d'élément '{}' dans l'élément '{}'".format(nom, element.tag))
        
        return e
