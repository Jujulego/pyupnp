# -*- coding: utf-8 -*-

# Importations:
# Tag
from .classes import TagErreur, FrameErreur, FrameErreurFatale, StopFrameIteration, ErreurFichierMP3, FrameWarning
from .dicos import flags_id3v2
from .fonctions import anal_mp3
from .frames import FrameHeader, FrameText, FrameImage, FrameURL, FrameAutre, frame_generator
from .header import TagHeader

from base.utils import verif_type
from fichiers.base import Fichier

from django.core.files import File

from io import BufferedReader
from os import makedirs, path
import warnings

# Classe Tag
class Tag():
    """Classe contenant les résultats d'une analyse des tags d'un fichier audio mp3:

- le fichier :                  fichier----------> ouvert en lecture par octets (rb)
- la version des tags :         version ---------|
- la taille totale des tags :   taille ----------|----> Sortis d'un objet TagHeader
- les drapeaux du header :      drapeaux_header -|

- le titre du morceau :         titre ------|
- le nom de l'album :           album ------|
- le nom de l'artiste :         artiste ----|----> Sortis de l'attribut tags
- le genre :                    genre ------|
- le numero du morceaux :       numero -----|

- durée :                       durée ------------> Objet Duree (sorti de l'attribut tags)

- touts les tags :              tags -------------> Dictionnaire d'objets Frame

- erreurs :            les erreurs du processus -----> ensemble des erreurs
"""

    # Méthodes spéciales:
    # Générales
    def __init__(self, fichier, anal_id3=True):
        """
        tag.__init__(fichier, anal_tags) => Tag
            fichier: le fichier à analyser
            anal_tags: analyse des tags ID3 (par default True)
                 Le désactiver permet de ne récupérer que les infos sur le fichier, comme sa durée
        """
        
        # Récupération et vérification de l'objet fichier
        if not (type(fichier) in (File, BufferedReader) or issubclass(type(fichier), File)):
            raise TypeError("fichier doit être une instance de File (Django), ou ouvert en mode rb (objet BufferedReader)")
        
        if type(fichier) is BufferedReader:
            fichier = File(fichier)
            
        self._fichier = fichier
        
        # liste des erreurs
        self._erreurs = {
            "frame": [],
            "autre": [],
        }
        
        # Analyse du header du fichier (10ers octets)
        self._header = TagHeader(self.lire_fichier(10))
        
        # Analyse des caractéristiques du fichier
        self._infos_mp3 = anal_mp3(self.lire_fichier(fichier.size), self._taille)
        
        if anal_id3:
            # Analyse des frames
            if self.version[:5] == "ID3v2":
                self.anal_frames2()

    def __iter__(self):
        return iter(self.tags)

    def __repr__(self):
        return "<Tag {}, {}>".format(self.fichier.name, self.version)

## Attributs:
    def __getattribute__(self, nom):
        """Entrer t.TXXX revient a t["TXXX"]"""
        if nom in flags_id3v2.keys():
            return self[nom]
        else:
            return super(Tag, self).__getattribute__(nom)

## Index:
    def __getitem__(self, index):
        """t[index] <=> t.tags[index]"""
        try:
            return self.tags[index]
        except KeyError as err:
            err.args = ("Le tag {} est inconnu ou non-défini".format(index), )
            raise err

    def __setitem__(self, index, valeur):
        if index in ['TCOM', 'TEXT', 'TOLY', 'TOPE', 'TPE1']:
            self.creer_frame(index, v=valeur)
        else:
            try:
                self.tags[index][0].valeur = valeur
            except IndexError:
                self.creer_frame(index, v=valeur)

    def __delitem__(self, index):
        del self.tags[index]

