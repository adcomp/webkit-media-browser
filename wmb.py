#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Media Browser [ gtk, webkit, mplayer ]
#
#  by ADcomp <david.madbox@gmail.com>
#
#  This program is distributed under the terms of the GNU General Public License
#  For more info see http://www.gnu.org/licenses/gpl.txt
##

import gtk

import os
import os.path
import sys

from config import *
import mplayer
import sysinfo

try:
    import webkit
    import jswebkit
except:
    print('Error : Install python-webkit python-jswebkit')
    sys.exit()

realpath = os.path.dirname(os.path.realpath( __file__ ))
os.chdir(realpath)

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

class WebkitMediaBrowser():

    def __init__(self):

        self.load_config()
        self.ui()

    def load_config(self):
        #~ self.cats = ('PICTURES','MUSIC','VIDEO','PROGRAMS','SYSTEM')
        self.cats = ('PICTURES','MUSIC','VIDEO','SYSTEM')

        self.cur_draw = 'menu'
        self.data = []
        self.cur_cat = ''
        self.path = []
        
        self.bpos_tab = []
        self.browser_pos = 0
        self.browser_offset = 0

        # load theme from config 
        self.theme = Theme('default')
        
    def ui(self):
        ##  main window 
        self.window = gtk.Window()
        self.window.set_border_width(0)
        color = gtk.gdk.color_parse('#000')
        self.window.modify_bg(gtk.STATE_NORMAL, color)
        
        if self.theme.fullscreen:
            self.window.fullscreen()
        else:
            self.window.resize(self.theme.width, self.theme.height)

        self.window.show()

        self.box = gtk.HBox()
        self.box.show()
        self.window.add(self.box)

        self.webview = webkit.WebView()
        self.webview.show()
        #~ self.webview.connect("navigation-policy-decision-requested", self.nav_request)
        self.webview.connect('load-finished', self.onLoad)
        #~ self.webview.connect('realize', self._realize)
        #~ self.webview.set_size_request(self.theme.width, self.theme.height)
        
        self.webview.open('%s/themes/%s/index.html' % (realpath, self.theme.name))

        self.box.pack_start(self.webview)

        if self.theme.use_embed_mplayer:
            self.mplayer = mplayer.MPlayer(self)
            self.box.pack_start(self.mplayer)
            self.mplayer.realize()

        ##  signal/callback
        self.window.connect('destroy', self._quit)
        self.window.connect("key-press-event", self.onkeypress)
        #~ self.window.connect('size-allocate', self._size_allocate)
        #~ self.window.connect('realize', self._realize)

    def _size_allocate(self, widget, allocation):
        #~ print allocation
        pass

    def _realize(self, widget):
        pass

    def onLoad(self, webview, frame):
        #~ print('load finished ..')
        if self.theme.image_bg:
            bg = '<img src="%s"' % self.theme.image_bg
            bg += ' width="100%" height="100%">'
            self.update_content('background', bg)
            
        self.draw_list()

    def nav_request(self, webview, frame, request, navigation_action, policy_decision):
        uri = request.get_uri()

    def draw_list(self):
        self.data = []
        self.data_list = []
        
        if self.cur_draw == 'menu':

            for cat in self.cats:
                self.data.append(cat)

        else:

            path = ''
            for p in self.path: path += p + '/'
            
            ls = os.listdir(path)
            
            # split dir/file
            rep = ['..']
            fich = []
            
            for l in ls:
                if os.path.isdir(path + '/' + l):
                    rep.append(l)
                else:
                    ext = get_ext(l)
                    if ext in self.theme.ext[self.cur_cat]:
                        fich.append(l)
            
            rep.sort()
            fich.sort()
            
            ls = rep + fich
            
            for rp in rep:
                self.data.append(Entry(rp, 'DIR'))
            for f in fich:
                self.data.append(Entry(f, 'FILE'))
                
        self.to_html()

    def get_html(self):
        frame = self.webview.get_main_frame()
        ctx = jswebkit.JSContext(frame.get_global_context())
        text = ctx.EvaluateScript("document.body.innerHTML")
        return text

    def to_html(self):
        #~ print 'to html ..'
        
        if self.cur_draw == 'menu':
            
            html = '<div id="menu"><ul>'
            
            index = 0
            for i in self.data:
                
                if index == self.browser_pos:
                    html += "<li class=\"menufocus\"><a href=\"\">%s</a></li>" % i
                    preview = '<img src=\"%s\">' % self.theme.img_menu[i]
                else:
                    html += '<li class=\"menu\"><a href=\"\">%s</a></li>' % i
                index += 1
                
            html += '</div>'
            
            self.update_content('items', '')
        else:
          
            path = ''
            for p in self.path: path += p + '/'
            
            fullpath = path + '/' + self.data[self.browser_pos+self.browser_offset].name
            
            html = '<div id="browser"><ul>'
            
            index = 0

            for i in range(self.theme.browse_maxline):

                if (i+self.browser_offset) == len(self.data):
                    break

                txt = self.data[i+self.browser_offset].name.replace('_','<i>_</i>')
                txt = txt.replace(' ','<i>_</i>')
                    
                if index == self.browser_pos:
                    html += '<li class=\"browserfocus\"><a href=\"\">%s</a></li>' % txt
                    
                    if self.data[i+self.browser_offset].xtype == 'DIR':
                        
                        if self.cur_cat == 'MUSIC':
                            cover_exist = False
                            for c in ('cover.jpg', 'cover.png','folder.jpg','folder.png'):
                                p = os.path.abspath(fullpath + '/' + c)
                                if os.path.exists(p):
                                    preview = '<img src=\"%s\">' % p
                                    cover_exist = True
                            if not cover_exist:
                                preview = '<img src=\"%s\">' % self.theme.img_menu[self.cur_cat]
                        else:
                            preview = '<img src=\"%s\">' % self.theme.img_menu[self.cur_cat]
                            
                    else:
                        
                        if self.cur_cat == 'PICTURES':
                            preview = '<img src=\"%s\">' % fullpath
                            if self.cur_draw == 'picture':
                                self.show_image(fullpath)
                        else:
                            preview = '<img src=\"%s\">' % self.theme.img_file[self.cur_cat]
                            
                else:
                    html += '<li class=\"browser\"><a href=\"\">%s</a></li>' % txt
                    
                index += 1
                
                # ( xx/xx ) items in this directory ..
                if self.browser_pos == 0 and self.browser_offset == 0:
                    items = '( <b>' + str(len(self.data)-1) + '</b> ) items'
                else:
                    items = '( <b>' + str(self.browser_pos + self.browser_offset) + ' / ' + str(len(self.data)-1) + '</b> ) items'
                self.update_content('items', items)
                
            html += '</ul></div>'

        self.update_content('page', html)
        self.update_content('preview', preview)
        
        #~ print preview
        #~ print html
        #~ return html

    def onkeypress(self, widget, event):
        #~ print 'onkeypress .. cur_draw=', self.cur_draw
        
        if self.cur_draw == 'system':
            self.cur_draw = 'menu'
            self.to_html()
            return

        if event.keyval == gtk.keysyms.F5:
            print self.get_html()
            return

        if event.keyval == gtk.keysyms.Escape or event.keyval == gtk.keysyms.BackSpace:
            self.cmd_escape()
        elif event.keyval == gtk.keysyms.Page_Up:
            self.cmd_page_up()
        elif event.keyval == gtk.keysyms.Page_Down:
            self.cmd_page_down()
        elif event.keyval == gtk.keysyms.Up:
            self.cmd_up()
        elif event.keyval == gtk.keysyms.Down:
            self.cmd_down()
        elif event.keyval == gtk.keysyms.Left:
            self.cmd_left()
        elif event.keyval == gtk.keysyms.Right:
            self.cmd_right()
        elif event.keyval == gtk.keysyms.space:
            self.cmd_space()
        elif event.keyval == gtk.keysyms.o:
            self.cmd_o()
        elif event.keyval == gtk.keysyms.x:
            self.mplayer.close()
        elif event.keyval == gtk.keysyms.Home:
            if self.cur_draw == 'picture':
                self.flip_image()
            if not self.cur_draw == 'video':
                self.cur_draw = 'menu'
                self.browser_pos = 0
                self.bpos_tab = []
                self.draw_list()
            
        if not self.cur_draw == 'video':
            self.to_html()
            
        if event.keyval == gtk.keysyms.Return:
            self.cmd_enter()
            
        #~ elif event.keyval == gtk.keysyms.f:
            #~ print 'F'

    def cmd_escape(self):
        if self.cur_draw == 'picture':
            self.flip_image()
        elif self.cur_draw == 'video':
            self.play_video()
        elif self.cur_draw == 'menu':
            self._quit()
        else:
            self.cmd_back()

    def cmd_enter(self):
        if self.cur_draw == 'picture':
            self.flip_image()
            
        elif self.cur_draw == 'video':
            self.mplayer.pause()
            
        elif self.cur_draw == 'menu':
            
            self.cur_cat = self.cats[self.browser_pos]
            
            if self.cur_cat == 'SYSTEM':
                self.cur_draw = 'system'
                self.update_content('page', sysinfo.get_html())
            else:
                self.cur_draw = 'browser'
                self.bpos_tab.append((self.browser_pos, 0))
                self.path = [self.theme.cats[self.cats[self.browser_pos]]]
                self.browser_pos = 0
                self.browser_offset = 0
                self.draw_list()
            
        elif self.cur_draw == 'browser':
            
            if self.browser_pos == 0 and self.browser_offset == 0:
                self.cmd_back()
                
            else:
                path = ''
                for p in self.path: path += p + '/'
                
                fullpath = path + self.data[self.browser_pos+self.browser_offset].name
                #~ fullpath = fullpath.replace("'", "\\'")
                #~ fullpath = fullpath.replace(" ", "\ ")
                #~ fullpath = "'" + fullpath + "'"
                
                # directory .. 
                if os.path.isdir(fullpath):
                    #~ print 'Dir - ' + fullpath
                    self.path.append(self.data[self.browser_pos+self.browser_offset].name)
                    self.bpos_tab.append((self.browser_pos, self.browser_offset))
                    self.browser_pos = 0
                    self.browser_offset = 0
                    self.draw_list()

                # file ..
                else:
                    #~ print 'File - ' + fullpath
                    if self.cur_cat == 'VIDEO':
                        if self.theme.use_embed_mplayer:
                            self.play_video(fullpath)
                        else:
                            cmd = self.theme.cmd_video + " " + self.theme.cmd_video_opt + " "
                            cmd += "'" + fullpath + "'"
                            launch_command(cmd)
                        
                    elif self.cur_cat == 'PICTURES':
                        self.show_image(fullpath)
                        
                    elif self.cur_cat == 'MUSIC':
                        self.play_song(fullpath)

    def cmd_up(self):
        if self.cur_draw == 'video':
            self.mplayer.seek(60)
            
        elif self.cur_draw == 'menu':
            self.browser_pos -= 1
            if self.browser_pos == -1:
                self.browser_pos = len(self.cats)-1
        else:
            
            if self.browser_pos < int(self.theme.browse_maxline/2):
                self.browser_pos -= 1
                
                if self.browser_pos == -1:
                    if self.browser_offset == 0:

                        if len(self.data)<= self.theme.browse_maxline:
                            self.browser_pos = len(self.data)-1
                        else:
                            self.browser_offset = len(self.data) - self.theme.browse_maxline
                            self.browser_pos = self.theme.browse_maxline - 1
            
            elif self.browser_pos > int(self.theme.browse_maxline/2):
                self.browser_pos -= 1
            else:
                if not (self.browser_offset + self.theme.browse_maxline == len(self.data)):
                    if self.browser_offset == 0:
                        self.browser_pos -= 1
                    else:
                        self.browser_offset -= 1
                else:
                    self.browser_offset -= 1
                
    def cmd_down(self):
        if self.cur_draw == 'video':
            self.mplayer.seek(-60)

        else:
            if len(self.data) <= self.theme.browse_maxline:
                self.browser_pos += 1
                
                if self.browser_pos == len(self.data):
                    self.browser_pos = 0
            
            else:
                if self.browser_pos < (self.theme.browse_maxline/2):
                    self.browser_pos += 1
                else:
                    if (self.browser_offset + self.theme.browse_maxline) == len(self.data):
                        self.browser_pos += 1
                        if (self.browser_offset + self.browser_pos) == len(self.data):
                            self.browser_pos = 0
                            self.browser_offset = 0
                    else:
                        self.browser_offset += 1

    def cmd_goto(self):
        pass

    def cmd_o(self):
        if self.cur_draw == 'video':
            self.mplayer.cmd('osd')

    def cmd_space(self):
        if self.cur_draw == 'video':
            self.mplayer.pause()

    def cmd_left(self):
        if self.cur_draw == 'video':
            self.mplayer.seek(-10)
        else:
            self.cmd_escape()

    def cmd_right(self):
        if self.cur_draw == 'video':
            self.mplayer.seek(10)
        else:
            self.cmd_enter()

    def cmd_page_up(self):
        if not self.cur_draw == 'browser':
            return
            
        if (self.browser_pos + self.browser_offset - self.theme.browse_maxline) > 0:
            self.browser_offset -= self.theme.browse_maxline
            self.draw_list()

    def cmd_page_down(self):
        if not self.cur_draw == 'browser':
            return
            
        if len(self.data) > (self.browser_pos + self.browser_offset + self.theme.browse_maxline):
            self.browser_offset += self.theme.browse_maxline
            self.draw_list()
            

    def cmd_back(self):
        
        if len(self.path) == 1:
            self.cur_draw = 'menu'
        else:
            self.path = self.path[:-1]
            
        self.browser_pos = self.bpos_tab[-1][0]
        self.browser_offset = self.bpos_tab[-1][1]
        self.bpos_tab = self.bpos_tab[:-1]

        self.draw_list()

    def update_progressbar(self, percent):
        if percent == -1:
            return

        html = '<div class="meter-value" style="background-color: #1E90FF; width:'
        html += str(int(percent)) + '%;">'
        if percent:
            html += '<div class="meter-text">' + str(int(percent)) + '%</div>'
        html += '</div>'
        self.update_content('progressbar', html)

    def play_video(self, target=None):
        if self.cur_draw == 'video':
            self.mplayer.close()
            self.mplayer.hide()
            self.webview.show()
            self.cur_draw = 'browser'
        else:
            self.mplayer.close()
            self.webview.hide()
            self.mplayer.show()
            self.cur_draw = 'video'
            self.mplayer.play(target)

    def play_song(self, target):
        self.mplayer.close()
        self.mplayer.play(target)
        
    def show_image(self, image):
        html = '<h1>' + image.split('/')[-1] + '</h1>'
        html += '<img src="%s">' % image
        self.update_content('imagecell', html)
        if self.cur_draw == 'browser':
            self.flip_image()
        
    def flip_image(self):
        #~ print 'flip_image .. cur_draw=', self.cur_draw
        if self.cur_draw == 'browser':
            script = "div_hide = document.getElementById(\"container\");" 
            script += "div_hide.style.display = 'none';"
            script += "div_show = document.getElementById(\"imageviewer\");" 
            script += "div_show.style.display = 'table';"
            self.cur_draw = 'picture'
        else:
            script = "div_hide = document.getElementById(\"imageviewer\");" 
            script += "div_hide.style.display = 'none';"
            script += "div_show = document.getElementById(\"container\");" 
            script += "div_show.style.display = 'block';"
            self.cur_draw = 'browser'

        self.webview.execute_script(script)

    def update_content(self, div, html):
        script = "div_content = document.getElementById(\"%s\");" % div
        script += "div_content.innerHTML= \"%s\"; " % html.replace('"', '\\"')
        self.webview.execute_script(script)

    def update_status(self, name):
        html = name.split('/')[-1]
        self.update_content('status', html)
        
    def _quit(self, widget=None):
        if self.theme.use_embed_mplayer:
            self.mplayer.close()
        gtk.main_quit()

    def main(self):
        gtk.main()

WebkitMediaBrowser().main()
