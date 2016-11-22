# Classe
class CreationMixin:
    # Méthodes
    def creer_coffre(self, nom, contenu={}):
        try:
            return self.stock.ajouter_coffre(nom, contenu=contenu)
        
        except FileExistsError:
            return self.stock[nom]
    
    def creer_stock(self, nom):
        try:
            return self.stock.ajouter_stock(nom)
        
        except FileExistsError:
            return self.stock[nom]
