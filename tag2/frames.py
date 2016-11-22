# -*- coding: utf-8 -*-

# Importations
# Tag
from .classes import FrameErreur, FrameErreurFatale, StopFrameIteration, MyDate
from .dicos import encodages, flags_frameheader, flags_id3v2, type_images
from .fonctions import verif_type, get_key_from_item_dict, anal_tcon, anal_tkey, sauve_tkey, anal_tmed, sauve_tmed
from .header import Header

# Python (systeme)
import re
from datetime import timedelta, time

# Classe de base (héritage)
class FrameHerit():
# Méthodes spéciales:
    def __eq__(self, objet):
        if issubclass(type(objet), FrameHerit):
            return self.id_frame == objet.id_frame
        
        return False
    
    def __ne__(self, objet):
        if issubclass(type(objet), FrameHerit):
            return self.id_frame != objet.id_frame
        
        return False

    def __gt__(self, objet):
        if issubclass(type(objet), FrameHerit):
            return self.id_frame > objet.id_frame
        
        return False

    def __ge__(self, objet):
        if issubclass(type(objet), FrameHerit):
            return self.id_frame >= objet.id_frame
        
        return False

    def __lt__(self, objet):
        if issubclass(type(objet), FrameHerit):
            return self.id_frame < objet.id_frame
        
        return False

    def __le__(self, objet):
        if issubclass(type(objet), FrameHerit):
            return self.id_frame <= objet.id_frame
        
        return False

# Propriétés:
    @property
    def header(self):
        return self._header

    @property
    def id_frame(self):
        return self.header.id_frame

    @property
    def taille(self):
        return self.header.taille
    
    @taille.setter
    def taille(self, ntaille):
        self.header.taille = ntaille

    @property
    def type_frame(self):
        return self.header.type

# classe FrameHeader
class FrameHeader(Header, FrameHerit):
    """Classe contenant d'une analyse de header de tag (frame):
- l'identifiant du tag :     id_frame
- le type d'information :    type_frame
- la taille du tag :         taille
- les drapeaux :             drapeaux
    - n°0 Préservation du tag si il est altéré
    - n°1 Préservation du tag si le fichier est altéré
    - n°2 Lecture seule du tag
    - n°3 Compression
    - n°4 Cryptage
    - n°5 Identifiant de groupe
"""

# Méthodes spéciales:
## générales:
    def __init__(self, header, version_tag):
        # Récupération et vérification du header
        verif_type(header, 'header', bytes)
        self._header = header
        
        # Si le header est une suite d'octets nuls fin de la boucle
        if header[:4] == b"\x00\x00\x00\x00":
            raise StopFrameIteration
        
        # Récupération de l'identifiant
        try:
            self._id = header[:4].decode('utf-8')
        except UnicodeDecodeError:
            raise FrameErreurFatale("Le tag {frame} est altéré".format(frame=self.header))
            
        # Récupération du type de contenu du frame
        if not self._id in flags_id3v2:
            raise FrameErreurFatale("L'identifiant de tag: {} est inconnu".format(self.id_frame))
            
        self._type = flags_id3v2[self._id]
        
        # Récupération de la taille du frame
        if "ID3v2.4" in version_tag:
            self._taille = self.recup_taille()
        else:
            self._taille = int.from_bytes(self.header[4:8], "big") + 10
        
        # Récupérationdes drapeaux
        self._drapeaux = self.recup_drapeaux()
        
        self._version_tag = version_tag

    def __repr__(self):
        return "Header de tag (ID: '{}')".format(self.id_frame)

    def __str__(self):
        return self._header


## Attributs:
    def __delattr__(self, nom):
        raise AttributeError("Impossible de supprimer un attribut")

# Méthodes
# - lecture
    def recup_drapeaux(self):
        """h.recup_drapeaux() ==> dict
Méthode analysant les 2 derniers octets du header pour en tirer les status des drapeaux sous forme d'un dictionnaire"""
        # Récupération du dictionnaire
        flags = flags_frameheader
        
        # Récupération des bits contenant la 1ere série de drapeaux (8e octet)
        flags_b = bin(self._header[8])[2:]
        
        while len(flags_b) < 8:
            flags_b = '0' + flags_b
        if int(flags_b[0]):
            flags["Altération du tag"] = True
        if int(flags_b[1]):
            flags["Altération du fichier"] = True
        if int(flags_b[2]):
            flags["Lecture seule"] = True
        
        # Récupération des bits contenant la 2nd série de drapeaux (9e octet)
        flags_b = bin(self._header[9])[2:]
        
        while len(flags_b) < 8:
            flags_b = '0' + flags_b
        if int(flags_b[0]):
            flags["Compression (zlib)"] = True
        if int(flags_b[1]):
            flags["Chiffrage"] = True
        if int(flags_b[2]):
            flags["Identifiant de groupe"] = True
            
        return flags

    def recup_taille(self):
        """h.recup_taille() ==> int
Méthode analysant les 5, 6, 7 et 8eme octets de header afin d'en extraire la taille totale du tag"""
        taille = 0
        i = 3
        for b in self.header[4:8]:
            taille += b*pow(128, i)
            i -= 1
        return taille + 10

