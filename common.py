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
            Popen(cmd, shell=True)
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

#~ class Pymplayer(gtk.Socket):
class MPlayer(gtk.DrawingArea):
    """ Classe d'interface entre mplayer et le programme """
    
    def __init__(self, theme):
        gtk.DrawingArea.__init__(self)
        
        #~ self.connect('size-allocate', self._size_allocate)
        self.connect('realize', self._realize)
        
        self.theme = theme
        self.mplayer_pipe = '/tmp/mplayer_wmb.pipe'

        try:
            os.unlink(self.mplayer_pipe)
        except:
            pass

        os.mkfifo(self.mplayer_pipe)
        os.chmod(self.mplayer_pipe, 0666)

    def _size_allocate(self, widget, allocation):
        print allocation

    def _realize(self, widget):
        color = gtk.gdk.Color('#000')
        # set bg color to black
        widget.modify_bg(gtk.STATE_NORMAL, color)
        # set xid for mplayer
        self.setwid(long(widget.window.xid))

        # hide mouse cursor
        pix_data = """/* XPM */
        static char * invisible_xpm[] = {
        "1 1 1 1",
        "       c None",
        " "};"""
        pix = gtk.gdk.pixmap_create_from_data(None, pix_data, 1, 1, 1, color, color)
        invisible = gtk.gdk.Cursor(pix, pix, color, color, 0, 0)
        widget.window.set_cursor(invisible)

    def execmplayer(self, cmd): 
        open(self.mplayer_pipe, 'w').write(cmd + "\n")
        #~ self._mplayer.stdin.write(cmd)
        #~ print >>self._mplayer.stdin, cmd
    
    def setwid(self, wid):
        opt = ' -really-quiet -nojoystick -nolirc -slave -vo x11 -zoom'
        launch_command("mplayer %s -wid %s -idle -input file=%s" % (opt, wid, self.mplayer_pipe))
        
    def loadfile(self, filename):
        self.execmplayer("loadfile '%s'" % filename)

    def stop(self):
        self.execmplayer("stop")

    def pause(self):
        self.execmplayer("pause")

    def forward(self):
        self.execmplayer("seek +10 0")

    def backward(self):
        self.execmplayer("seek -10 0")      

    def forward2(self):
        self.execmplayer("seek +60 0")

    def backward2(self):
        self.execmplayer("seek -60 0")      

    def quit(self):
        self.execmplayer("quit")

    def osd(self):
        self.execmplayer("osd")

    def key_down_event(self, key):
        self.execmplayer("key_down_event %s" % key)
