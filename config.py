#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gtk import gdk

class Theme:
    
    def __init__(self, name):
        self.name = name

        self.fullscreen = 0
        self.cats = {}
        self.ext = {}
        self.img_file = {}
        self.img_menu = {}
        
        self.image_bg = 'images/bg.jpg'
        
        if self.fullscreen:
            self.width = gdk.screen_width()
            self.height = gdk.screen_height()
        else:
            self.width = 1280
            self.height = 720
        
        self.browse_maxline = 11

        self.cmd_video = 'mplayer'
        self.cmd_video_opt = '-ao alsa -vo x11 -nojoystick -nolirc -quiet -zoom'

        self.cats['PICTURES'] = '/mnt/data/images/wallpaper'
        self.ext['PICTURES'] = ('png', 'jpg', 'jpeg', 'gif', 'svg', ' bmp')
        self.img_file['PICTURES'] = 'images/image-x-generic.svg'
        self.img_menu['PICTURES'] = 'images/folder-pictures.svg'
        
        self.cats['VIDEO'] = '/mnt/data/video'
        self.ext['VIDEO'] = ('avi', 'mpg', 'mpeg', 'mov', 'divx', 'wmv', 'vob',
                             'flv', '3gp', 'mp4', 'webm', 'ogv')
        self.img_file['VIDEO'] = 'images/video-x-generic.svg'
        self.img_menu['VIDEO'] = 'images/folder-videos.svg'
        
        
        self.cats['MUSIC'] = '/mnt/data/musique'
        self.ext['MUSIC'] = ('mp3', 'ogg', 'wav', 'wma')
        self.img_file['MUSIC'] = 'images/audio-x-generic.svg'
        self.img_menu['MUSIC'] = 'images/folder-music.svg'

        self.img_menu['PROGRAMS'] = 'images/text-x-python.svg'
        self.img_menu['SYSTEM'] = 'images/applications-system.svg'
