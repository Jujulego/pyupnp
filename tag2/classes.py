# -*- coding: utf-8 -*-

# Exceptions
class ErreurFichierMP3(Exception):
    """Levée pour toute erreur rapport au fichier MP3 annalysé"""
    pass

class TagErreur(Exception):
    """Erreur lors de l'analyse des tags"""
    pass

class FrameErreur(Exception):
    """Erreur lors de l'analyse d'un frame"""
    pass

class FrameErreurFatale(FrameErreur):
    """Erreur fatale lors de l'analyse d'un frame"""
    pass

class StopFrameIteration(Exception):
    """Plus de frames à analyser"""
    pass

# Warning
class FrameWarning(Warning):
    """Envoyé si il y a eu une erreur lors de l'analyse des frames."""
    pass

# Classes
class MyDate():
    """Classe pareille à datetime.date, l'année en moins"""

    mois_text = {    1:  "janvier",
            2:  "février",
            3:  "mars",
            4:  "avril",
            5:  "mai",
            6:  "juin",
            7:  "juillet",
            8:  "août",
            9:  "septembre",
            10: "octobre",
            11: "novembre",
            12: "décembre"}

# Méthodes spéciales:
## Générales:
    def __init__(self, mois, jours):
        self.mois = mois
        self.jours = jours

    def __repr__(self):
        return "{} {}".format(str(self.jours), Date.mois_text[self.mois])

    def __str__(self):
        return "{} {}".format(str(self.jours), Date.mois_text[self.mois])

# Méthodes:
    def vers_date(self, annees):
        from datetime import date
        return date(year=annees, month=self.mois, day=self.jours)
    
    def vers_bytes(self):
        return self.jours.to_bytes(1, 'big') + self.mois.to_bytes(1, 'big')

# Asseceurs:
    def _get_mois(self):
        return self._mois

    def _get_jours(self):
        return self._jours

# Modateurs:
    def _set_mois(self, mois):
        if mois > 12 or mois < 0:
            raise AttributeError("L'argument mois doit être compris entre 0 et 12 inclus")
        self._mois = mois

    def _set_jours(self, jours):
        if self.mois in [1, 3, 5, 7, 8, 10, 12] and (jours < 0 or jours > 31):
            raise AttributeError("L'argument jours doit être compris entre 0 et 31 inclus")
        elif self.mois in [4, 6, 9, 11] and (jours < 0 or jours > 30):
            raise AttributeError("L'argument jours doit être compris entre 0 et 30 inclus")
        elif self.mois == 2 and (jours < 0 or jours > 29):
            raise AttributeError("L'argument jours doit être compris entre 0 et 29 inclus")
        self._jours = jours

# Propriétés:
    mois = property(_get_mois, _set_mois)
    jours = property(_get_jours, _set_jours)
