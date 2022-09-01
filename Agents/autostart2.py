#!/usr/bin/env python2
# coding: utf8
# Copyright 2019 Fabrice DUVAL

from __future__ import unicode_literals
from __future__ import print_function

from subprocess import Popen
import sys
import time

filename = sys.argv[1]
# filename = "StateMachineR1.py"

commande = "python2 " + ' '.join(sys.argv[1:])
while True:
    print("\nStarting " + filename)
    print(commande) 
    p = Popen(commande, shell=True)
    p.wait()
    time.sleep(5)
#    break
