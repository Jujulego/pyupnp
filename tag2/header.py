# -*- coding: utf-8 -*-

# Importations:
# Tag
from .dicos import flags_header
from .classes import TagErreur
from .fonctions import verif_type

# Classe Header
class Header():
    """Classe définisant des méthodes spéciales pour les classes TagHeader et FrameHeader"""

# Méthodes spéciales:
## Attributs:
    def __delattr__(self, nom):
        raise AttributeError("Impossible de supprimer un attribut")

## Index:
    def __getitem__(self, index):
        return self._header[index]

    def __setitem__(self, index, valeur):
        raise TypeError("Interdiction de modifier le tag")

    def __delitem__(self, index):
        raise TypeError("Le header de tag doit toujours faire 10 octets")

    def __contains__(self, valeur):
        if type(valeur) is bytes:
            pass
            
        elif type(valeur) is str:
            valeur = valeur.encode()
            
        elif type(valeur) is int:
            valeur = str(valeur).encode()
            
        else:
            raise TypeError("La valeur doit être de type bytes, str ou int, et pas de type: {}".format(str(valeur.__class__)[8:-2]))
            
        return valeur in self._header

    def __len__(self):
        return len(self._header)

## Mathématiques:
    def __add__(self, ajout):
        raise TypeError("Le header de tag ne doit pas dépasser 10 octets")

    def __radd__(self, ajout):
        raise TypeError("Le header de tag ne doit pas dépasser 10 octets")

    def __iadd__(self, ajout):
        raise TypeError("Le header de tag ne doit pas dépasser 10 octets")

    def __sub__(self, enleve):
        raise TypeError("Le header de tag doit toujours faire 10 octets")

    def __rsub__(self, enleve):
        raise TypeError("Le header de tag doit toujours faire 10 octets")

    def __isub__(self, enleve):
        raise TypeError("Le header de tag doit toujours faire 10 octets")

# Classe TagHeader
class TagHeader(Header):
    """Classe contenant les résultats d'une analyse d'un header de tags:
- la version du tag :        version
- la taille totale du tag :  taille
- les drapeaux :             drapeaux
   - n°0 Désynchronisé
   - n°1 Extention de header
   - n°2 Expérimental
"""
# Méthodes spéciales:
    def __init__(self, header):
        # header doit être des bytes
        verif_type(header, 'header', bytes)
        
        self._header = header
        self._version = self.recup_version()
        self._drapeaux = self.recup_drapeaux()
        self.taille = self.recup_taille()

    def __repr__(self):
        """Représentation de l'objet TagHeader :
Header de tag (ver: {self._version})"""
        return "Header de tag (ver: {})".format(self._version)

    def __str__(self):
        """self.__str__() <==> self._header"""
        return self._header.decode('utf-8')

## Attributs:
    def __getattr__(self, nom):
        raise AttributeError("Un objet TagHeader ne contient pas l'attribut {}".format(nom))

## Logiques:
    def __eq__(self, objet):
        """h.__eq__(...) <==> h == objet
si l'objet est en bytes ou un string: h.header == objet[.encode()]"""
        if type(objet) is bytes:
            return self._header == objet
            
        elif type(objet) is str:
            return self._header == objet.encode()
            
        elif type(objet) is TagHeader:
            return self._header == objet.header
            
        else:
            return False

    def __ne__(self, objet):
        """h.__eq__(...) <==> h != objet
si l'objet est en bytes ou un string: h.header != objet[.encode()]"""
        if type(objet) is bytes:
            return self._header != objet
            
        elif type(objet) is str:
            return self._header != objet.encode()
            
        elif type(objet) is TagHeader:
            return self._header != objet.header
            
        else:
            return True

    def __gt__(self, objet):
        """h.__gt__(...) <==> h.version > objet.version
si h.version == objet.version : h.taille > objet.taille"""
        if type(objet) is not TagHeader:
            return False
            
        if self._version == objet.version:
            return self._version > objet.taille
            
        else:
            return self._version > objet.version

    def __ge__(self, objet):
        """h.__ge__(...) <==> h.version >= objet.version"""
        if type(objet) is not TagHeader:
            return False
            
        return self._version >= objet.version

    def __lt__(self, objet):
        """h.__lt__(...) <==> h.version < objet.version
si h.version == objet.version : h.taille < objet.taille"""
        if type(objet) is not TagHeader:
            return False
            
        if self._version == objet.version:
            return self._version < objet.taille
            
        else:
            return self._version < objet.version

    def __le__(self, objet):
        """h.__le__(...) <==> h.version <= objet.version"""
        if type(objet) is not TagHeader:
            return False
            
        return self._version <= objet.version

