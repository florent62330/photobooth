#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Fichier: potograph.py
# Cree le 27 mai 2015 19:15:00


"""

Auteur :      thuban (thuban@yeuxdelibad.net)  
licence :     GNU General Public Licence

Description :
    prendre des photos avec un RPi
"""

import sys
import os
import time
import picamera
import io
import pygame
from buzz import *
from pygame.locals import *


size = w, h = 640, 480
black = (0, 0, 0)
white = (255, 255, 255)
validbuttons = [0,1,2,3] # buttons to valid
startbutton = 9 # button start to print

#ajout
#xSize, ySize = 640, 400
xSize, ySize = 1280, 1024
rgb = bytearray(xSize * ySize * 4)
sizeData =  [(1440, 1080), (xSize, ySize), (0.0, 0.0, 1.0, 1.0)]

def findlastimg():
    tmp = 0
    for f in os.listdir("."):
        if f.endswith('.JPG') or f.endswith('.jpg')\
                or f.endswith('.PNG') or f.endswith('.png'):
            lastaccess = os.stat(f).st_ctime
            if lastaccess > tmp:
                img = f
                tmp = lastaccess

    return(img)

def cleanfolder():
    for f in os.listdir("."):
        if f.endswith(".jpg") or f.endswith(".JPG"):
            os.remove(f)

class interface():
    def __init__(self, device):

        pygame.init()
        self.displayinfo = pygame.display.Info()
        self.xw, self.yw = self.displayinfo.current_w, self.displayinfo.current_h
        size = (self.xw, self.yw) # to have full screen size
        self.screen = pygame.display.set_mode(size)
        self.device = device
        self.filename = "" # image
        self.camera = picamera.PiCamera()

    def photo(self):
        #cleanfolder()
        self.showtext("3")
        pygame.time.wait(1000)
        self.showtext("2")
        pygame.time.wait(1000)
        self.showtext("1")
        pygame.time.wait(1000)
        self.showtext("Photo!", white, black)
	self.filename = "{}.jpg".format(time.strftime("%H-%M-%S-%d%m%Y"))
        self.camera.capture(self.filename)

        if os.path.isfile(self.filename):
            img=pygame.image.load(self.filename).convert()
            iw = img.get_width()
            ih = img.get_height()

            if ih < self.yw :
                r = self.yw / ih
                img = pygame.transform.scale(img, (iw * r, ih * r))
                iw = img.get_width()
                ih = img.get_height()
            elif ih > self.yw :
                r = ih / self.yw 
                img = pygame.transform.scale(img, (iw / r, ih / r))
                iw = img.get_width()
                ih = img.get_height()

            self.screen.fill(black)
            self.screen.blit(img,(self.xw/2 - iw/2, self.yw/2 - ih/2))
            pygame.display.flip() 

            pygame.time.wait(1000)

    def readImgFromCamera(self):
        stream = io.BytesIO() # Capture into in-memory stream
        self.camera.capture(stream, use_video_port=True, format='rgba')
        stream.seek(0)
        stream.readinto(rgb)
        stream.close()
        img = pygame.image.frombuffer(rgb[0: (xSize * ySize * 4)], sizeData[1], 'RGBA')
        return img

    def start(self):
        pygame.key.set_repeat(35, 65)
        pygame.mouse.set_visible(False)

        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN,\
                                pygame.MOUSEBUTTONDOWN])
        self.fontwidth=72
        self.font = pygame.font.Font(pygame.font.get_default_font(), self.fontwidth)
        self.fontheight = self.font.get_height()

        # Initialisation du joystick
        self.nbJoy = pygame.joystick.get_count()
        if self.nbJoy == 1:
            self.monJoy = pygame.joystick.Joystick(0)
            self.monJoy.init()
        # Premier affichage
        #self.showtext("Appuyez sur un bouton")
        buzz1 = Buzz()
        i = 0

        while True:
            #ADD
            buzz1.setlight(0, state=True)
            img = self.readImgFromCamera()
            self.screen.blit(img, (0, 0))
            pygame.display.flip()
            r = buzz1.readcontroller(timeout=50)
            if r != None and i == 0:
                i = 1
                buzz1.setlight(0)
                self.photo()
            elif r != None:
                i = 0
            #END ADD
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.photo()
                if event.type == pygame.QUIT:
                    buzz1.setlight(0)
                    print('� la prochaine!')
                    pygame.quit()
                    sys.exit()

                elif (event.type == KEYDOWN and event.key == K_ESCAPE):
                    print('� la prochaine!')
                    buzz1.setlight(0)
                    pygame.quit()
                    sys.exit()

                elif event.type == KEYDOWN:
                    self.photo()

                break
            pygame.event.clear()
            pygame.time.wait(100)
            pygame.display.update()
                    

    def showtext(self, text, bg=black, fg=white):
        self.screen.fill(bg)
        x = (self.xw / 2) - (self.fontwidth * len(text) / 4)
        y = (self.yw / 2) - self.fontheight
        self.screen.blit(self.font.render(text,1, fg),(x,y))

        pygame.display.flip()

def showhelp():
    print("usage {} <webcam|camera>".format(sys.argv[0]))
    sys.exit(1)

def main():

    if len(sys.argv) != 2:
        showhelp()
    else:
        device = sys.argv[1]
        if not device in ['webcam','camera']:
            showhelp()
    potograph = interface(device)
    potograph.start()

    return 0

if __name__ == '__main__':
	main()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
