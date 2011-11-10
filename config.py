#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gtk import gdk

from common import *

class Theme:
    
    def __init__(self, name):
        self.name = name

        self.fullscreen = 0
        
        #~ self.image_bg = 'images/dark-abstract.jpg'
        self.image_bg = 'images/1.jpg'
        
        if self.fullscreen:
            self.width = gdk.screen_width()
            self.height = gdk.screen_height()
        else:
            self.width = 1280
            self.height = 720
        
        self.browse_maxline = 11
        
        self.use_embed_mplayer = 1

        self.cmd_video = 'mplayer'
        self.cmd_video_opt = '-ao alsa -vo xv -fs -nolirc -quiet'
        
        self.cats = {'PICTURES':'/mnt/data/images/wallpaper',
                     'VIDEO':'/mnt/data/video',
                     'MUSIC':'/mnt/data/musique',
                    }
        
        self.ext = {}
        self.ext['VIDEO'] = ('avi', 'mpg', 'mpeg', 'mov', 'divx', 'wmv', 'vob',
                             'flv', '3gp', 'mp4', 'webm', 'ogv')
        self.ext['MUSIC'] = ('mp3', 'ogg', 'wav', 'wma')
        self.ext['PICTURES'] = ('png', 'jpg', 'jpeg', 'gif', 'svg', ' bmp')

        self.img_file = {'PICTURES': 'images/image-x.png',
                         'VIDEO': 'images/video-x.png',
                         'MUSIC': 'images/audio-x.png',
                        }

        self.img_menu = {'PICTURES': 'images/icon-pictures.png',
                         'VIDEO': 'images/icon-video.png',
                         'MUSIC': 'images/icon-music.png',
                         'PROGRAMS': 'images/icon-app.png',
                         'SYSTEM': 'images/icon-system.png',
                        }
