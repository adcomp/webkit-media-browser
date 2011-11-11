#!/usr/bin/env python
# -*- coding: utf-8 -*-

# module mplayer based on Pymp

import gtk
import sys
import os
import fcntl
import gobject
import re
import time
import subprocess

STATUS_TIMEOUT = 1000
STATUS_STREAM_TITLE_REGEXP = re.compile("ICY Info: StreamTitle='(.*?)';")

PIX_DATA = """/* XPM */
static char * invisible_xpm[] = {
"1 1 1 1",
"       c None",
" "};"""

#
#  Provides simple piped I/O to an mplayer process.
#
class MPlayer(gtk.DrawingArea):

    mplayerIn, mplayerOut = None, None
    eofHandler, statusQuery = 0, 0
    paused = False

    #
    #  Initializes this Mplayer.
    #
    def __init__(self, wmb):
        gtk.DrawingArea.__init__(self)
        self.wmb = wmb
        self.connect('realize', self._realize)

    def _realize(self, widget):
        color = gtk.gdk.Color('#000')
        # set bg color to black
        widget.modify_bg(gtk.STATE_NORMAL, color)
        # set xid for mplayer
        self.wid = str(long(widget.window.xid))

        # hide mouse cursor
        pix = gtk.gdk.pixmap_create_from_data(None, PIX_DATA, 1, 1, 1, color, color)
        invisible = gtk.gdk.Cursor(pix, pix, color, color, 0, 0)
        widget.window.set_cursor(invisible)

    #
    #   Plays the specified target.
    #
    def play(self, target):
        print target

        # Open pipe
        cmd = self.wmb.theme.cmd_video + ' ' + self.wmb.theme.cmd_video_opt + ' -slave -wid ' + self.wid
        cmd = cmd.split()
        cmd.append(target)
        
        p = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (self.mplayerIn, self.mplayerOut) = (p.stdin, p.stdout)

        fcntl.fcntl(self.mplayerOut, fcntl.F_SETFL, os.O_NONBLOCK)

        self.startEofHandler()
        self.startStatusQuery()
        
        if not self.wmb.cur_draw == 'video':
            self.wmb.update_status(target)

    #
    #  Issues command to mplayer.
    #
    def cmd(self, command):

        if not self.mplayerIn:
            return

        try:
            self.mplayerIn.write(command + "\n")
            self.mplayerIn.flush()  #flush pipe
        except StandardError:
            return

    #
    #  Toggles pausing of the current mplayer job and status query.
    #
    def pause(self):

        if not self.mplayerIn:
            return

        if self.paused:  #unpause
            self.startStatusQuery()
            self.paused = False
            #~ self.pymp.control.switchPlayStatus(1)

        else:  #pause
            self.stopStatusQuery()
            self.paused = True
            #~ self.pymp.control.switchPlayStatus(0)

        self.cmd("pause")

    #
    #  Seeks the amount using the specified mode.  See mplayer docs.
    #
    def seek(self, amount, mode=0):
        self.cmd("seek " + str(amount) + " " + str(mode))
        self.queryStatus()

    #
    #  Cleanly closes any IPC resources to mplayer.
    #
    def close(self):

        if self.paused:  #untoggle pause to cleanly quit
            self.pause()

        self.stopStatusQuery()  #cancel query
        self.stopEofHandler()  #cancel eof monitor

        self.cmd("quit")  #ask mplayer to quit

        try:
            self.mplayerIn.close()   #close pipes
            self.mplayerOut.close()
        except StandardError:
            pass

        self.mplayerIn, self.mplayerOut = None, None

        if not self.wmb.cur_draw == 'video':
            self.wmb.update_progressbar(0)
            self.wmb.update_status('')

    #
    #  Triggered when mplayer's stdout reaches EOF.
    #
    def handleEof(self, source, condition):

        self.stopStatusQuery()  #cancel query

        self.mplayerIn, self.mplayerOut = None, None

        #if self.pymp.playlist.continuous:  #play next target
        #   self.pymp.playlist.next(None, None)
        #else:  #reset progress bar
        #   self.pymp.control.setProgress(-1)
        if self.wmb.cur_draw == 'video':
            self.wmb.play_video()
        else:
            self.wmb.update_progressbar(0)
            self.wmb.update_status('')

        return False

    #
    #  Queries mplayer's playback status and upates the progress bar.
    #
    def queryStatus(self):

        self.cmd("get_percent_pos")  #submit status query
        self.cmd("get_time_pos")

        time.sleep(0.05)  #allow time for output

        line, percent, seconds = None, -1, -1

        while True:
            try:  #attempt to fetch last line of output
                line = self.mplayerOut.readline()
            except StandardError:
                break

            if not line:
                break

            if line.startswith("ANS_PERCENT_POSITION"):
                percent = int(line.replace("ANS_PERCENT_POSITION=", ""))

            if line.startswith("ANS_TIME_POSITION"):
                seconds = float(line.replace("ANS_TIME_POSITION=", ""))

            if line.startswith("ICY Info: StreamTitle="):  #resolve title for streams
                #~ self.pymp.playlist.set_track_title(STATUS_STREAM_TITLE_REGEXP.match(line).group(1) + ' (stream)')
                pass

        #~ self.pymp.control.setProgress(percent, seconds)
        if not self.wmb.cur_draw == 'video':
            self.wmb.update_progressbar(percent)
        return True

    #
    #  Inserts the status query monitor.
    #
    def startStatusQuery(self):
        self.statusQuery = gobject.timeout_add(STATUS_TIMEOUT, self.queryStatus)

    #
    #  Removes the status query monitor.
    #
    def stopStatusQuery(self):
        if self.statusQuery:
            gobject.source_remove(self.statusQuery)
        self.statusQuery = 0

    #
    #  Inserts the EOF monitor.
    #
    def startEofHandler(self):
        self.eofHandler = gobject.io_add_watch(self.mplayerOut, gobject.IO_HUP, self.handleEof)

    #
    #  Removes the EOF monitor.
    #
    def stopEofHandler(self):
        if self.eofHandler:
            gobject.source_remove(self.eofHandler)
        self.eofHandler = 0

#End of file
