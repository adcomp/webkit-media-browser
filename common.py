#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import os
import os.path
import sys
import random
import subprocess
from subprocess import Popen
import fcntl

def launch_command(cmd):
    if cmd != ' ' and cmd != None and len(cmd)!=0:

        try:
            subprocess.Popen(cmd, shell=True)
        except OSError:
            pass

def get_ext(fullpath):
    if not '.' in fullpath:
        return None
    else:
        return fullpath.split('.')[-1]

class Entry:
    
    def __init__(self, name, xtype, ext=None):
        self.name = name
        self.xtype = xtype
        
        if ext:
            self.ext = ext
