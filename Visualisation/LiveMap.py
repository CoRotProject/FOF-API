# coding: utf8
# Copyright 2020 Fabrice DUVAL
# Biblio
# https://docs.python-eve.org/en/stable/features.html
# https://docs.python-eve.org/en/stable/tutorials/custom_idfields.html
# https://www.youtube.com/watch?v=lc8NNJgeVjI
# https://www.youtube.com/watch?v=vIwpvkkvos0
# https://www.pygame.org/docs/ref/sprite.html
# https://opensource.com/article/17/12/game-python-moving-player

# version 3 ==> on passe avec une version d'image modificable Connecté sur la BDD

import base64
# import math
import io
import pygame
import pygame.freetype
from PIL import Image, ImageDraw
# import tkinter.messagebox
import sys
# sys.path.append("..\\Commandes")
# from commandeAPI import getvalues, findINfactory, findfactory
import Commandes.commandeAPI as commandeAPI
#test des fonctions annexe de commandeAPI
if not commandeAPI.check_ping("127.0.0.1"):
    exit()

try:
    print("API in remote mode: ",sys.argv[1])
    commandeAPI.seturl(sys.argv[1])
except IndexError:
    print("API in local 127.0.0.1")

try:
    factoryname = sys.argv[2]
except IndexError:
    factoryname = "Factory LINEACT Real"
print("Factory Name = ",factoryname)

# Liaison labo BDD
modeenligne = True
try:
    factoryid = commandeAPI.findfactory(name=factoryname)[0]
except TimeoutError:
    modeenligne = False
    print("Pas de connexion au serveur " + commandeAPI.urlTemplate)
except IndexError:
    modeenligne = False
    print("Pas de base de données correcte")

# if not tkinter.messagebox.askokcancel(title="Validation IP serveur", message="Connexion au serveur " + commandeAPI.urlTemplate + "\nFactory = "+factoryname):
#     quit(-1)



pygame.font.init()
successes, failures = pygame.init()
print("{0} successes and {1} failures".format(successes, failures))

myfont = pygame.font.SysFont(None, 18)

def updaterobotpos(factoryid, listerobot):
    notmoved = True
    for robot in listerobot:
        info = commandeAPI.getvalues(factoryid, "robot", robot[0])["transform2D"]
        if info["x"] != robot[1].xcm != robot[1].xcm or info["y"] != robot[1].ycm or info["theta"] % 360 != robot[1].angle % 360:
            notmoved = False
            robot[1].movetocm(info["x"], info["y"], info["theta"])
    return notmoved

