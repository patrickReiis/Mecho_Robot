import pygame, sys
from pygame.locals import *

flags = pygame.SCALED|pygame.RESIZABLE
DISPLAYSURF = pygame.display.set_mode((1280,720),flags)

FPS = 60
FPSCLOCK = pygame.time.Clock()

BGCOLOR = (143,219,242)

def terminate():
    pygame.quit()
    sys.exit()

def checkQuit():
    for event in pygame.event.get(QUIT):
        terminate()

    for event in pygame.event.get(KEYDOWN):
        if event.key == K_ESCAPE:
            terminate()
        if event.mod == KMOD_LCTRL and event.key == K_w:
            terminate()
        pygame.event.post(event) # put the other KEYDOWN events back to the list

def renderMap(textFile):
    """
    This function reads a text file, gets it's data
    and create a list with. This list is a list of numbers.
    e.g: [[0,0,1],[1,0,1]] 
    Each number other than 0 will represent a tile on the game.
    """

    mapNum = []
    with open('maps/'+textFile) as text:
        data = text.read()
        data = data.split('\n')

        for row in data:
            _ = []
            if row:
                for x in row:
                    _.append(int(x))
                mapNum.append(_)

        return mapNum

def renderAndDrawRect(mapNum,camera):
    """
    This function gets every item in the 2D mapNum list and 
    draws them with the specified images and also creates a list of rects and
    returns it.
    """
    rects = []

    for row in range(len(mapNum)):
        for column in range(len(mapNum[row])):
            if mapNum[row][column] == 1:
                DISPLAYSURF.blit(groundImg,(column*48-camera[0],row*48-camera[1]))
            if mapNum[row][column] != 0:
                rects.append(Rect(column*48,row*48,48,48))

    return rects

def main():
    global groundImg,soilImg,soilSkullImg

    playerImg = pygame.transform.scale(pygame.image.load('images/robot.png').convert(),(20,40))
    playerImg.set_colorkey((0,0,85)) # Any pixel that matches this RGB color will be transparent on the image

    gunImg = pygame.transform.scale(pygame.image.load('images/gun.png').convert(),(48,48))
    gunImg.set_colorkey((255,255,255))

    groundImg = pygame.transform.scale(pygame.image.load('images/ground.png').convert(),(48,48))
    groundImg.set_colorkey((255,255,255))

    soilImg = pygame.transform.scale(pygame.image.load('images/soil.png').convert(),(48,48))
    soilSkullImg = pygame.transform.scale(pygame.image.load('images/soilSkull.png').convert(),(48,48))

    gameMap = renderMap('map.txt') 

    camera = [0,0]

    while True:
        checkQuit()
        DISPLAYSURF.fill((BGCOLOR))
        
        tiles = renderAndDrawRect(gameMap,camera)

        FPSCLOCK.tick(FPS)
        pygame.display.update()

if __name__ == main():
    main()
        

