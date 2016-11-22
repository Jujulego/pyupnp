#! /usr/bin/python3.5
# Importations
import starter

import gc
import tracemalloc

# Execution
if __name__ == "__main__":
    tracemalloc.start(200)
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
    
    starter.Starter().executer()
    
    print("Tracemalloc stats :")
    
    snapshot = tracemalloc.take_snapshot()
    top_l = snapshot.statistics('lineno')
    top = snapshot.statistics('traceback')
    rep = ""
    
    while rep != "q":
        print("[ Top 20 ]")
        i = 1
        
        for stat in top_l[:20]:
            print(" {:<2d} ".format(i), stat)
            i += 1
        
        print("")
        print("Voir quel traceback ? (q pour quitter)")
        rep = input("> ")
        
        if not rep.isdecimal():
            continue
        
        stat = top[int(rep)-1]
        print("")
        print("Traceback n°{} :".format(rep))
        print(top_l[int(rep)-1])
        print("{} blocks: {:.2f} KiB".format(stat.count, stat.size / 1024))
        for l in stat.traceback.format():
            print("  ", l)
        
        print("")
        input("[Appuyez sur ENTREE]")
    
    print("Au revoir !")