class Laboratoire():
    """Définition du laboratoire"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, nom, fichier, resolutionorigine, offset):
        """"
        nom = nom de la carte
        fichier = fichier png du plan
        resolutionorigine = résolution en pixel par mètre
        offset = décalage en mètre du point en bas à gauche (par defaut ce point vaut (0,0) )
        """
        self.origine = pygame.image.load(fichier)
        self.rectaille = self.origine.get_rect()
        self.imageresolution = resolutionorigine / 1000
        self.offset = offset
        self.nom = nom
        self.affichage = None

        # Attention ! Convention "naturelle" dans les versions "m" y vers le haut !!! et (0,0) en bas à gauche
        # top et bottom sont donc inversés
        sizem = (1000 * self.rectaille.w / resolutionorigine, 1000 * self.rectaille.h / resolutionorigine, ) # taille en mm pour rester sur des entiers
        self.rectaff_m_orig = pygame.Rect((offset[0] * 1000, offset[1] * 1000), sizem)
        # on affiche tout par défaut
        self.rectaff_m = self.rectaff_m_orig

        #on initialise taille affichage (size) = taille image
        self.size = [self.rectaille.w, self.rectaille.h, ]
        #ajout des pièces immobile dans la factory
        self.changesize(self.size)

    def changesize(self, sizeaff, positionimage=None):
        if not positionimage:
            positionimage = self.rectaff_m
        newh = min(positionimage.w / sizeaff[0] * sizeaff[1], self.rectaff_m_orig.h) # l'affichage est prioritaire
        neww = min(positionimage.w, self.rectaff_m_orig.h * sizeaff[0] / sizeaff[1])
        positionimage.inflate_ip(neww - positionimage.w, newh - positionimage.h, )
        new_rectaff = positionimage.clamp(self.rectaff_m_orig)

        image = self.origine.subsurface(self.rectmm2pix(new_rectaff, origine=True))
        self.affichage = pygame.transform.scale(image, sizeaff)
        self.size = sizeaff
        self.rectaff_m = new_rectaff

    def pospix2mm(self, point):
        return point[0]/self.size[0] * self.rectaff_m.w + self.rectaff_m.left, - point[1]/self.size[1] * self.rectaff_m.h + self.rectaff_m.bottom,

    def zoom(self, ratio, positionclic=None):
        if positionclic is None:
            positionclic = self.rectaff_m.center
        positionmm = self.pospix2mm(positionclic)
        new_rectaff = self.rectaff_m.copy()
        ratio2 = max(min(ratio, self.rectaff_m_orig.w/self.rectaff_m.w, self.rectaff_m_orig.h/self.rectaff_m.h, ), 1000/self.rectaff_m.w, 1000/self.rectaff_m.h,)
        new_rectaff.w *= ratio2
        new_rectaff.h *= ratio2
        new_rectaff.center = positionmm
        new_rectaff.clamp_ip(self.rectaff_m_orig)
        image = self.origine.subsurface(self.rectmm2pix(new_rectaff, origine=True))
        self.affichage = pygame.transform.scale(image, self.size)
        self.rectaff_m = new_rectaff

    def rectmm2pix(self, rect, origine=False):
        if origine: # par rapport à l'image d'origine
            tailleratiox, tailleratioy = self.imageresolution, self.imageresolution
        else:
            tailleratiox, tailleratioy = self.getaspectratio()
        newleft = (rect.left - self.rectaff_m_orig.left) * tailleratiox
        newtop = (self.rectaff_m_orig.bottom - rect.bottom) * tailleratioy
        newwidth = rect.w * tailleratiox
        newheight = rect.h * tailleratiox
        return pygame.Rect((newleft, newtop, newwidth, newheight, ))

    def getaspectratio(self):
        return (self.size[0] / self.rectaff_m.w, self.size[1] / self.rectaff_m.h)

    def getposinpixel(self, xmm, ymm):
        ratiox, ratioy = self.getaspectratio()
        posx = int((xmm - self.rectaff_m.left) * ratiox)
        posy = int(- (ymm - self.rectaff_m.bottom) * ratioy)
        return (posx, posy,)

class RobotClass(pygame.sprite.Sprite):
    """"Définition de l'affichage des robots"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, name, fichier, shortname, labo): # Laboratoire renvoi vers le labo# resolution en pixel par mètre # offset en mètre
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.factoryid = None
        self.robotId = None
        self.textsurface = myfont.render(shortname, True, (255, 0, 0))
        self.angle = 0  # angle
        self.labo = labo
        self.offset = labo.offset
        self.moveangle = 0
        self.angle = 0
        self.movetox = 0
        self.posx = 0
        self.movetoy = 0
        self.posy = 0
        self.rect = pygame.Rect(0, 0, 0, 0)
        # self.transform_mtopixelcoef = [self.resolution[0], -self.offset[0]*self.resolution[0], -self.resolution[1],
        # -self.offset[1]*self.resolution[1], ] # [a, b, c, d] ==> Xpixel = ax + b en Ypixel = cy + d
        # self.frame = 0 # count frames
        self.imageBase = pygame.image.load(fichier) # resolution imposée ! = 1pt/cm ==> 100pt/m
        self.rectimageBase = self.imageBase.get_rect()

        self.rectmm = self.rectimageBase.copy()
        self.rectmm.w *= 10 #==> transformation en mm
        self.rectmm.h *= 10 #==> transformation en mm
        self.imagezoomee = self.resizeme()
        self.image = self.imagezoomee

        self.textrect = self.textsurface.get_rect()

    def resizeme(self):
        # newtaillew = int(self.labo.getaspectratio()[0] * self.rectmm.w)
        # newtailleh = int(self.labo.getaspectratio()[1] * self.rectmm.h)
        # newimage = pygame.transform.scale(self.imageBase, (newtaillew, newtailleh, ))
        newimage = pygame.transform.rotozoom(self.imageBase, 0, self.labo.getaspectratio()[0]*self.rectmm.w/self.rectimageBase.w)
        self.rect.size = newimage.get_rect().size
        return newimage

    def movetomm(self, posx, posy, theta=0):
        '''
        control robot movement move in mm
        '''
        self.movetox, self.movetoy = posx, posy
        self.moveangle = theta

    def fget_pospix(self):
        return self.labo.getposinpixel(self.posx, self.posy, )

    def fget_xpix(self):
        return self.fget_pospix()[0]

    def fget_ypix(self):
        return self.fget_pospix()[1]

    xpix = property(fget=fget_xpix, doc="position x en pixel")
    ypix = property(fget=fget_ypix, doc="position y en pixel")

    def updateposedatabase(self):
        infos = commandeAPI.getvalues(self.factoryid, "robot", self.robotId)
        self.movetomm(infos["transform2D"]["x"]*1000, infos["transform2D"]["y"]*1000, infos["transform2D"]["theta"])
        retour = infos["name"] + " : " + infos["status"]
        if infos["status"] == "busy":
            operationrunning = commandeAPI.findINfactory(factoryid,"operation", status="doing", resourceInfo=self.robotId)
            if operationrunning:
                operation = commandeAPI.getvalues(self.factoryid, "operation", operationrunning[0])
                if "name" in operation:
                    retour += ' - ' + operation["name"]
                else:
                    retour += ' - ' + operationrunning[0]
            else:
                retour += ' - other'
        return retour

    def update(self, Forced=False):
        '''
        Update sprite position
        '''
        moved = False
        if Forced:
            self.imagezoomee = self.resizeme()
        if abs((self.moveangle - self.angle) % 360) > 0.1 or Forced:
            print("{} {}° ==> {}°".format(self.name, self.angle, self.moveangle, ))
            self.angle = self.moveangle % 360 # angle entre 0 et 359
            newimage = pygame.transform.rotate(self.imagezoomee, self.angle)
            taille = newimage.get_rect()
            # taille.inflate_ip(taille.w - self.rect.w, taille.h - self.rect.h)
            taille.inflate_ip(self.rect.w - taille.w, self.rect.h - taille.h)
            self.image = newimage.subsurface(taille)
            self.textrect.center = self.image.get_rect().center
            self.image.blit(self.textsurface, self.textrect)
            moved = True

        togoxpix, togoypix = self.labo.getposinpixel(self.movetox, self.movetoy)
        togoxpix = min(max(togoxpix, 0), labo.size[0])
        togoypix = min(max(togoypix, 0), labo.size[1])
        if self.rect.centerx != togoxpix or self.rect.centery != togoypix or Forced:
            print("{} ({},{}) ==> ({},{}) ({},{})m".format(self.name, self.rect.x, self.rect.y, togoxpix, togoypix, self.movetox/1000, self.movetoy/1000, ))
            self.rect.center = (togoxpix, togoypix)
            # if self.rect.x < 0:
            #     self.rect.x = 0
            # if self.rect.right > labo.size[0]:
            #     self.rect.x = labo.size[0] - self.rect.w
            # if self.rect.y < 0:
            #     self.rect.y = 0
            # if self.rect.bottom > labo.size[1]:
            #     self.rect.y = labo.size[1] - self.rect.h
            moved = True
        return moved

