#!/usr/bin/env python

import sys, os, fcntl, gobject, re, time, subprocess

MPLAYERCONFFILE = os.path.expanduser("~/.pymp/mplayer")

STATUS_TIMEOUT = 1000
STATUS_STREAM_TITLE_REGEXP = re.compile("ICY Info: StreamTitle='(.*?)';")

#
#  Provides simple piped I/O to an mplayer process.
#
class Mplayer:

	pymp, mplayerIn, mplayerOut = None, None, None
	eofHandler, statusQuery = 0, 0
	paused = False

	#
	#  Initializes this Mplayer with the specified Pymp.
	#
	def __init__(self, pymp):
		self.pymp = pymp

	#
	#   Plays the specified target.
	#
	def play(self, target):

		# Open pipe
		p = subprocess.Popen(['mplayer -slave -quiet "' + target + '" -include "' + MPLAYERCONFFILE + '" 2>/dev/null'], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		(self.mplayerIn, self.mplayerOut) = (p.stdin, p.stdout)

		fcntl.fcntl(self.mplayerOut, fcntl.F_SETFL, os.O_NONBLOCK)

		self.startEofHandler()
		self.startStatusQuery()
		self.pymp.control.switchPlayStatus(1)

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
			self.pymp.control.switchPlayStatus(1)

		else:  #pause
			self.stopStatusQuery()
			self.paused = True
			self.pymp.control.switchPlayStatus(0)

		self.cmd("pause")

	#
	#  Seeks the amount using the specified mode.  See mplayer docs.
	#
	def seek(self, amount, mode=0):
		self.pymp.mplayer.cmd("seek " + str(amount) + " " + str(mode))
		self.pymp.mplayer.queryStatus()

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
			self.mplayerIn.close()	 #close pipes
			self.mplayerOut.close()
		except StandardError:
			pass

		self.mplayerIn, self.mplayerOut = None, None
		self.pymp.control.setProgress(-1)  #reset bar
		self.pymp.control.switchPlayStatus(0)

	#
	#  Triggered when mplayer's stdout reaches EOF.
	#
	def handleEof(self, source, condition):

		self.stopStatusQuery()  #cancel query

		self.mplayerIn, self.mplayerOut = None, None

		if self.pymp.playlist.continuous:  #play next target
			self.pymp.playlist.next(None, None)
		else:  #reset progress bar
			self.pymp.control.setProgress(-1)

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
				self.pymp.playlist.set_track_title(STATUS_STREAM_TITLE_REGEXP.match(line).group(1) + ' (stream)')

		self.pymp.control.setProgress(percent, seconds)
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
