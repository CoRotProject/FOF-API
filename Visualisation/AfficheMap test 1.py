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

VMAX = 20

class RobotClass(pygame.sprite.Sprite):
    def __init__(self, screensize):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0 # move along X
        self.movey = 0 # move along Y
        self.moveangle = 0 # angle vitesse
        self.angle = 0  # angle
        # self.frame = 0 # count frames
        image = pygame.image.load('mir100-pixilart.png') # resolution = 1pt/cm
        rectima = image.get_rect()
        rectima.w /= 2.5
        rectima.h /= 2.5
        self.rect = rectima
        self.imageBase = pygame.transform.scale(image, (rectima.w, rectima.h))
        self.image = self.imageBase
        self.screensize = screensize

    def control(self, x, y, theta=0):
        '''
        control player movement
        '''
        self.movex += x
        self.movex = max(min(VMAX, self.movex), -VMAX)
        self.movey += y
        self.movey = max(min(VMAX, self.movey), -VMAX)
        self.moveangle += theta
        self.moveangle = max(min(VMAX, self.moveangle), -VMAX)

    def update(self):
        '''
        Update sprite position
        '''
        if self.moveangle != 0:
            self.angle = (self.angle + self.moveangle) % 360 # angle entre 0 et 359
            newimage = pygame.transform.rotate(self.imageBase,self.angle)
            taille = newimage.get_rect()
            dx = (taille.w - self.rect.w) / 2
            dy = (taille.h - self.rect.h) / 2
            self.image = newimage.subsurface(pygame.Rect(dx, dy, self.rect.w, self.rect.h))
            
        self.rect.x = self.rect.x + self.movex
        self.rect.y = self.rect.y + self.movey
        print("({},{},{}) --> ({},{},{})".format(self.rect.x, self.rect.y, self.angle, self.movex, self.movey, self.moveangle,))
        if self.rect.x < 0:
            self.rect.x = 0
            self.movex = max(0, self.movex)
        if self.rect.right > self.screensize.right:
            self.rect.x = self.screensize.right - self.rect.w
            self.movex = min(0, self.movex)
        if self.rect.y < 0:
            self.rect.y = 0
            self.movey = max(0, self.movey)
        if self.rect.bottom > self.screensize.bottom:
            self.rect.y = self.screensize.bottom - self.rect.h
            self.movey = min(0, self.movey)


successes, failures = pygame.init()
print("{0} successes and {1} failures".format(successes, failures))
background = pygame.image.load("Madrillet 500x325.png") # correspond à 1pt/5cm ==> 25mx16m25

window_width = 1000
window_height = 650
REALW = 25.0
REALH = 16.25
ratio = window_width / REALW

size = (window_width, window_height)
screen = pygame.display.set_mode(size) # ==> 1pt/2.5cm ==> toujours 25mx16m25
backdropbox = screen.get_rect()

background = pygame.transform.scale(background, size)

pygame.display.set_caption("Map Madrillet Atelier Flexible")

clock = pygame.time.Clock()
FPS = 5  # Frames per second.

couleur = {"BLACK" : (0, 0, 0), "WHITE" : (255, 255, 255), "RED" : (255, 0, 0), "GREEN" : (0, 255, 0), "BLUE" : (0, 0, 255)}

robotMir = RobotClass(backdropbox)
robotMir.rect.x = 100
robotMir.rect.y = 100
robot_list = pygame.sprite.Group()
robot_list.add(robotMir)
stepMir = 1


# rect = pygame.Rect((0, 0), (32, 32))
# image = pygame.Surface((32, 32))
# image.fill(couleur["RED"])

screen.blit(background, [0, 0])

Continuer = True

GoVers = 0
Deplacement = 2

pygame.display.flip()

while Continuer:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Continuer = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP,): #z
                GoVers |= 1
                GoVers &= 63-2
            elif event.key in (pygame.K_s, pygame.K_DOWN,):
                GoVers |= 2
                GoVers &= 63-1
            elif event.key in (pygame.K_a, pygame.K_LEFT,): #q
                GoVers |= 4
                GoVers &= 63-8
            elif event.key in (pygame.K_d, pygame.K_RIGHT,):
                GoVers |= 8
                GoVers &= 63-4
            elif event.key in (pygame.K_q,): #a
                GoVers |= 16
                GoVers &= 63-32
            elif event.key in (pygame.K_e,):
                GoVers |= 32
                GoVers &= 63-16
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_UP,):
                GoVers &= 63-1
            elif event.key in (pygame.K_s, pygame.K_DOWN,):
                GoVers &= 63-2
            elif event.key in (pygame.K_a, pygame.K_LEFT,):
                GoVers &= 63-4
            elif event.key in (pygame.K_d, pygame.K_RIGHT,):
                GoVers &= 63-8
            elif event.key in (pygame.K_q,): #a
                GoVers &= 63-16
            elif event.key in (pygame.K_e,):
                GoVers &= 63-32
            print(str(event.key) + " ==> " + str(GoVers))
    if GoVers & 1:
        # rect.move_ip(0, -Deplacement)
        robotMir.control(0, -stepMir)
    if GoVers & 2:
        # rect.move_ip(0, Deplacement)
        robotMir.control(0, stepMir)
    if GoVers & 4:
        # rect.move_ip(-Deplacement, 0)
        robotMir.control(-stepMir, 0)
    if GoVers & 8:
        # rect.move_ip(Deplacement, 0)
        robotMir.control(stepMir, 0)
    if GoVers & 16:
        # rect.move_ip(Deplacement, 0)
        robotMir.control(0, 0, stepMir * 5)
    if GoVers & 32:
        # rect.move_ip(Deplacement, 0)
        robotMir.control(0, 0, -stepMir * 5)
    
    screen.blit(background, [0, 0])
    # screen.fill(BLACK)
    # screen.blit(image, rect)
    robotMir.update()
    robot_list.draw(screen)
    pygame.display.flip()
    # pygame.display.update(rect.inflate(Deplacement*3,Deplacement*3))  # Or pygame.display.flip()
