__all__ = ["Table"]

# Variables
operateurs = {
    "lt" : lambda val, liste: [v for v in liste if v.valeur <  val],
    "lte": lambda val, liste: [v for v in liste if v.valeur <= val],
    "eq" : lambda val, liste: [v for v in liste if v.valeur == val],
    "ne" : lambda val, liste: [v for v in liste if v.valeur != val],
    "gte": lambda val, liste: [v for v in liste if v.valeur >= val],
    "gt" : lambda val, liste: [v for v in liste if v.valeur >  val],
    
    "contain" : lambda val, liste: [v for v in liste if val in v.valeur],
    "ncontain": lambda val, liste: [v for v in liste if not vat in v.valeur],
    
    "in" : lambda val, liste: [v for v in liste if v.valeur in val],
    "nin": lambda val, liste: [v for v in liste if not v.valeur in val],
}

# Classe
class Donnee:
    # Méthodes spéciales
    def __init__(self, table, colonne, num, donnee):
        self.table = table
        self.colonne = colonne
        self.num = num
        
        self.valeur = donnee
    
    def __repr__(self):
        return "<Donnee {!r}, {}:{:d}>".format(self.table, self.colonne.nom, self.num)

class Ligne:
    # Méthodes spéciales
    def __init__(self, table, num):
        self.table = table
        self.num = num
        
        self._donnees = {}
        
        for nom in self.table:
            self._donnees[nom] = self.table[nom][num]
    
    def __repr__(self):
        return "<Ligne {!r} n°{:d}>".format(self.table, self.num)
    
    def __getitem__(self, nom):
        return self._donnees[nom]

class Colonne:
    # Méthodes spéciales
    def __init__(self, table, nom):
        self.table = table
        self.nom = nom
        
        self._donnees = {}
    
    def __repr__(self):
        return "<Colonne {!r} {}>".format(self.table, self.nom)
    
    def __len__(self):
        return len(self._donnees)
    
    def __iter__(self):
        return iter(self._donnees)
    
    def __getitem__(self, num):
        if isinstance(num, int):
            return self._donnees[num]
    
    def __setitem__(self, num, val):
        if isinstance(num, int):
            self._donnees[num] = val
    
    def __delitem__(self, num):
        if isinstance(num, int):
            del self._donnees[num]
    
    # Méthodes
    def ajouter_valeur(self, valeur, num=-1):
        if num < 0:
            num = len(self)
        
        self._donnees[num] = Donnee(self.table, self, num, valeur)
        
        return num
    
    def rechercher(self, **expressions):
        valeurs = self.donnees()
                
        for op, val in expressions.items():
            valeurs = operateurs[op](val, valeurs)
        
        return [v.num for v in valeurs]
    
    def donnees(self):
        return list(self._donnees.values())
    
    def suppr_valeur(self, num):
        del self._donnees[num]

class Table:
    # Méthodes spéciales
    def __init__(self, colonnes=[]):
        self._colonnes = {}
        
        for col in colonnes:
            self.ajouter_colonne(col)
    
    def __repr__(self):
        return "<Table {} colonnes x {} lignes>".format(len(self._colonnes), len(self.lignes()))
    
    def __getitem__(self, nom):
        if isinstance(nom, str):
            return self._colonnes[nom]
        
        elif isinstance(nom, int):
            return Ligne(self, nom)
    
    def __iter__(self):
        return iter(self._colonnes)
    
    def __len__(self):
        return len(self.lignes())
    
    def __getstate__(self):
        noms = list(self._colonnes.keys())
        
        vals = []
        for l in self.lignes():
            d = {}
            for n in noms:
                d[n] = l[n].valeur
            
            vals.append(d)
        
        return noms, vals
    
    def __setstate__(self, etat):
        noms, vals = etat
        self._colonnes = {}
        
        for n in noms:
            self.ajouter_colonne(n)
        
        for v in vals:
            self.ajouter_valeurs(**v)
    
    # Méthodes
    def ajouter_colonne(self, nom, defaut=None):
        if nom in self._colonnes:
            return
        
        col = self._colonnes[nom] = Colonne(self, nom)
        
        for _ in range(len(list(self._colonnes.values())[0])):
            col.ajouter_valeur(defaut)
    
    def ajouter_valeurs(self, _num=-1, **valeurs):
        for nom, col in self._colonnes.items():
            val = None
            
            if nom in valeurs:
                val = valeurs[nom]
            
            _num = col.ajouter_valeur(val, _num)
        
        return _num
    
    def lignes(self):
        return [Ligne(self, n) for n in range(len(list(self._colonnes.values())[0]))]
    
    def rechercher(self, **expressions):
        exprs = {}
        
        for op, val in expressions.items():
            op += "__"
            
            nom = op.split("__")[0]
            op  = op.split("__")[1] or "eq"
            
            if nom in exprs:
                exprs[nom][op] = val
            
            else:
                exprs[nom] = {op: val}
        
        results = {}
        
        for nom, expr in exprs.items():
            nums = self[nom].rechercher(**expr)
            
            for n in results:
                results[n] &= (n in nums)
            
            if len(results) == 0:
                for n in nums:
                    if not n in results:
                        results[n] = True
            
            if len(results) == 0:
                break
        
        return [Ligne(self, n) for n, t in results.items() if t]
    
    def suppr_ligne(self, num):
        for nom in self:
            self[nom].suppr_valeur(num)
