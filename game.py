import pygame, sys
from pygame.locals import *


DISPLAYSURF = pygame.display.set_mode((700,600))

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

