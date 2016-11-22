# -*- coding: utf-8 -*-

# Importations
# Tag :
from .classes import ErreurFichierMP3

# Python (système)
import re

# analyse TCON
from .dicos import genres

# analyse TKEY
from .dicos import notes

# analyse TMED
from .dicos import type_media, extension_type_media

# analyse du fichier
from .dicos import numero_layer, version_MPEG, dico_biterate, deter_frequence_echantillons, mode_chaine

# Fonctions générales
def verif_type(objet, nom_argument, *types_objet):
    """Fonction vérifiant le type d'un argument"""
    pas_type = ""
    
    for t in types_objet:
        if type(objet) is not t:
            ok_type = True
            pas_type += str(t)[8:-2] + ", "
        else:
            ok_type = False
    if ok_type:
        raise TypeError("L'argument {} n'est pas du/des type(s) {}".format(nom_argument, pas_type[:-2]))

def anti_none(*liste):
    """Fonction supprimant les valeurs égale a None dans un/des dictionnaire(s)"""
    n_liste = []
    for dico in liste:
        i = 0
        while i < len(dico):
            for k in dico.keys():
                if dico[k] == None:
                    del dico[k]
                    i = 0
                    break
                i += 1
        n_liste.append(dico)
    return n_liste

def get_key_from_item_dict(dico, item):
    return list(dico.keys())[list(dico.values()).index(item)]

# Analyse de frames plus pousées
def anal_tkey(tkey, encodage):
    """Fonction analysant la valeur du frame TKEY"""
    verif_type(tkey, 'tkey', bytes)
    
    tkey = tkey.decode(encodage)
    text_tkey = notes[tkey[0]]
    
    try:
        if tkey[1] == '#':
            text_tkey += ' dièse'
        elif tkey[1] == 'b':
            text_tkey += ' bémole'
        elif tkey[1] == 'm':
            text_tkey += ' mineur'
        if tkey[2] == 'm':
            text_tkey += ' mineur'
    finally:
        return text_tkey

def sauve_tkey(valeur, encod):
    tkey = get_key_from_item(notes, valeur[:valeur.find(' ')])
    
    valeur = valeur[valeur.find(' ') + 1:]
    
    if valeur.find(' ') != -1:
        val = valeur[:valeur.find(' ')]
    else:
        val
    
    if val == 'dièse':
        tkey += '#'
    elif val == 'bémole':
        tkey += 'b'
    elif val == 'mineur':
        tkey += 'm'
    
    if valeur.find(' ') != -1:
        tkey += 'm'
    
    return bytes(tkey, encod)

