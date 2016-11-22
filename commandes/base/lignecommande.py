# Importations
import abc
import argparse
import sys

# Classe
class BaseLigneCommande(metaclass=abc.ABCMeta):
    '''
    Objet gérant la ligne de commande.
    '''
    
    # Attributs
    arguments = []
    options = {}
    commandes = []
    
    # Méthodes spéciales
    def __init__(self):
        '''
        Crée le parser à l'aide de argparse
        '''
        
        self.parser = argparse.ArgumentParser(**self.options)
        
        for arg in self.arguments:
            noms = arg["noms"]
            del arg["noms"]
            
            self.parser.add_argument(*noms, **arg)
        
        if len(self.commandes) > 0:
            sous_parsers = self.parser.add_subparsers()
            
            for c in self.commandes:
                c(sous_parsers.add_parser(c.nom, **c.options))
    
    # Méthodes
    def lancer(self, args=None):
        try:
            args = self.parser.parse_args(sys.argv[1:] if not args else args)
            self.executer(args)
            
            sys.exit(0)
        
        except Exception as err:
            self.erreur(err)
    
    @abc.abstractmethod
    def executer(self, args):
        raise NotImplemented
    
    def erreur(self, erreur):
        raise erreur