# Méthodes:
    def anal_frames2(self):
        # Récupération des frames (du 10eme octet à self.taille - 10 (sans le header))
        frames = self.lire_fichier(self._taille-10, 10)
        self.tags = {}
        
        while len(frames) > 0:
            # Analyse du header de tag. Si erreur : impossible de déterminer la taille du frame ou tags fini => arrêt de la boucle
            try:
                header = FrameHeader(frames[:10], self.version)
            except FrameErreurFatale as err:
                self._erreurs["frame"].append(FrameErreurFatale("FrameErreurFatale\n{base}\nFichier: {nom_f}\nTag: {tag}".format(base=err.args[0], nom_f=self.fichier.name, tag=frames[:header.taille])))
                break
            except StopFrameIteration:
                break
            
            if header.id_frame[0] == 'T' or header.id_frame == "COMM":
                base = FrameText
            elif header.id_frame[0] == 'W':
                base = FrameURL
            elif header.id_frame == "APIC":
                base = FrameImage
            else:
                base = FrameAutre
            
            try:
                frame = self._creer_classe_frame(base)(frames[:header.taille], header)
                
                try:
                    self.tags[frame.id_frame].append(frame)
                except KeyError:
                    self.tags[frame.id_frame] = [frame]
            except FrameErreur as err:
                self._erreurs["frame"].append(FrameErreur("FrameErreur\n{base}\nFichier: {nom_f}\nTag: {tag}".format(base=err.args[0], nom_f=self.fichier.name, tag=frames[:header.taille])))
            except Exception as err:
                self._erreurs["autre"].append(FrameErreur("{type_err}\n{base}\nFichier: {nom_f}\nTag: {tag}".format(type_err=str(type(err))[8:-2], base=err.args[0], nom_f=self.fichier.name, tag=frames[:header.taille])))
            
            frames = frames[header.taille:]
        self._zero = len(frames)
        
        if len(self.erreurs["autre"]) + len(self.erreurs["frame"]) > 0:
            warnings.warn("Erreurs lors de l'analyse des frames", FrameWarning)

    def lire_fichier(self, num_cf, num_cd=0):
        self.fichier.seek(num_cd)
        return self.fichier.read(num_cf)
    
    @staticmethod
    def _creer_classe_frame(bases):
        class Frame(bases):
            def __repr__(self):
                return 'Tag {}'.format(self.id_frame)
        return Frame
    
    def creer_frame(self, id_frame, **data):
        frame = frame_generator(id_frame, self.version, **data)
        
        try:
            self.tags[id_frame].append(frame)
        except KeyError:
            self.tags[id_frame] = [frame]
    
    def _sum_text_tags(self, identifiant):
        tags = self[identifiant]
        text = ""
        for tag in tags:
            if type(tag.valeur) is list:
                for t in tag.valeur:
                    text += t + ", "
                text = text[:-2]
            else:
                text += str(tag.valeur)
            text += ", "
        return text[:-2]
    
    def sauve(self, nom=None, ecrase=False, creer_dir=True):
        taille = self._taille
        data = b""
        for tag in self.tags.values():
            for f in tag:
                data += f.sauve()
        
        data += bytes(self._zero)
        
        if len(data) != self.header.taille - 10:
            self.header.taille = len(data) + 10
        
        if not nom:
            nom = self.fichier.name
        
        if path.exists(nom) and not ecrase:
            raise ValueError("Le fichier {} existe déjà".format(nom))
        
        if not path.exists(path.dirname(nom)):
            if creer_dir:
                makedirs(path.dirname(nom), exist_ok=True)
            else:
                raise ValueError("Le dossier {} n'existe pas".format(path.dirname(nom)))
        
        morc = self.lire_fichier(self.fichier.size, taille)
        
        with open(nom, "wb") as f:
            f.write(self.header.sauve() + data + morc)
            f.flush()
        
        self = Tag(File(open(nom, 'rb')))
        return self
    
# Propriétés:
# erreurs
    @property
    def erreurs(self):
        return self._erreurs

# fichier
    @property
    def fichier(self):
        return self._fichier

# header
    @property
    def header(self):
        return self._header
    
    # Sous-attributs:
    # drapeaux
    @property
    def drapeaux_header(self):
        return self.header.drapeaux
    
    # taille
    @property
    def _taille(self):
        return self.header.taille
    
    @property
    def taille(self):
        """Affichage de l'attribut taille avec unités en facteurs de 1024:
- o  (octets)        *1024⁰
- ko (kilooctets)    *1024¹
- Mo (Mégaoctets)    *1024²
- Go (Gigaoctets)    *1024³"""

        if self._taille // pow(1024, 3) != 0:
            # Assez rare ...
            taille = str(round(self._taille / pow(1024, 3), 2)) + "Go"
            
        elif self._taille // pow(1024, 2) != 0:
            taille = str(round(self._taille / pow(1024, 2), 2)) + "Mo"
            
        elif self._taille // pow(1024, 1) != 0:
            taille = str(round(self._taille / pow(1024, 1), 2)) + "ko"
            
        else:
            taille = str(self._taille) + "o"
            
        return taille
    
    # version
    @property
    def version(self):
        return self.header.version

# quelques frames
    @property
    def album(self):
        try:
            return self._sum_text_tags("TALB")
        except KeyError:
            return None
    
    @album.setter
    def album(self, album):
        verif_type(album, 'album', str)
        
        try:
            self.tags['TALB'][0].valeur = album
        except KeyError:
            self.creer_frame('TALB', v=album)

    @property
    def artiste(self):
        try:
            return self._sum_text_tags("TPE1")
        except KeyError:
            return None
    
    @artiste.setter
    def artiste(self, artiste):
        verif_type(artiste, 'artiste', str, list)
        
        if type(artiste) is str:
            artiste = artiste.split(',')
        
        self.creer_frame('TPE1', v=artiste)
    
    @artiste.deleter
    def artiste(self):
        self.tags['TPE1'] = []

    @property
    def duree(self):
        return self.infos_mp3["durée"]
    
    @duree.setter
    def duree(self, duree):
        raise AttributeError("Impossible de modifier la durée: ce n'est pas dans les tags.")

    @property
    def infos_mp3(self):
        return self._infos_mp3
    
    @infos_mp3.setter
    def infos_mp3(self, d):
        raise AttributeError("Impossible de modifier cela.")

    @property
    def genre(self):
        try:
            return self._sum_text_tags("TCON")
        except KeyError:
            return None
    
    @genre.setter
    def genre(self, genre):
        verif_type(genre, 'genre', str)
        
        try:
            self.tags['TCON'][0].valeur = genre
        
        except KeyError:
            self.creer_frame('TCON', v=genre)
    
    @property
    def numero(self):
        try:
            return self._sum_text_tags("TRCK")
        except KeyError:
            return "0"
    
    @numero.setter
    def numero(self, numero):
        verif_type(numero, 'numero', str, int)
        
        if type(numero) is int:
            numero = str(numero)
        
        try:
            self.tags['TRCK'][0].valeur = numero
        except KeyError:
            self.creer_frame('TRCK', v=numero)

    @property
    def titre(self):
        try:
            return self._sum_text_tags("TIT2")
        except KeyError:
            return None
    
    @titre.setter
    def titre(self, titre):
        verif_type(titre, 'titre', str)
        
        try:
            self.tags['TIT2'][0].valeur = titre
        except KeyError:
            self.creer_frame('TIT2', v=titre)