def anal_tmed(tmed, encodage):
    """Fonction analysant la valeur du frame TMED"""
    verif_type(tmed, 'tmed', bytes)
    
    l_tmed = tmed.decode(encodage).split('(')
    tmed = ""
    for t in l_tmed:
        tmed += t + ')'
        
    l_tmed = tmed.split(')')
    while l_tmed.count('') > 0:
        l_tmed.remove('')
        
    text_tmed = ""
    regex_anal = re.compile("^(?P<valeur>([( ]{0,2}((?P<CD>CD)((?P<DD>/DD)|(?P<AD>/AD)|(?P<AA>/AA)|(?P<A2>/A)){0,4})|((?P<DIG>DIG)(?P<A1>/A)?)|((?P<ANA>ANA)((?P<WAC>/WAC)|(?P<n8CA>/8CA)){0,2})|((?P<LD>LD)(?P<A3>/A)?)|((?P<TT>TT)((?P<n33>/33)|(?P<n45>/45)|(?P<n71>/71)|(?P<n76>/76)|(?P<n78>/78)|(?P<n80>/80)){0,6})|((?P<MD>MD)(?P<A4>/A)?)|((?P<DAT>DAT)((?P<A5>/A)|(?P<n1>/1)|(?P<n2>/2)|(?P<n3>/3)|(?P<n4>/4)|(?P<n5>/5)|(?P<n6>/6)){0,7})|((?P<DCC>DCC)(?P<A6>/A)?)|((?P<DVD>DVD)(?P<A7>/A)?)|((?P<TV>TV)((?P<PAL1>/PAL)|(?P<NTSC1>/NTSC)|(?P<SECAM1>/SECAM)){0,3})|((?P<VID>VID)((?P<PAL2>/PAL)|(?P<NTSC2>/NTSC)|(?P<SECAM2>/SECAM)|(?P<VHS>/VHS)|(?P<SVHS>/SVHS)|(?P<BETA>/BETA)){0,6})|((?P<RAD>/RAD)(/(?P<FM>/FM)|(?P<AM>/AM)|(?P<LW>/LW)|(?P<MW>/MW)){0,4})|((?P<TEL>/TEL)(?P<I1>/I)?)|((?P<MC>MC)((?P<m4>/4)|(?P<n9>/9)|(?P<II1>/II)|(?P<III1>/III)|(?P<IV1>/IV)|(?P<I2>/I)){0,6})|((?P<REE>REE)((?P<m9>/9)|(?P<n19>/19)|(?P<n38>/38)|(?P<m76>/76)|(?P<II2>/II)|(?P<III2>/III)|(?P<IV2>/IV)|(?P<I3>/I)){0,8})[ )]?)|(?P<TEXT>[^\x00]+))+$")
    
    anal = []
    for tmed in l_tmed:
        anal_tmed = regex_anal.match(tmed).groupdict()
        
        anal_tmed["A"] = anal_tmed["A1"] or anal_tmed["A2"] or anal_tmed["A3"] or anal_tmed["A4"] or anal_tmed["A5"] or anal_tmed["A6"] or anal_tmed["A7"]
        anal_tmed["PAL"] = anal_tmed["PAL1"] or anal_tmed["PAL2"]
        anal_tmed["NTSC"] = anal_tmed["NTSC1"] or anal_tmed["NTSC2"]
        anal_tmed["SECAM"] = anal_tmed["SECAM1"] or anal_tmed["SECAM2"]
        anal_tmed["n4"] = anal_tmed["n4"] or anal_tmed["m4"]
        anal_tmed["I"] = anal_tmed["I1"] or anal_tmed["I2"] or anal_tmed["I3"]
        anal_tmed["II"] = anal_tmed["II1"] or anal_tmed["II2"]
        anal_tmed["III"] = anal_tmed["III1"] or anal_tmed["III2"]
        anal_tmed["IV"] = anal_tmed["IV1"] or anal_tmed["IV2"]
        anal_tmed["n9"] = anal_tmed["n9"] or anal_tmed["m9"]
        anal_tmed["n76"] = anal_tmed["n76"] or anal_tmed["m76"]
        
        texte = anal_tmed["TEXT"]
        
        del anal_tmed["valeur"], anal_tmed["A1"], anal_tmed["A2"], anal_tmed["A3"], anal_tmed["A4"], anal_tmed["A5"], anal_tmed["A6"], anal_tmed["A7"], anal_tmed["PAL1"], anal_tmed["PAL2"], anal_tmed["NTSC1"], anal_tmed["NTSC2"], anal_tmed["SECAM1"], anal_tmed["SECAM2"], anal_tmed["m4"], anal_tmed["I1"], anal_tmed["I2"], anal_tmed["I3"], anal_tmed["II1"], anal_tmed["II2"], anal_tmed["III1"], anal_tmed["III2"], anal_tmed["IV1"], anal_tmed["IV2"], anal_tmed["m9"], anal_tmed["TEXT"]
        
        anti_none(anal_tmed)
        
        text_tmed += " | "
        
        for k in type_media.keys():
            if k in anal_tmed.values():
                text_tmed += type_media[k]
                
        for k in extension_type_media.keys():
            if k in anal_tmed.values():
                text_tmed += extension_type_media[k]
                
        try:
            if texte[0] == " ":
                texte = texte[1:]
            text_tmed += " " + texte
            
        except TypeError:
            pass
            
    return text_tmed[3:]

def sauve_tmed(valeur, encod):
    list_val = valeur.split(' | ')
    tmed = ""
    
    for val in list_val:
        if len(list_val) != 1:
            tmed += '('
        
        lp_val = val.split(', ')
        
        tmed += get_key_from_item_dict(type_media, lp_val[0])
        del lp_val[0]
        
        for p_val in lp_val:
            tmed += get_key_from_item_dict(extension_type_media, ", " + p_val)
        
        if len(list_val) != 1:
            tmed += ')'
    
    return bytes(tmed, encod)

