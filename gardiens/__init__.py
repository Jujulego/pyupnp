# Importations
from .gardien import Gardien
from .lock import RLock

import multiprocessing as mp

mp.Process.run_base = mp.Process.run

def run(self):
    try:
        return self.run_base()
    
    finally:
        if hasattr(self, "gardien"):
            if self.gardien.status == "actif":
                self.gardien.arreter(False)

mp.Process.run = run
