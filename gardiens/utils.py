# Importations
from base.utils import recupIp

from datetime import datetime
import multiprocessing as mp
import time

# Fonctions
def identifiant_processus():
    proc = mp.current_process()
    
    if not hasattr(proc, "gardien_id"):
        proc.gardien_id = "{:02x}{:02x}{:02x}{:02x}-{pid:04x}-{epoch:016x}".format(
            *([int(x) for x in recupIp().split(".")]),
            pid=proc.pid,
            epoch=int(time.time() * pow(10,7))
        )
    
    return proc.gardien_id

def analyse_identifiant(ident):
    ip, pid, epoch = ident.split('-')
    
    ip = '.'.join([str(int(ip[:2], 16)), str(int(ip[2:4], 16)), str(int(ip[4:6], 16)), str(int(ip[6:8], 16))])
    pid = int(pid, 16)
    epoch = int(epoch, 16) / (pow(10, 7))
    
    return ip, pid, datetime.fromtimestamp(epoch)
