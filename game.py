import pygame, sys
from pygame.locals import *

flags = pygame.SCALED|pygame.RESIZABLE
DISPLAYSURF = pygame.display.set_mode((1280,720),flags)

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

def main():
    while True:
        checkQuit()

        pygame.display.update()

if __name__ == main():
    main()
        

