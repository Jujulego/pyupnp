# Importations
import abc

# Classe
class BaseCommande(metaclass=abc.ABCMeta):
    '''
    Base abstraite d'une classe de commande.
    Permet de créer dynamiquement des commandes pour la ligne de commande, grâce à argparse.
    '''
    
    # Attributs
    options = {}
    arguments = []
    
    # Méthodes spéciales
    def __init__(self, parser):
        '''
        Contruit le parser.
        '''
        
        for arg in self.arguments:
            noms = arg["noms"]
            del arg["noms"]
            
            parser.add_argument(*noms, **arg)
        
        parser.set_defaults(fonction=self.executer)
        
        self.parser = parser
    
    # Méthodes
    @abc.abstractmethod
    def executer(self, args):
        raise NotImplemented
