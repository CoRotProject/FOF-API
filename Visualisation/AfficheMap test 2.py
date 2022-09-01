# coding: utf8
# Copyright 2020 Fabrice DUVAL
# Biblio
# https://docs.python-eve.org/en/stable/features.html
# https://docs.python-eve.org/en/stable/tutorials/custom_idfields.html
# https://www.youtube.com/watch?v=lc8NNJgeVjI
# https://www.youtube.com/watch?v=vIwpvkkvos0
# https://www.pygame.org/docs/ref/sprite.html
# https://opensource.com/article/17/12/game-python-moving-player

import pygame
import sys
# sys.path.append("..\\Commandes")
import commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

pygame.font.init()
successes, failures = pygame.init()
print("{0} successes and {1} failures".format(successes, failures))

myfont = pygame.font.SysFont(None, 18)

VMAX = 20

def updaterobotpos(factoryId, listerobot):
    notmoved = True
    for robot in listerobot:
        info = commandeAPI.getvalues(factoryId, "robot", robot[0])["transform2D"]
        if info["x"] != robot[1].xcm  != robot[1].xcm or info["y"] != robot[1].ycm or info["theta"] % 360 != robot[1].angle % 360:
            notmoved = False
            robot[1].movetocm(info["x"], info["y"], info["theta"])
    return notmoved

class RobotClass(pygame.sprite.Sprite):
    def __init__(self, name, shortname, screensize, resolution): # resolution en cm/pixel
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.textsurface = myfont.render(shortname, True, (255, 0, 0))
        self.angle = 0  # angle
        self.moveangle = 0
        self.movetox = 0
        self.movetoy = 0
        self.transform_mtopixelcoef = [100 / resolution, 280, -100 / resolution, 650-80,] # [a, b, c, d] ==> Xpixel = ax + b en Ypixel = cy + d
        # self.frame = 0 # count frames
        image = pygame.image.load('mir100-pixilart.png') # resolution = 1pt/cm
        rectima = image.get_rect()
        rectima.w /= resolution
        rectima.h /= resolution
        self.rect = rectima
        self.imageBase = pygame.transform.scale(image, (rectima.w, rectima.h))
        self.image = self.imageBase
        self.textrect = self.textsurface.get_rect()
        self.textrect.centerx = rectima.centerx
        self.textrect.centery = rectima.centery
        # self.image.blit(self.textsurface, self.textrect)
        self.screensize = screensize

    def moveto(self, x, y, theta=0):
        '''
        control player movement
        '''
        self.movetox = x
        self.movetoy = y
        self.moveangle = theta

    def fget_xcm(self):
        return (self.rect.x - self.transform_mtopixelcoef[1]) / self.transform_mtopixelcoef[0]

    def fget_ycm(self):
        return (self.rect.y - self.transform_mtopixelcoef[3]) / self.transform_mtopixelcoef[2]

    xcm = property(fget=fget_xcm,doc="position x en cm")
    ycm = property(fget=fget_ycm,doc="position y en cm")

    def movetocm(self, x, y, theta=0):
        '''
        control player movement
        '''
        self.movetox = self.transform_mtopixelcoef[0] * x + self.transform_mtopixelcoef[1]
        self.movetoy = self.transform_mtopixelcoef[2] * y + self.transform_mtopixelcoef[3]
        self.moveangle = theta

    def update(self):
        '''
        Update sprite position
        '''
        moved = False
        if (self.moveangle - self.angle) % 360:
            print("{} {}° ==> {}°".format(self.name, self.angle, self.moveangle, ))
            self.angle = self.moveangle % 360 # angle entre 0 et 359
            newimage = pygame.transform.rotate(self.imageBase, self.angle)
            taille = newimage.get_rect()
            dx = (taille.w - self.rect.w) / 2
            dy = (taille.h - self.rect.h) / 2
            self.image = newimage.subsurface(pygame.Rect(dx, dy, self.rect.w, self.rect.h))
            self.image.blit(self.textsurface, self.textrect)
            moved = True
            
        if self.rect.x != self.movetox or self.rect.y != self.movetoy:
            print("{} ({},{}) ==> ({},{})".format(self.name, self.rect.x, self.rect.y, self.movetox, self.movetoy, ))
            self.rect.x = self.movetox
            self.rect.y = self.movetoy
            if self.rect.x < 0:
                self.rect.x = 0
            if self.rect.right > self.screensize.right:
                self.rect.x = self.screensize.right - self.rect.w
            if self.rect.y < 0:
                self.rect.y = 0
            if self.rect.bottom > self.screensize.bottom:
                self.rect.y = self.screensize.bottom - self.rect.h
            moved = True
        return moved

background = pygame.image.load("Madrillet 500x325.png") # correspond à 1pt/5cm ==> 25mx16m25

window_width = 1000
window_height = 650
REALW = 25.0
REALH = 16.25
ratio = window_width / REALW
deltax = 0
deltay = 0

size = (window_width, window_height)
screen = pygame.display.set_mode(size) # ==> 1pt/2.5cm ==> toujours 25mx16m25
backdropbox = screen.get_rect()

background = pygame.transform.scale(background, size)
pygame.display.set_caption("Map Madrillet Atelier Flexible")

clock = pygame.time.Clock()
FPS = 2  # Frames per second.

couleur = {"BLACK" : (0, 0, 0), "WHITE" : (255, 255, 255), "RED" : (255, 0, 0), "GREEN" : (0, 255, 0), "BLUE" : (0, 0, 255)}

robot_list = pygame.sprite.Group()

robotMir1 = RobotClass("Robot Mir100_ARM", "Arm", backdropbox, 2.5)
robot_list.add(robotMir1)

robotMir2 = RobotClass("Robot Mir100_CAPITAINE", "Hook", backdropbox, 2.5)
robot_list.add(robotMir2)

robotMir1.moveto(100, 100)
robotMir2.moveto(100, 200)


screen.blit(background, [0, 0])

Continuer = True

GoVers = 0
Deplacement = 2

pygame.display.flip()

#mode reel
factoryId = commandeAPI.findfactory(name="Factory LINEACT Test Fabrice")[0]
robots = []
robots.append([commandeAPI.findINfactory(factoryId, "resource", name="mir100_Arm")[0], robotMir1])
robots.append([commandeAPI.findINfactory(factoryId, "resource", name="mir100_Capitaine")[0], robotMir2])

            

while Continuer:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Continuer = False
            break

    updaterobotpos(factoryId, robots)
    screen.blit(background, [0, 0])
    # screen.fill(BLACK)
    # screen.blit(image, rect)
    robotMir1.update()
    robotMir2.update()
    robot_list.draw(screen)
    pygame.display.flip()
    # pygame.display.update(rect.inflate(Deplacement*3,Deplacement*3))  # Or pygame.display.flip()
