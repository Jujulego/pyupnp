# -*- coding: utf-8 -*-
# Importations
from random import randrange
from threading import RLock
from datetime import timedelta
from time import sleep

import fcntl
import socket
import struct

# Fonctions
def verif_type(objet, nom_argument, *types_objet, no_error=False):
    """
        Fonction vérifiant le type d'un argument.
    """
    pas_type = ""
    ok_type = False
    
    for t in types_objet:
        if not isinstance(objet, t):
            pas_type += str(t)[8:-2] + ", "
        
        else:
            ok_type = True
    
    if not no_error:
        if not ok_type:
            raise TypeError("L'argument {} n'est pas du/des type(s) {}".format(nom_argument, pas_type[:-2]))
    
    else:
        if not ok_type:
            return False
        
        return True

# Génération de texte aléatoire
table_char = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
              'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
              'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

def generate_rand_text(longueur):
    t = ''
    for _ in range(longueur):
        t += table_char[randrange(60)]
    
    return t

# Suppression des accents
accents = {
    "a": ("à", "á", "â", "ã", "ä", "å", "æ", "ā", "ă", "ą"),
    "A": ("À", "Á", "Â", "Ã", "Ä", "Å", "Æ", "Ā", "Ă", "Ą"),
    "c": ("ç", "ć", "č"),
    "C": ("Ç", "Ć", "Č"),
    "d": ("ď", "đ"),
    "D": ("Ď", "Đ"),
    "e": ("è", "é", "ê", "ë", "ė", "ę", "ě", "ĕ", "ə", "ē"),
    "E": ("È", "É", "Ê", "Ë", "Ė", "Ę", "Ě", "Ĕ", "Ə", "Ē"),
    "g": ("ģ", "ğ"),
    "G": ("Ģ", "Ğ"),
    "i": ("ì", "í", "î", "ï"),
    "I": ("Ì", "Í", "Î", "Ï"),
    "k": ("ķ",),
    "K": ("Ķ",),
    "l": ("ł", "ľ", "ļ", "ĺ"),
    "L": ("Ł", "Ľ", "Ļ", "Ĺ"),
    "n": ("ň", "ņ", "ń", "ñ"),
    "N": ("Ň", "Ņ", "Ń", "Ñ"),
    "o": ("ő", "ø", "ö", "õ", "ó", "ò", "œ", "ô"),
    "O": ("Ő", "Ø", "Ö", "Õ", "Ó", "Ò", "Œ", "Ô"),
    "r": ("ŕ", "ř"),
    "R": ("Ŕ", "Ř"),
    "s": ("ß", "§", "ś", "š", "ş"),
    "S": ("ß", "§", "Ś", "Š", "Ş"),
    "t": ("þ", "ť", "ț", "ţ"),
    "T": ("Þ", "Ť", "Ț", "Ţ"),
    "u": ("ų", "ű", "ů", "ū", "ü", "ú", "ù", "û"),
    "U": ("Ų", "Ű", "Ů", "Ū", "Ü", "Ú", "Ù", "Û"),
    "y": ("ý",),
    "Y": ("Ý",),
    "z": ("ź", "ż", "ž"),
    "Z": ("Ź", "Ż", "Ž"),
}

def anti_accent(string):
    """Remplace les caractères avec accents par ceux correspondant sans accent"""
    
    texte = ""
    for c in string:
        for a in accents.items():
            if c in a[1]:
                c = a[0]
        texte += c

    return texte

# Affichage sécurisé en multi-threads
affichage_verrou = RLock()

def afficher(texte):
    '''
    Affiche de manière thread-safe.
    '''
    global affichage_verrou
    
    with affichage_verrou:
        print(texte)

# Affichages stylisés
def genererTableau(donnees, rangs=None, couleur=lambda d: "0"):
    verif_type(donnees, "donnees", list)
    verif_type(rangs, "rangs", list, type(None))

    if not rangs:
        rangs = list(donnees[0].keys())

    max_rangs = {}
    for r in rangs:
        m = len(r)

        for d in donnees:
            try:
                m = max(m, len(str(d[r])))

            except KeyError:
                pass

        max_rangs[r] = m
    
    interligne1 = "┌"
    interligne2 = "├"
    interligne3 = "└"
    entete = "│"
    base = "│"
    for r in rangs:
        interligne1 += "─" * (max_rangs[r]+2) + "┬"
        interligne2 += "─" * (max_rangs[r]+2) + "┼"
        interligne3 += "─" * (max_rangs[r]+2) + "┴"
        entete += (" {:^" + str(max_rangs[r]) + "} │").format(r)
        base += " \033[{1}m{0[" + r + "]!s:<" + str(max_rangs[r]) + "}\033[0m │"
    
    texte = interligne1[:-1] + "┐\n"
    texte += entete + "\n"
    texte += interligne2[:-1] + "┤\n"
    for d in donnees:
        texte += base.format(d, couleur(d)) + "\n"
    
    texte += interligne3[:-1] + "┘"
    
    return texte

# Mesurer le temps
def chrono(temps):
    verif_type(temps, "temps", int)
    
    t = timedelta(seconds=0)
    dt = timedelta(seconds=1)
    
    print(t)
    while t.seconds <= temps:
        sleep(1)
        t += dt
        print("\033[A" + str(t))

def minuteur(temps):
    verif_type(temps, "temps", int)
    
    t = timedelta(seconds=temps)
    dt = timedelta(seconds=1)
    
    print(t)
    while t.seconds > 0:
        sleep(1)
        t -= dt
        print("\033[A" + str(t))
    
    print("Driiiiing !!!!")

# Récupérer l'adresse ip
def recupIp(*interfaces):
    """
    Renvoie l'adresse Ip de la première interface donnée
    Par défaut utilise 'lo'
    """
    
    if len(interfaces) == 0:
        interfaces = ['lo']
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    erreurs = []
    
    try:
        for interface in interfaces:
            try:
                return socket.inet_ntoa(fcntl.ioctl(sock.fileno(), 0x8915, struct.pack("256s", interface.encode("utf-8")))[20:24])
            
            except OSError as err:
                if err.errno in [19, 99]:
                    erreurs.append(err)
                    continue
                
                raise
        
        raise erreurs[0]
    
    finally:
       sock.close()

# Fichiers
def joinext(nom, ext):
    if nom.endswith(ext):
        return nom
    
    while nom.endswith("."):
        nom = nom[:-1]
    
    while ext.startswith("."):
        ext = ext[1:]
    
    return ".".join((nom, ext))