# Méthodes:
## lecture:
    def recup_drapeaux(self):
        """h.recup_drapeaux() ==> dict
Méthode analysant le 6eme octet du header pour en tirer les status des drapeaux sous forme d'un dictionnaire"""
        if self.version == 'ID3v1':
            # La version ID3v1 n'a pas de drapeaux
            return None
        
        # Récupération du dictionnaire de base
        flags = flags_header
        
        # Récupération pour analyse par bits des drapeaux
        flags_b = bin(self._header[5])[2:]
        
        # Ajustement de la longueur (8 bits)
        while len(flags_b) < 8:
            flags_b = '0' + flags_b
        
        # Modification des valeurs du dictionnaire (False par défault)
        if int(flags_b[0]):
            flags["Désynchronisé"] = True
            
        if int(flags_b[1]):
            flags["Header étendu"] = True
            self._version += " ext."
            
        if int(flags_b[2]):
            flags["Tag expérimental"] = True
            self._version += " exp."
        
        return flags

    def recup_taille(self):
        """h.recup_taille() ==> int
Méthode analysant les 4 derniers octets de header afin d'en extraire la taille totale du tag"""
        if self.version == "ID3v1":
            # Les tags ID3v1 ont une longueur constante de 128 octets
            return 128
            
        else:
            taille_b = self._header[-4:]
            i = 3
            taille = 0
            for b in taille_b:
                taille += b*pow(128, i)
                i -= 1
            return taille

    def recup_version(self):
        """h.recup_version() ==> str
Méthode analysant les 5 premiers octets du header pour en déduire la version du tag"""
        if self._header[:3].decode('utf-8') == 'TAG':
            return "ID3v1"
            
        elif self._header[:3].decode('utf-8') == 'ID3':
            if self._header[3] <= 4:
                return "ID3v2.{}.{}".format(self._header[3], self._header[4])
            else:
                raise TagErreur("La version du tag est inconnue")
        else:
            raise TagErreur("La version du tag est inconnue ou le tag est corrompu")

## écriture:
    def sauve(self):
        return self.sauve_version() + self.sauve_flags() + self.sauve_taille()
    
    def sauve_flags(self):
        flags = self.drapeaux
        
        if flags is None: # Tag ID3v1 : pas de drapeaux
            return b""
        
        flags_b = '0b'
        
        if flags["Désynchronisé"]:
            flags_b += '1'
        else:
            flags_b += '0'
        
        if flags["Header étendu"]:
            flags_b += '1'
        else:
            flags_b += '0'
        
        if flags["Tag expérimental"]:
            flags_b += '1'
        else:
            flags_b += '0'
        
        flags_b += '00000' # Longueur finale : 8 bits
            
        return int(flags_b, 0).to_bytes(1, 'big')
    
    def sauve_taille(self):
        taille = self.taille
        
        if self.version == "ID3v1": # Tag ID3v1 : taille constante (128o) non-précisée
            return b""
        
        taille_b = b""
        i = 3
        
        while i > -1:
            taille_b += (taille // pow(128, i)).to_bytes(1, 'big')
            taille %= pow(128, i)
            
            i -= 1
        
        return taille_b
    
    def sauve_version(self):
        v = self.version
        
        if v == "ID3v1":
            return b"TAG"
        
        return b"ID3" + int(v[v.find('.')+1:v.rfind('.')]).to_bytes(1, "big") + int(v[v.rfind('.')+1:]).to_bytes(1, "big")

# Propriétés:
    @property
    def drapeaux(self):
        return self._drapeaux

    @property
    def header(self):
        return self._header
    @property
    def version(self):
        return self._version