### Partie paramètre à récupérer de la BDD

# background = pygame.image.load("Madrillet 500x325.png") # correspond à 1pt/5cm ==> 25mx16m25 # pour la version <=2
# background = pygame.image.load("Madrillet.png") # plan complet 1pt/5cm

def addstock(factoryid, image, offsetfact, infostock):
    # offsetfact dx, dy, dtheta, size per pixel in m
    positionstock = commandeAPI.findrealposition(factoryid, infostock)
    imgstock = Image.open("mir100-pixilart emplacement.png").rotate(positionstock["theta"]) # 0.01 m /pixel center point is the reference point
    ratio = offsetfact[3]/0.01
    positioncentre = (positionstock["x"] - offsetfact[0]) / offsetfact[3], (positionstock["y"] - offsetfact[1]) / offsetfact[3]
    imgstock = imgstock.resize((int(imgstock.size[0] // ratio), int(imgstock.size[1] // ratio)), Image.ANTIALIAS)
    Xmin, Ymin = int(positioncentre[0] - imgstock.size[0]//2), int(image.size[1] - positioncentre[1] - imgstock.size[1]//2)
    image.paste(imgstock, (Xmin, Ymin, Xmin + imgstock.size[0], Ymin + imgstock.size[1]), imgstock)
    return image

def addmachine(image, offsetfact, infomachine):
    positionmachine = commandeAPI.findrealposition(factoryid, infomachine)
    tailleMx, tailleMy = int(infomachine["volume"]["dx"] / offsetfact[3]), int(infomachine["volume"]["dy"] / offsetfact[3])
    taille = int((tailleMx**2 + tailleMy**2) ** 0.5 + 4)
    machine = Image.new("RGBA", (taille, taille), (255, 255, 255, 0))
    draw = ImageDraw.Draw(machine)
    draw.rectangle((((taille-tailleMx)//2, (taille-tailleMy)//2), ((taille+tailleMx)//2, (taille+tailleMy)//2)),fill="black")
    machine = machine.rotate(positionmachine["theta"])
    positioncentre = (positionmachine["x"] - offsetfact[0]) / offsetfact[3], (positionmachine["y"] - offsetfact[1]) / offsetfact[3]
    Xmin, Ymin = int(positioncentre[0] - machine.size[0]//2), int(image.size[1] - positioncentre[1] - machine.size[1]//2)
    image.paste(machine, (Xmin, Ymin, Xmin + machine.size[0], Ymin + machine.size[1]), machine)
    return image


# Init Labo ==> a faire depuis la bdd
if modeenligne:
    factorydata = commandeAPI.getfactory(factoryid)
    if "plan" in factorydata.keys():
        deltax = factorydata["plan"]["offset"]["x"]
        deltay = factorydata["plan"]["offset"]["y"]
        offset = (deltax, deltay, 0.0)
        offset_scaled = offset + (factorydata["plan"]["scale"],)
        # ajout des éléments fixes Stocks
        imageFactoryPNG = base64.b64decode(factorydata["plan"]["picture"])
        image = Image.open(io.BytesIO(imageFactoryPNG))

        stockbase = commandeAPI.findINfactory(factoryid, "stock", link=None)
        for stock in stockbase:
            infos = commandeAPI.getvalues(factoryid, "stock", stock)
            image = addstock(factoryid, image, offset_scaled, infos)

        # ajout des éléments fixes Machine
        machines = commandeAPI.findINfactory(factoryid, "machine",)
        for machine in machines:
            infos = commandeAPI.getvalues(factoryid, "machine", machine)
            image = addmachine(image, offset_scaled, infos)
            for stock in commandeAPI.findINfactory(factoryid, "stock", link=machine):
                infos = commandeAPI.getvalues(factoryid, "stock", stock)
                image = addstock(factoryid, image, offset_scaled, infos)

        image.save("carte.png", "PNG")
        # with open("carte.png", "wb") as file:
        #     file.write(imageFactory)
        labo = Laboratoire("Laboratoire", "carte.png", 1/factorydata["plan"]["scale"], offset)
    else:
        print("Factory incompatible dans la database (pas de carte)")

else:
    deltax = -20.5
    deltay = -34.2
    offset = (deltax, deltay, 0.0)
    labo = Laboratoire("Madrillet", "Madrillet.png", 20.0, offset)

#Init ecran
window_width = 1000
window_height = 600
size = (window_width, window_height)
screen = pygame.display.set_mode(size, pygame.RESIZABLE) # ==> 1pt/xxcm ==>pour 1000pts pour REALW mètre
backdropbox = screen.get_rect()
pygame.display.set_caption("Map Madrillet Atelier Flexible")
clock = pygame.time.Clock()
FPS = 5  # Frames per second.
couleur = {"BLACK" : (0, 0, 0), "WHITE" : (255, 255, 255), "RED" : (255, 0, 0), "GREEN" : (0, 255, 0), "BLUE" : (0, 0, 255)}

# Init robot
robot_list = pygame.sprite.Group()
tableaurobot = []
if modeenligne:
    robots = commandeAPI.findINfactory(factoryid, "resource", robotType="mir100")
    for robot in robots:
        infos = commandeAPI.getvalues(factoryid, "robot", robot)
        encours = RobotClass("Robot " + infos["name"], 'mir100-pixilart.png', infos["name"][infos["name"].rfind('_')+1:], labo)
        robot_list.add(encours)
        encours.factoryid = factoryid
        encours.robotId = robot
        tableaurobot.append(encours)
        encours.movetomm(infos["transform2D"]["x"]*1000, infos["transform2D"]["y"]*1000, infos["transform2D"]["theta"])
else:
    robotMir1 = RobotClass("Robot Mir100_ARM", 'mir100-pixilart.png', "Arm", labo)
    robot_list.add(robotMir1)
    tableaurobot.append(robotMir1)
    robotMir1.movetomm(0, 0)

    robotMir2 = RobotClass("Robot Mir100_CAPITAINE", 'mir100-pixilart.png', "Hook", labo)
    robot_list.add(robotMir2)
    tableaurobot.append(robotMir2)
    robotMir2.movetomm(8000, 8000)


# Initi liaison base/robot

small_font = pygame.freetype.SysFont(pygame.font.get_default_font(), 12)
Continuer = True

while Continuer:
    clock.tick(FPS)
    resized = False
    for event in pygame.event.get():
        # print(event)
        # print(event.type)
        if event.type == pygame.QUIT:
            Continuer = False
            break
        if event.type == pygame.VIDEORESIZE:
            labo.changesize(event.dict['size'])
            print("changement de taille")
            screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
            resized = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 5:
                # zoom
                print("zoom out")
                labo.zoom(1.25, event.pos)
                resized = True
            elif event.button == 4:
                # dezoom
                print("zoom in")
                labo.zoom(0.8, event.pos)
                resized = True
# updaterobotpos(factoryid, robots)
    screen.blit(labo.affichage, [0, 0])
    # screen.fill(BLACK)
    # screen.blit(image, rect)
    nb1 = 0
    for nb1, robot in enumerate(tableaurobot):
        if modeenligne:
            retour = robot.updateposedatabase()
            if retour:
                small_font.render_to(screen, (5, 5 + 16 * nb1), retour, (255, 64, 0))
        robot.update(Forced=resized)
    if modeenligne:
        for nb2, machine in enumerate(machines):
            infos = commandeAPI.getvalues(factoryid, "machine", machine)
            small_font.render_to(screen, (5, 21 + 16 * (nb1 + nb2)), infos["name"] + " - " + infos["status"], (255, 64, 0))
    robot_list.draw(screen)
    pygame.display.flip()
    # pygame.display.update(rect.inflate(Deplacement*3,Deplacement*3))  # Or pygame.display.flip()