# - écriture
    def sauve(self):
        return bytes(self.id_frame, 'utf-8') + self.sauve_taille() + self.sauve_drapeaux()
    
    def sauve_drapeaux(self):
        flags = self.drapeaux
        
        if flags is None: # Tag ID3v1 : pas de drapeaux
            return b""
        
        flags_b = '0b'
        
        if flags["Altération du tag"]:
            flags_b += '1'
        else:
            flags_b += '0'
        
        if flags["Altération du fichier"]:
            flags_b += '1'
        else:
            flags_b += '0'
        
        if flags["Lecture seule"]:
            flags_b += '1'
        else:
            flags_b += '0'
        
        flags_b += '00000'
        
        if flags["Compression (zlib)"]:
            flags_b += '1'
        else:
            flags_b += '0'
        
        if flags["Chiffrage"]:
            flags_b += '1'
        else:
            flags_b += '0'
        
        if flags["Identifiant de groupe"]:
            flags_b += '1'
        else:
            flags_b += '0'
        
        flags_b += '00000' # Longueur finale : 16 bits
            
        return int(flags_b, 0).to_bytes(2, 'big')
    
    def sauve_taille(self):
        taille = self.taille - 10
        
        if "ID3v2.4" in self._version_tag:
            taille_b = b""
            i = 3
        
            while i > -1:
                taille_b += (taille // pow(128, i)).to_bytes(1, 'big')
                taille %= pow(128, i)
            
                i -= 1
        
            return taille_b
        
        return taille.to_bytes(4, 'big')

# Propriétés:
    @property
    def drapeaux(self):
        return self._drapeaux

    @property
    def id_frame(self):
        return self._id

    @property
    def taille(self):
        return self._taille
    
    @taille.setter
    def taille(self, ntaille):
        self._taille = ntaille

# Dictionnaire identifiant => (regex, fonction d'analyse)
regex_text = {
        "TALB": (re.compile(b"^TALB.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TBPM": (re.compile(b"^TBPM.{6}(?P<encodage>.)(?P<valeur>[0-9]+).*$", re.DOTALL),    lambda t, e: int(t)),
        "TCOM": (re.compile(b"^TCOM.{6}(?P<encodage>.)(?P<valeur>.+/?)+.*$", re.DOTALL),    lambda t, e: t.decode(e).split('/')),
        "TCON": (re.compile(b"^TCON.{6}(?P<encodage>.)(?P<valeur>\({0,2}.+\)?)+.*$", re.DOTALL), anal_tcon),
        "TCOP": (re.compile(b"^TCOP.{6}(?P<encodage>.)(?P<valeur>[0-9]{,4}.*).*$", re.DOTALL),    lambda t, e: (int(t[:4]), t[4:].decode(e))),
        "TDAT": (re.compile(b"^TDAT.{6}(?P<encodage>.)(?P<valeur>([0-9]{2}){2}).*$", re.DOTALL),lambda t, e: MyDate(int(t[2:]), int(t[:2]))),
        "TDLY": (re.compile(b"^TDLY.{6}(?P<encodage>.)(?P<valeur>[0-9]+).*$", re.DOTALL),     lambda t, e: time(microsecond=int(t) * 1000)),
        "TDRC": (re.compile(b"^TDRC.{6}(?P<encodage>.)(?P<valeur>[0-9]{4}).*$", re.DOTALL),    lambda t, e: int(t)),
        "TENC": (re.compile(b"^TENC.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TEXT": (re.compile(b"^TEXT.{6}(?P<encodage>.)(?P<valeur>.+/?)+.*$", re.DOTALL),    lambda t, e: t.decode(e).split('/')),
        "TFLT": (re.compile(b"^TFLT.{6}(?P<encodage>.)(?P<valeur>(MPG)|(VQF)|(PCM)|/(([1-3](.5)?)|(AAC))|([^\x00]+)).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "TIME": (re.compile(b"^TIME.{6}(?P<encodage>.)(?P<valeur>([0-9]{2}){2}).*$", re.DOTALL),lambda t, e: time(hour=int(t[:2]), minute=int(t[2:]))),
        "TIT1": (re.compile(b"^TIT1.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TIT2": (re.compile(b"^TIT2.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TIT3": (re.compile(b"^TIT3.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TKEY": (re.compile(b"^TKEY.{6}(?P<encodage>.)(?P<valeur>([A-G][#b]?[m]?)|o).*$", re.DOTALL), anal_tkey),
        "TLAN": (re.compile(b"^TLAN.{6}(?P<encodage>.)(?P<valeur>([^\x00]{3}\x00)+).*$", re.DOTALL), lambda t, e: t.decode()),
        "TLEN": (re.compile(b"^TLEN.{6}(?P<encodage>.)(?P<valeur>[0-9]+).*$", re.DOTALL),    lambda t, e: timedelta(milliseconds=int(t))),
        "TMED": (re.compile(b"^TMED.{6}(?P<encodage>.)(?P<valeur>(\({0,2}(DIG(/A)?)|(ANA(/(WAC)|(8CA)){0,2})|(ANA(/(A)|(DD)|(AD)|(AA)){0,4})|(LD(/A)?)|(TT(/(33)|(45)|(71)|(76)|(78)|(80)){0,6})|(MD(/A)?)|(DAT(/[A1-6]){0,7})|(DCC(/A)?)|(DVD(/A)?)|(TV(/(PAL)|(NTSC)|(SECAM)){0,3})|(VID(/(PAL)|(NTSC)|(SECAM)|(VHS)|(SVHS)|(BETA)){0,6})|(RAD(/(FM)|(AM)|(LW)|(MW)){0,4})|(TEL(/I)?)|(MC(/(4)|(9)|(I{0,3})|(IV)){0,6})|(REE(/(9)|(19)|(38)|(76)|(I{0,3})|(IV)){0,8})\)?)*[^\x00]*)+.*$", re.DOTALL),        anal_tmed),
        "TOAL": (re.compile(b"^TOAL.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TOFN": (re.compile(b"^TOFN.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TOLY": (re.compile(b"^TOLY.{6}(?P<encodage>.)(?P<valeur>.+/?)+.*$", re.DOTALL),    lambda t, e: t.decode(e).split('/')),
        "TOPE": (re.compile(b"^TOPE.{6}(?P<encodage>.)(?P<valeur>.+/?)+.*$", re.DOTALL),    lambda t, e: t.decode(e).split('/')),
        "TORY": (re.compile(b"^TORY.{6}(?P<encodage>.)(?P<valeur>[0-9]{4}).*$", re.DOTALL),    lambda t, e: int(t)),
        "TOWN": (re.compile(b"^TOWN.{6}(?P<encodage>.)(?P<valeur>.+)+.*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TPE1": (re.compile(b"^TPE1.{6}(?P<encodage>.)(?P<valeur>.+/?)+.*$", re.DOTALL),    lambda t, e: t.decode(e).split('/')),
        "TPE2": (re.compile(b"^TPE2.{6}(?P<encodage>.)(?P<valeur>.+)+.*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TPE3": (re.compile(b"^TPE3.{6}(?P<encodage>.)(?P<valeur>.+)+.*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TPE4": (re.compile(b"^TPE4.{6}(?P<encodage>.)(?P<valeur>.+)+.*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TPOS": (re.compile(b"^TPOS.{6}(?P<encodage>.)(?P<valeur>[0-9]+(/[0-9]+)?).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "TPUB": (re.compile(b"^TPUB.{6}(?P<encodage>.)(?P<valeur>.+)+.*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TRCK": (re.compile(b"^TRCK.{6}(?P<encodage>.)(?P<valeur>[0-9]+(/[0-9]+)?).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "TRDA": (re.compile(b"^TRDA.{6}(?P<encodage>.)(?P<valeur>.+)+.*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TRSN": (re.compile(b"^TRSN.{6}(?P<encodage>.)(?P<valeur>.+)+.*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TRSO": (re.compile(b"^TRSO.{6}(?P<encodage>.)(?P<valeur>.+)+.*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TSIZ": (re.compile(b"^TSIZ.{6}(?P<encodage>.)(?P<valeur>[0-9]+).*$", re.DOTALL),    lambda t, e: int(t)),
        "TSRC": (re.compile(b"^TSRC.{6}(?P<encodage>.)(?P<valeur>.{12}).*$", re.DOTALL),    lambda t, e: t),
        "TSSE": (re.compile(b"^TSSE.{6}(?P<encodage>.)(?P<valeur>.+)+.*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TSOA": (re.compile(b"^TSOA.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TSOP": (re.compile(b"^TSOP.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TSO2": (re.compile(b"^TSO2.{6}(?P<encodage>.)(?P<valeur>.+).*$", re.DOTALL),        lambda t, e: t.decode(e)),
        "TYER": (re.compile(b"^TYER.{6}(?P<encodage>.)(?P<valeur>[0-9]{4}).*$", re.DOTALL),    lambda t, e: int(t)),
        "TXXX": (re.compile(b"^TXXX.{6}(?P<encodage>.)(?P<description>.+?)\x00+(?P<valeur>.+).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "COMM": (re.compile(b"^COMM.{6}(?P<encodage>.)(?P<langue>.{3})(?P<description>.*?)\x00+(?P<valeur>.+).*$", re.DOTALL), lambda t, e: t.decode(e))}

regex_url = {    "WCOM": (re.compile(b"^WCOM.{6}(?P<url>[^\x00]+).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "WCOP": (re.compile(b"^WCOP.{6}(?P<url>[^\x00]+).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "WOAF": (re.compile(b"^WOAF.{6}(?P<url>[^\x00]+).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "WOAR": (re.compile(b"^WOAR.{6}(?P<url>[^\x00]+).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "WOAS": (re.compile(b"^WOAS.{6}(?P<url>[^\x00]+).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "WORS": (re.compile(b"^WORS.{6}(?P<url>[^\x00]+).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "WPAY": (re.compile(b"^WPAY.{6}(?P<url>[^\x00]+).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "WPUB": (re.compile(b"^WPUB.{6}(?P<url>[^\x00]+).*$", re.DOTALL), lambda t, e: t.decode(e)),
        "WXXX": (re.compile(b"^WXXX.{6}(?P<encodage>.)(?P<description>[^\x00]+)\x00(?P<url>[^\x00]+).*$", re.DOTALL), lambda t, e: t.decode(e))}

regex_autres = {"AENC": (re.compile(b"^AENC.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "APIC": (re.compile(b"^APIC.{6}(?P<encodage>.)(?P<MIME_type>[^\x00]+)\x00(?P<type_image>[\x00-\x14])(?P<description>[^\x00]*?)\x00(?P<image>((\xff\xd8)|(\x89PNG)).*)$", re.DOTALL), None),
        "COMR": (re.compile(b"^COMR.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "ENCR": (re.compile(b"^ENCR.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "EQUA": (re.compile(b"^EQUA.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "ETCO": (re.compile(b"^ETCO.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "GEOB": (re.compile(b"^GEOB.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "GRID": (re.compile(b"^GRID.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "IPLS": (re.compile(b"^IPLS.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "LINK": (re.compile(b"^LINK.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "MCDI": (re.compile(b"^MCDI.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "MLLT": (re.compile(b"^MLLT.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "OWNE": (re.compile(b"^OWNE.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "PRIV": (re.compile(b"^PRIV.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "PCNT": (re.compile(b"^PCNT.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "POPM": (re.compile(b"^POPM.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "POSS": (re.compile(b"^POSS.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "RBUF": (re.compile(b"^RBUF.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "RVAD": (re.compile(b"^RVAD.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "RVRB": (re.compile(b"^RVRB.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "SYLT": (re.compile(b"^SYLT.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "SYTC": (re.compile(b"^SYTC.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "UFID": (re.compile(b"^UFID.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "USER": (re.compile(b"^USER.{6}(?P<valeur>.*)$", re.DOTALL), None),
        "USLT": (re.compile(b"^USLT.{6}(?P<valeur>.*)$", re.DOTALL), None)}

# dicos associant des ids de tags aux fonctions de retour en forme bytes (sauvegarde)
sauve_frames = {"AENC": lambda v: v,
        "APIC": lambda e, m, t, d, v: get_key_from_item_dict(encodages, e) + bytes(m, e) + b"\x00" + int(get_key_from_item_dict(type_images, t), 0).to_bytes(1, 'big') + bytes(d, e) + b"\x00" + v,
        "COMM": lambda e, l, d, v: get_key_from_item_dict(encodages, e) + bytes(d, "iso-8859-1") + bytes(d, e) + b"\x00" + bytes(v, e),
        "COMR": lambda v: v,
        "ENCR": lambda v: v,
        "EQUA": lambda v: v,
        "ETCO": lambda v: v,
        "GEOB": lambda v: v,
        "GRID": lambda v: v,
        "IPLS": lambda v: v,
        "LINK": lambda v: v,
        "MCDI": lambda v: v,
        "MLLT": lambda v: v,
        "OWNE": lambda v: v,
        "PRIV": lambda v: v,
        "PCNT": lambda v: v,
        "POPM": lambda v: v,
        "POSS": lambda v: v,
        "RBUF": lambda v: v,
        "RVAD": lambda v: v,
        "RVRB": lambda v: v,
        "SYLT": lambda v: v,
        "SYTC": lambda v: v,
        "TALB": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TBPM": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(str(v), 'utf-8'),
        "TCOM": lambda e, v: get_key_from_item_dict(encodages, e) + bytes('/'.join(v), e),
        "TCON": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TCOP": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TDAT": lambda e, v: get_key_from_item_dict(encodages, e) + v.vers_bytes(),
        "TDLY": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(str(v), 'utf-8'),
        "TDRC": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(str(v), 'utf-8'),
        "TENC": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TEXT": lambda e, v: get_key_from_item_dict(encodages, e) + bytes('/'.join(v), e),
        "TFLT": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TIME": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(str(v.microsecond / 1000), 'big'),
        "TIT1": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TIT2": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TIT3": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TKEY": lambda e, v: get_key_from_item_dict(encodages, e) + sauve_tkey(v, e),
        "TLAN": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TLEN": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(str(v), 'utf-8'),
        "TMED": lambda e, v: get_key_from_item_dict(encodages, e) + sauve_tmed(v, e),
        "TOAL": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TOFN": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TOLY": lambda e, v: get_key_from_item_dict(encodages, e) + bytes('/'.join(v), e),
        "TOPE": lambda e, v: get_key_from_item_dict(encodages, e) + bytes('/'.join(v), e),
        "TORY": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(str(v), 'utf-8'),
        "TOWN": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TPE1": lambda e, v: get_key_from_item_dict(encodages, e) + bytes('/'.join(v), e),
        "TPE2": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TPE3": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TEP4": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TPOS": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TPUB": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TRCK": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TRDA": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TRSN": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TRSO": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TSIZ": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(str(v), 'utf-8'),
        "TSRC": lambda e, v: get_key_from_item_dict(encodages, e) + v,
        "TSSE": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TSOA": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TSOP": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TSO2": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(v, e),
        "TYER": lambda e, v: get_key_from_item_dict(encodages, e) + bytes(str(v), 'utf-8'),
        "TXXX": lambda e, d, v: get_key_from_item_dict(encodages, e) + bytes(d, e) + b"\x00" + bytes(v, e),
        "UFID": lambda v: v,
        "USER": lambda v: v,
        "USLT": lambda v: v,
        "WCOM": lambda v: bytes(v, 'utf-8'),
        "WCOP": lambda v: bytes(v, 'utf-8'),
        "WOAF": lambda v: bytes(v, 'utf-8'),
        "WOAR": lambda v: bytes(v, 'utf-8'),
        "WOAS": lambda v: bytes(v, 'utf-8'),
        "WORS": lambda v: bytes(v, 'utf-8'),
        "WPAY": lambda v: bytes(v, 'utf-8'),
        "WPUB": lambda v: bytes(v, 'utf-8'),
        "WXXX": lambda e, d, v: get_key_from_item_dict(encodages, e) + bytes(d, e) + b"\x00" + bytes(v, 'utf-8')}

# classes Frames
# FrameText:
class FrameText(FrameHerit):
    """Classe Frame pour les frames textuelles"""

# Méthodes spéciales:
    def __init__(self, tag, header):
        verif_type(tag, 'tag', bytes)
        verif_type(header, 'header', FrameHeader)
        
        self._header = header
        
        valeurs = regex_text[self.id_frame][0].match(tag)
        
        if valeurs == None:
            raise FrameErreur("Type de l'erreur: Le tag ne correspond pas à l'expression régulière\nTag {id_tag}".format(id_tag=self.id_frame))
            
        self._encodage = self.recup_encodage(valeurs.group('encodage'))
        
        if self.id_frame == "TXXX":
            self._valeur = regex_text[self.id_frame][1](valeurs.group('valeur'), self.encodage)
            
            # Nouvelles méthodes
            def sauve_long(self, encod=None, desc=None, val=None):
                if not encod:
                    encod = self.encodage
                    
                if not desc:
                    desc = self.description
                    
                if not val:
                    val = self.val
                
                return len(sauve_frames[self.id_frame](encod, desc, val))
            
            # Nouvelles propriétés
            def _get_description(self):
                return self._description
            
            def _set_description(self, ndesc):
                verif_type(ndesc, 'ndesc', str)
                
                self.taille += self.sauve_long(desc = ndesc) - self.sauve_long()
                self._description = ndesc
                
            FrameText._get_description = _get_description
            FrameText._set_description = _set_description
            FrameText.description = property(_get_description)
            
            self._description = regex_text[self.id_frame][1](valeurs.group('description'), self.encodage)
            
        elif self.id_frame == "COMM":
            self._valeur = regex_text[self.id_frame][1](valeurs.group('valeur'), self.encodage)
            
            # Nouvelles méthodes
            def sauve_long(self, encod=None, lang=None, desc=None, val=None):
                if not encod:
                    encod = self.encodage
                    
                if not lang:
                    lang = self.langue
                    
                if not desc:
                    desc = self.description
                    
                if not val:
                    val = self.val
                
                return len(sauve_frames[self.id_frame](encod, lang, desc, val))
            
            # Nouvelles propriétés
            def _get_description(self):
                return self._description
            
            def _set_description(self, ndesc):
                verif_type(ndesc, 'ndesc', str)
                
                self.taille += self.sauve_long(desc = ndesc) - self.sauve_long()
                self._description = ndesc
            
            FrameText._get_description = _get_description
            FrameText._set_description = _set_description
            FrameText.description = property(_get_description, _set_description)
            
            def _get_langue(self):
                return self._langue
            
            def _set_langue(self, nlang):
                verif_type(nlang, 'nlang', str)
                
                if len(nlang) != 3:
                    raise ValueError("Le paramètre langue doit meusurer 3 charactères")
                
                self.taille += self.sauve_long(lang = nlang) - self.sauve_lang()
                self._langue = nlang
            
            FrameText._get_langue = _get_langue
            FrameText._set_langue = _set_langue
            FrameText.langue = property(_get_langue, _set_langue)
            
            self._description = regex_text[self.id_frame][1](valeurs.group('description'), self.encodage)
            self._langue = valeurs.group('langue').decode("iso-8859-1")
        else:
            self._valeur = regex_text[self.id_frame][1](valeurs.group('valeur'), self.encodage)

# Méthodes:
    def sauve(self):
        if self.id_frame == "COMM":
            data = sauve_frames[self.id_frame](self.encodage, self.langue, self.description, self.valeur)
        
        elif self.id_frame == "TXXX":
            data = sauve_frames[self.id_frame](self.encodage, self.description, self.valeur)
        
        else:
            data = sauve_frames[self.id_frame](self.encodage, self.valeur)
        
        if len(data) != self.taille - 10:
            self.taille = len(data) + 10
        
        return self.header.sauve() + data
    
    def sauve_long(self, encod=None, val=None):
        if not encod:
            encod = self.encodage
            
        if not val:
            val = self.valeur
            
        return len(sauve_frames[self.id_frame](encod, val))
    
    def recup_encodage(self, encodage):
        verif_type(encodage, 'encodage', bytes)
        
        return encodages[encodage]

# Propriétés:
    @property
    def encodage(self):
        return self._encodage
        
    @encodage.setter
    def encodage(self, nencod):
        verif_type(nencod, 'nencod', str, bytes)
        
        if type(nencod) == bytes:
            nencod = encodages[nencod]
        
        elif not nencod in encodages.values():
                raise ValueError("Encodage {} non-supporté".format(nencod))
        
        self.taille += self.sauve_long(encod = nencod) - self.sauve_long()
        self._encodage = nencod

    @property
    def valeur(self):
        return self._valeur
    
    @valeur.setter
    def valeur(self, nval):
        verif_type(nval, 'nval', type(self._valeur))
        
        self.taille += self.sauve_long(val = nval) - self.sauve_long()
        self._valeur = nval

# FrameImage:
class FrameImage(FrameHerit):
    """Classe Frame pour les images attachées"""

# Méthodes spéciales:
    def __init__(self, tag, header):
        verif_type(tag, 'tag', bytes)
        verif_type(header, 'header', FrameHeader)
        
        self._header = header
        
        valeurs = regex_autres[self.id_frame][0].match(tag)
        
        if valeurs == None:
            raise FrameErreur("Type de l'erreur: Le tag ne correspond pas à l'expression régulière\nTag {id_tag}".format(id_tag=self.id_frame))
            
        self._encodage = self.recup_encodage(valeurs.group("encodage"))
        self._MIME_type = valeurs.group("MIME_type").decode(self.encodage)
        self._type_image = type_images[hex(int.from_bytes(valeurs.group("type_image"), 'little'))]
        try:
            self._description = valeurs.group("description").decode(self.encodage)
        except:
            self._description = ""
        self._image = valeurs.group("image")

# Méthodes:
    def sauve(self):
        data = sauve_frames["APIC"](self.encodage, self.MIME_type, self.type_image, self.description, self.image)
        
        if len(data) != self.taille - 10:
            self.taille = len(data) + 10
        
        return self.header.sauve() + data
    
    def sauve_long(self, encod=None, mime=None, timg=None, desc=None, img=None):
        if not encod:
            encod = self.encodage
            
        if not mime:
            mime = self.MIME_type
            
        if not timg:
            timg = self.type_image
            
        if not desc:
            desc = self.description
            
        if not img:
            img = self.image
            
        return len(sauve_frames["APIC"](encod, mime, timg, desc, img))
    
    def extraire_image(self, nom_fic):
        verif_type(nom_fic, 'nom_fic', str)
        from os import path
        if path.isfile(nom_fic):
            raise FileExistsError("Le fichier {} existe déjà".format(nom_fic))
        with open(nom_fic, "wb") as f:
            f.write(self.image)

    def recup_encodage(self, encodage):
        verif_type(encodage, 'encodage', bytes)
        if not encodage in encodages:
            return encodage
        else:
            return encodages[encodage]

# Propriétés:
    @property
    def encodage(self):
        return self._encodage
        
    @encodage.setter
    def encodage(self, nencod):
        verif_type(nencod, 'nencod', str, bytes)
        
        if type(nencod) == bytes:
            nencod = encodages[nencod]
        
        elif not nencod in encodages.values():
            raise ValueError("Encodage {} non-supporté".format(nencod))
        
        self.taille += self.sauve_long(encod = nencod) - self.sauve_long()
        self._encodage = nencod

    @property
    def MIME_type(self):
        return self._MIME_type
        
    @MIME_type.setter
    def MIME_type(self, nmime):
        verif_type(nmime, 'nmime', str)
        
        self.taille += self.sauve_long(mime = nmime) - self.sauve_long()
        self._MIME_type = nmime

    @property
    def type_image(self):
        return self._type_image
        
    @type_image.setter
    def type_image(self, ntimg):
        verif_type(ntimg, 'ntimg', str, int)
        
        if type(ntimg) == int:
            ntimg = hex(ntimg)
        
        if ntimg[:2] == "0x":
            ntimg = type_images[ntimg]
        elif not ntimg in type_images.values():
            raise ValueError("Type d'image {} inconnu".format(ntimg))
        
        self.taille += self.sauve_long(timg = ntimg) - self.sauve_long()
        self._type_image = ntimg

    @property
    def description(self):
        return self._description
        
    @description.setter
    def description(self, ndesc):
        verif_type(ndesc, 'ndesc', str)
        
        self.taille += self.sauve_long(desc = ndesc) - self.sauve_long()
        self._description = ndesc

    @property
    def image(self):
        return self._image
        
    @image.setter
    def image(self, nimg):
        verif_type(nimg, 'nimg', bytes)
        
        self.taille += self.sauve_long(img = nimg) - self.sauve_long()
        self._image = nimg

# FrameURL:
class FrameURL(FrameHerit):
    """Classe Frame pour les URL"""

# Méthodes spéciales:
    def __init__(self, tag, header):
        verif_type(tag, 'tag', bytes)
        verif_type(header, 'header', FrameHeader)
        
        self._header = header
        
        valeurs = regex_url[self.id_frame][0].match(tag)
        
        if valeurs == None:
            raise FrameErreur("Type de l'erreur: Le tag ne correspond pas à l'expression régulière\nTag {id_tag}".format(id_tag=self.id_frame))
            
        if self.id_frame == "WXXX":
            self._url = regex_text[self.id_frame][1](valeurs.group('url'), self.encodage)

            # Définition de la méthode recup_encodage pour le nouvel attribut encodage, présent que pour le frame WXXX
            def recup_encodage(self, encodage):
                verif_type(encodage, 'encodage', bytes)
                if not encodage in encodages:
                    return encodage
                else:
                    return encodages[encodage]
            
            FrameURL.recup_encodage = recup_encodage
            
            # La présence de valeurs supplémentaire necéssite une modification de sauve_long
            def sauve_long(self, encod=None, desc=None, url=None):
                if not encod:
                    encod = self.encodage
                    
                if not desc:
                    desc = self.description
                    
                if not url:
                    url = self.url
                    
                return len(sauve_frames[self.id_frame](encod, desc, url))
            
            FrameURL.sauve_long = sauve_long

            # Définition de propriétés pour les attributs description et encodage
            def _get_description(self):
                return self._description
            
            def _set_description(self, ndesc):
                verif_type(ndesc, 'ndesc', str)
                
                self.taille += self.sauve_long(desc = ndesc) - self.sauve_long()
                self._description = ndesc
            
            FrameURL._get_description = _get_description
            FrameURL._set_description = _set_description
            FrameURL.description = property(_get_description, _set_description)
            
            def _get_encodage(self):
                return self._encodage
            
            def _set_encodage(self, nencod):
                verif_type(nencod, 'nencod', str, bytes)
                
                if type(nencod) == bytes:
                    nencod = encodages[nencod]
                
                elif not nencod in encodages.values():
                    raise ValueError("Encodage {} non-supporté".format(nencod))
                
                self.taille += self.sauve_long(encod = nencod) - self.sauve_long()
                self._encodage = nencod
            
            FrameURL._get_encodage = _get_encodage
            FrameURL._set_encodage = _set_encodage
            FrameURL.encodage = property(_get_encodage, _set_encodage)
            
            self._encodage = self.recup_encodage(valeurs.group('encodage'))
            self._description = regex_text[self.id_frame][1](valeurs.group('description'), self.encodage)
        else:
            self._url = regex_text[self.id_frame][1](valeurs.group('url'), self.encodage)

# Méthodes :
    def sauve(self):
        if self.id_frame == "WXXX":
            data = sauve_frames[self.id_frame](self.encodage, self.description, self.url)
        else:
            data = sauve_frames[self.id_frame](self.url)
        
        if len(data) != self.taille - 10:
            self.taille = len(data) + 10
        
        return self.header.sauve() + data
    
    def sauve_long(self, url=None):
        if not url:
            url = self.url
            
        return len(sauve_frames[self.id_frame](url))

# Propriétés:
    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, nurl):
        verif_type(nurl, 'nurl', str)
        
        self.taille += self.sauve_long(url = nurl) - self.sauve_long()
        self._url = nurl

# FrameAutre:
class FrameAutre(FrameHerit):
    """Classe pour les autres Frames"""

# Méthode spéciales:
    def __init__(self, tag, header):
        verif_type(tag, 'tag', bytes)
        verif_type(header, 'header', FrameHeader)
        
        self._header = header
        
        valeurs = regex_autres[self.id_frame][0].match(tag)
        
        if valeurs == None:
            raise FrameErreur("Type de l'erreur: Le tag ne correspond pas à l'expression régulière\nTag {id_tag}".format(id_tag=self.id_frame))
            
        self._valeur = valeurs.group('valeur')

# Méthodes :
    def sauve(self):
        data = sauve_frames[self.id_frame](self.valeur)
        
        if len(data) != self.taille - 10:
            self.taille = len(data) + 10
        
        return self.header.sauve() + data
    
    def sauve_long(self, val=None):
        if not val:
            val = self.valeur
        
        return len(sauve_frames[self.id_frame](val))
    
# Propriétés:
    @property
    def valeur(self):
        return self._valeur
    
    @valeur.setter
    def valeur(self, nval):
        verif_type(nval, 'nval', bytes)
        
        self.taille += self.sauve_long(val=nval) - self.sauve_long()
        self._valeur = nval

# Génération de frames
def frame_generator(id_frame, version, v, e="utf-8", d="", m=None, t="Couverture (avant)", l="fra"):
    """Génère un objet frame.
frame_generator(id_frame, version, v, e="utf-8", d="", m=None, t="Couverture (avant)", l="fra") => sous-classe de FrameHerit

id_frame => identifiant du tag à générer
version => version de tag (ex: 'ID3v2.3')
v => valeur du frame
e => encodage (pour frames contenant des informations textuelles)
d => description (pour APIC, COMM, TXXX et WXXX)
m => type MIME (d'image pour APIC)
t => type image (valeur de tag.dicos.type_images, pour APIC)
l => langue (longueur 3 charactères, pour COMM)"""

    if not id_frame in flags_id3v2.keys():
        raise ValueError("Frame {} inconnu".format(id_frame))
    
    if 'ID3v1' in version:
        raise ValueError("Impossible de générer des tags en version 1")
    
    donnees = {}
    
    if not v:
        raise AttributeError("La génération d'un frame nécessite au moins une valeur (attribut v)")
    else:
        if not id_frame[0] in ['T', 'W'] and not id_frame in ['APIC', 'COMM'] and type(v) is str:
            v = bytes(v, 'utf-8')
            print("s > b")
        donnees['v'] = v
    
    if (id_frame[0] == 'T' or id_frame in ['APIC', 'COMM', 'WXXX']):
        if not e in encodages.values():
            raise ValueError("L'encodage {} n'est pas supporté".format(e))
        else:
            donnees['e'] = e
    
    if id_frame in ['APIC', 'COMM', 'WXXX', 'TXXX']:
        donnees['d'] = d
    
    if id_frame == 'APIC':
        if not m:
            raise AttributeError("La génération d'un frame APIC nécessite un type MIME (attribut m)")
        elif not m[:6] == "image/":
            raise AttributeError("La génération d'un frame APIC nécessite un type MIME d'image (commençant par 'image/')")
        else:
            donnees['m'] = m
    
    if id_frame == 'APIC':
        if not t in type_images.values():
            raise ValueError("Type d'image {} inconnu".format(t))
        else:
            donnees['t'] = t
    
    if id_frame == 'COMM':
        if len(l) != 3:
            raise ValueError("La valeur de l doit meusurer 3 charactères")
        else:
            donnees['l'] = l
    
    data = sauve_frames[id_frame](**donnees)
    header = bytes(id_frame, "utf-8")
    
    taille = len(data)
    if "ID3v2.4" in version:
        taille_b = b""
        i = 3
    
        while i > -1:
            taille_b += (taille // pow(128, i)).to_bytes(1, 'big')
            taille %= pow(128, i)
        
            i -= 1
    else:
        taille_b = taille.to_bytes(4, 'big')
    
    header += taille_b + b"\x00\x00"
    data = header + data
    
    header = FrameHeader(header, version)
    
    if id_frame[0] == 'T' or id_frame == 'COMM':
        base = FrameText
    elif id_frame[0] == 'W':
        base = FrameURL
    elif id_frame == 'APIC':
        base = FrameImage
    else:
        base = FrameAutre
    
    class Frame(base):
        def __repr__(self):
            return 'Tag {}'.format(self.id_frame)
    
    return Frame(data, header)
