#!/usr/bin/python
# -*- coding: utf-8 -*-

import migration

def run_list():
    print "listing"

def run_generate(path = None):
    migration.Migration.generate(path)
