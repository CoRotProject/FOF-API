#!/usr/bin/env python3
# Copyright 2020 Fabrice DUVAL

from subprocess import Popen
import sys
import os
import time

filename = sys.argv[1]
dirfilename = os.path.dirname(sys.argv[1])
if dirfilename:
    os.chdir(dirfilename)
    filenamerun = os.path.basename(filename)
else:
    filenamerun = filename

commande = "python3 " + filename + ' ' + ' '.join(sys.argv[2:])
while True:
    print("\nStarting " + filenamerun)
    p = Popen(commande, shell=True)
    p.wait()
    time.sleep(5)