def anal_tcon(tcon, encodage):
    """Fonction analysant la valeur du frame TCON"""
    verif_type(tcon, 'tcon', bytes)
    
    l_tcon = tcon.decode(encodage).split('(')
    tcon = ""
    for t in l_tcon:
        tcon += t + ')'
        
    l_tcon = [t for t in tcon.split(')') if t] # Élimine les strings vides
    tcon = ""
    
    for t in l_tcon:
        if t.isnumeric():
            tcon += genres[int(t)]
        else:
            tcon += t
        
        tcon += ", "
        
    while tcon.endswith(", "):
        tcon = tcon[:-2]
    
    return tcon

# Analyse des caractéristiques du fichier
def anal_mp3(fichier, taille_tag):
    # Récuperation et analyse de l'entête
    x = fichier.find(b"\x00"*100+b"\xff")
    if x == -1:
        raise ErreurFichierMP3("Fichier MP3 non comforme")
        
    t = fichier[x+100:]
    dict_tag_mp3 = re.match("(?P<version_MPEG>[01]{2})(?P<numero_layer>[10]{2})(?P<protection>[10])(?P<index_biterate>[10]{4})(?P<index_echantillon_frequence>[10]{2})(?P<remplissage>[01])(?P<prive>[10])(?P<mode_chaine>(01(P?<extension_mode>[01]{2}))|[01]{2})(?P<copyright>[01])(?P<original>[01])", bin(int.from_bytes(t[:10], "big"))[2:][11:], re.DOTALL).groupdict()

    layer = numero_layer[dict_tag_mp3["numero_layer"]]
    version_mpeg = version_MPEG[dict_tag_mp3["version_MPEG"]]
    biterate = dico_biterate[version_mpeg][layer][dict_tag_mp3["index_biterate"]]

    # Récuperation et analyse (Si existance) du type MP3
    t = t[10:]
    type_mp3 = re.match(b"(?P<Xing>\x00{9,32}Xing.{3}(?P<flag_taille_frame>.)(?P<frame_taille>.{4})?(?P<taille>.{4})?.*)|(?P<VRBI>\x00{32}VRBI(?P<version_VRBI>.{2})(?P<delai>.{2})(?P<qualite>.{2})(?P<taille2>.{4})(?P<frame>.{4}).*)|.*", t, re.DOTALL).groupdict()

    Xing = {}

    if type_mp3["Xing"] != None:
        dict_tag_mp3["type"] = "Xing"
        frame_logic = bin(int.from_bytes(type_mp3["flag_taille_frame"], "big"))[-1]
        taille_logic = bin(int.from_bytes(type_mp3["flag_taille_frame"], "big"))[-2]

        if frame_logic:
            Xing["frame"] = int.from_bytes(type_mp3["frame_taille"], "big")

        if taille_logic:
            if frame_logic:
                    Xing["taille"] = int.from_bytes(type_mp3["taille"], "big")
            else:
                    Xing["taille"] = int.from_bytes(type_mp3["frame_taille"], "big")

        dict_tag_mp3["Xing"] = Xing

    elif type_mp3["VRBI"] != None:
        dict_tag_mp3["type"] = "VRBI"
        VRBI = {"version"     : type_mp3["version"],
            "délai"      : type_mp3["delai"],
            "qualité"     : type_mp3["qualite"],
            "taille"     : type_mp3["taille"],
            "nombre de frame": type_mp3["frame"]}

    else:
        dict_tag_mp3["type"] = "autre"

    # Calcul de la durée:
    if type_mp3["Xing"] != None and len(Xing) == 2:
        duree = ((Xing["taille"] * 8) / 1000) / (((Xing["taille"] * 8) / 1000) / ((Xing["frame"] / 38) - 1))
    elif type_mp3["VRBI"] != None:
        duree = (((VRBI["taille2"] - VRBI["delai"]) * 8) / 1000) / ((((VRBI["taille2"] - VRBI["delai"]) * 8) / 1000) / ((VRBI["nombre de frame"] / 38) - 1))
    else:
        duree = (((len(fichier) - taille_tag) * 8) / 1000) / biterate

    dict_tag_mp3["numero_layer"] = layer
    dict_tag_mp3["version_MPEG"] = version_mpeg
    dict_tag_mp3["biterate"] = biterate
    dict_tag_mp3["échantillons fréquence"] = deter_frequence_echantillons[version_mpeg][dict_tag_mp3["index_echantillon_frequence"][:2]]
    dict_tag_mp3["mode_chaine"] = mode_chaine[dict_tag_mp3["mode_chaine"]]
    dict_tag_mp3["durée"] = round(duree)
    return dict_tag_mp3
