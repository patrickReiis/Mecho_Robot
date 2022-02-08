import pygame, sys
from pygame.locals import *


DISPLAYSURF = pygame.display.set_mode((1024,760))

def exit():
    pygame.quit()
    sys.exit()

def checkQuit():
    for event in pygame.event.get(QUIT):
        exit()

    for event in pygame.event.get(KEYDOWN):
        if event.key == K_ESCAPE:
            exit()
        if event.mod == KMOD_LCTRL and event.key == K_w:
            exit()
        pygame.event.post(event) # put the other KEYDOWN events back to the list

def main():
    while True:
        checkQuit()

if __name__ == main():
    main()
        

