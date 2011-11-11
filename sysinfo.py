#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commands
import re
import os.path

def find_all(text):
    match = re.findall(r'(?:[a-z0-9]{2}:[a-z0-9]{2}.[a-z0-9].*:)(.*)(?:\(rev.*\))', text)
    if match:
        return match[0]
    else:
        match = re.findall(r'(?:[a-z0-9]{2}:[a-z0-9]{2}.[a-z0-9].*:)(.*)', text)
        if match:
            return match[0]
        else:
            return 'None'

def get_html():
    KERNEL = commands.getoutput("uname -r")

    if os.path.exists('/usr/bin/lsb_release'):
        RELEASE = commands.getoutput("lsb_release -r").split('\t')[1]
        CODENAME = commands.getoutput("lsb_release -c").split('\t')[1]
    else:
        RELEASE = commands.getoutput("uname -v")
        CODENAME = commands.getoutput("uname -mo")

    HOSTNAME = commands.getoutput("hostname")
    #~ HOSTNAME = commands.getoutput("echo $HOSTNAME")
    CPU = commands.getoutput("grep 'model name' /proc/cpuinfo | head -n 1").split(':')[1]
    MEM_TOTAL = commands.getoutput("free -m | grep 'Mem:' | awk '{print $2}'")
    MEM_FREE = commands.getoutput("free -m | grep 'cache:' | awk '{print $4}'")

    ## Graphic card
    VGA = commands.getoutput("lspci | grep VGA")
    VGA = find_all(VGA)


    NETWORKS = commands.getoutput("lspci | grep Ethernet").split('\n')
    NETWORK = find_all(NETWORKS[0])

    #~ AUDIO = commands.getoutput("lspci | grep [a-A]udio")
    AUDIO = commands.getoutput("lspci | grep Audio")
    AUDIO = find_all(AUDIO)

    if not AUDIO:
        AUDIO = commands.getoutput("lspci | grep audio")
        AUDIO = find_all(AUDIO)

    if not AUDIO:
        AUDIO = commands.getoutput("lspci | grep Multimedia")
        AUDIO = find_all(AUDIO)

    html = '<div class="sysinfo">'
    html += "<h1>Kernel :</h1><p>%s</p>" % (KERNEL)
    html += "<h1>Release :</h1><p>%s ( <i>%s</i> )</p>" %(RELEASE, CODENAME)
    html += "<h1>Hostname :</h1><p>%s</p>" % (HOSTNAME)

    html += "<h1>Cpu :</h1><p>%s</p>" % (CPU)
    html += "<h1>Mem :</h1><p>%sMB ( <i>%sMB free</i>)</p>" % (MEM_TOTAL, MEM_FREE)
    html += "<h1>Graphics :</h1><p>%s</p>" % (VGA)
    html += "<h1>Audio :</h1><p>%s</p>" % (AUDIO)
    html += "<h1>Network :</h1><p>%s</p>" % (NETWORK)

    if len(NETWORKS) > 1:
        end = len(NETWORKS)-1
        for card in NETWORKS[1:]:
            html += "%s" % (find_all(card))

    """
    DISKS = commands.getoutput("df -h | grep ^/dev/sd[a-z] --color=never").split('\n')

    for disk in DISKS:
        disk_tmp = disk.replace('/dev/','')
        html += "<h1>%s</p>" % (disk_tmp)
    """
    
    html += "</div>"
    return html
