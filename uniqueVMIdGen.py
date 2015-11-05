#!/usr/bin/python2.7

import os
import random

UFILE = "/home/t/thesis/VM_CUID"

print UFILE


def get_vmid():
    if os.path.exists(UFILE):
            f = open(UFILE,"r+")
            content = f.readline()
            print content
            f.close()
    else:
            seed = random.random()
            print seed
            print random.seed(seed)
            ran = random.random()
            o = str(ran)
            print o
            f = open(UFILE, "w+")
            f.write(o)
            f.close()

if __name__ == "__main__":
    get_vmid()
