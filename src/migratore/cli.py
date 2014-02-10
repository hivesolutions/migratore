#!/usr/bin/python
# -*- coding: utf-8 -*-

def run_list():
    print "listagem"

def run_generate(path = None):
    print "vai gerar ficheiro"

    import time
    timestamp = time.time()
    path = path or str(timestamp) + ".py"

    print path
