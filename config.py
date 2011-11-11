#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gtk import gdk

from common import *

class Theme:
    
    def __init__(self, name):
        self.name = name

        self.fullscreen = 0
        
        self.image_bg = 'images/bg.jpg'
        
        if self.fullscreen:
            self.width = gdk.screen_width()
            self.height = gdk.screen_height()
        else:
            self.width = 1280
            self.height = 720
        
        self.browse_maxline = 11
        
        self.use_embed_mplayer = 1

        self.cmd_video = 'mplayer'
        self.cmd_video_opt = '-ao alsa -vo x11 -nojoystick -nolirc -quiet -zoom'
        
        self.cats = {'PICTURES':'/mnt/data/images/wallpaper',
                     'VIDEO':'/mnt/data/video',
                     'MUSIC':'/mnt/data/musique',
                    }
        
        self.ext = {}
        self.ext['VIDEO'] = ('avi', 'mpg', 'mpeg', 'mov', 'divx', 'wmv', 'vob',
                             'flv', '3gp', 'mp4', 'webm', 'ogv')
        self.ext['MUSIC'] = ('mp3', 'ogg', 'wav', 'wma')
        self.ext['PICTURES'] = ('png', 'jpg', 'jpeg', 'gif', 'svg', ' bmp')

        self.img_file = {'PICTURES': 'images/image-x-generic.svg',
                         'VIDEO': 'images/video-x-generic.svg',
                         'MUSIC': 'images/audio-x-generic.svg',
                        }

        self.img_menu = {'PICTURES': 'images/folder-pictures.svg',
                         'VIDEO': 'images/folder-videos.svg',
                         'MUSIC': 'images/folder-music.svg',
                         'PROGRAMS': 'images/text-x-python.svg',
                         'SYSTEM': 'images/applications-system.svg',
                        }
