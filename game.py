import pygame, sys, math
from pygame.locals import *

flags = pygame.SCALED|pygame.RESIZABLE
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT),flags)

FPS = 60
FPSCLOCK = pygame.time.Clock()

BGCOLOR = (143,219,242)

PLAYERSPEED = 3
GRAVITY_FORCE = 0.2
MAX_NUM_JUMPS = 2
JUMP_HEIGHT = 5

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
            rowList = []
            if row:
                for x in row:
                    rowList.append(int(x))
                mapNum.append(rowList)

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

def get_collisions(player,tiles):
    """
    Returns all the tiles the have collided with the player
    """
    collisions = []

    for tile in tiles:
        if tile.colliderect(player):
            collisions.append(tile)
    return collisions

def move(player,tiles,movement):
    """
    1- Update player's position
    2- Check for collisions
    3- Update player's position so It doesn't cross the tiles it has collided with
    All of those steps are made separately for each axis
    """
    collisionsTypes = {'ground':False} # Store in dictionary because if I need more types I can easily add them

    player.x += movement[0]
    collisions = get_collisions(player,tiles)  # only testing collisions for X
    for rect in collisions:
        if movement[0] > 0:
            player.right = rect.left
        if movement[0] < 0:
            player.left = rect.right

    player.y += movement[1]
    collisions = get_collisions(player, tiles)  # only testing collisions for Y
    for rect in collisions:
        if movement[1] > 0:
            player.bottom = rect.top
            collisionsTypes['ground'] = True
        if movement[1] < 0:
            player.top = rect.bottom

    return player, collisionsTypes

def shootLogic(player,mouseCoord):
    """
    Each shoot must pass through the mouse position
    This funcion guarentess mathematically that 
    the shoots will follow a consistent straight path relative to the player center and mouse position
    """
    mousex,mousey = mouseCoord
    
    startx,starty = player.center # line (bullet) starts at the center of the player
    endx,endy = startx,starty # line (bullet) on first iteration will end at the center of the player

    # These values will update the line (bullet) position
    updatex = (mousex - startx)
    updatey = (mousey - starty)

    # Make sure the values are not too big so all bullets have almost the same speed
    while (updatex > 5 or updatex < -5) or (updatey > 5 or updatey < -5):
        updatex /= 2
        updatey /= 2
        
    return [startx,starty,endx,endy,[updatex,updatey]]

def shootData(shootValues):
    """
    This function updates the shootValues list and also removes the items
    if they leave the screen
    """


    for i in range(len(shootValues)):
        shootValues[i][0] += shootValues[i][4][0]*3
        shootValues[i][1] += shootValues[i][4][1]*3
        shootValues[i][2] += shootValues[i][4][0]*4
        shootValues[i][3] += shootValues[i][4][1]*4
    for shoot in shootValues[:]:
        if shoot[0] > WINDOWWIDTH or shoot[0] < 0 or shoot[1] > WINDOWHEIGHT or shoot[1] < 0:
            shootValues.remove(shoot)
        if shoot[4][0] == 0 and shoot[4][1]:
            shootValues.remove(shoot)

def drawShoot(shootValues):
     for line in shootValues:
        pygame.draw.line(DISPLAYSURF,(255,126,0),(line[0],line[1]),(line[2],line[3]),width=5)
        pygame.draw.line(DISPLAYSURF,(255,255,255),(line[0],line[1]),(line[2],line[3]),width=2)

def drawGun(gunImg,player,mouse_pos):
    """
    This function draws the gun and
    also rotates it so the front sight is aligned with 
    the mouse cursor
    """
    if not mouse_pos:
        gun = gunImg.get_rect()
        gun.center = player.center
        DISPLAYSURF.blit(gunImg,gun)

    if mouse_pos:

        flipGun = False

        co1 = mouse_pos[0] - player.centerx  
        ca1 = mouse_pos[1] - player.centery
        
        co = player.centerx - mouse_pos[0]
        ca = player.centery - mouse_pos[1]

        if (co < 0 and ca < 0) or (co < 0 and ca > 0):
            co = player.centerx - mouse_pos[0]
            ca = player.centery - mouse_pos[1]
            flipGun = False
        else:
            co,ca = co1,ca1
            flipGun = True

        hypotenuse = math.sqrt( ((co**2) + (ca**2)) )
        if hypotenuse != 0:
            degrees = math.degrees(math.asin(ca/hypotenuse))
            a = math.cos(degrees)
            b = math.sin(degrees)
        if flipGun:
            gunRotated = pygame.transform.flip(gunImg,True,False)
            rotating = pygame.transform.rotate(gunRotated,degrees).convert()
        else:
            rotating = pygame.transform.rotate(gunImg,degrees).convert()
        
        gun = rotating.get_rect()
        gun.center = player.center

        DISPLAYSURF.blit(rotating,gun)

def checkAnimation(counter,switchAnimation,name,player,mousepos):
    """
    This functions will iterate over switchAnimation and each time
    the counter is equal to one of the items in the switchAnimation list
    the player image will change.
    This creates an animation effect.
    """

    string = 'images/' + name 

    if counter > switchAnimation[-1:][0]:
        counter = 0 # Reset counter if it's equal to the last item

    playerSurf = None
    for i in range(len(switchAnimation)):
        if counter == switchAnimation[i]:
            message = string + str(i+1) # creates a path string / E.g; walking1,walking2,walking3...
            playerSurf = pygame.transform.scale(pygame.image.load(message+ '.png'),(20,40))
            playerSurf.set_colorkey((0,0,85))
            if mousepos and mousepos[0] < player.x:
                playerSurf = pygame.transform.flip(playerSurf,True,False) # If the mouse cursor is at the right of the player, flip the player horizontally 
                playerSurf.set_colorkey((0,0,85)) # Every pixel with this color will be transparent

    return counter,playerSurf 

def main():
    global groundImg,soilImg,soilSkullImg

    playerImg = pygame.transform.scale(pygame.image.load('images/robot.png').convert(),(20,40))
    playerImg.set_colorkey((0,0,85)) # Any pixel that matches this RGB color will be transparent on the image 
    origPlayerImg = playerImg.copy()
    player = playerImg.get_rect()
    player.x,player.y = 100,100

    gunImg = pygame.transform.scale(pygame.image.load('images/gun.png').convert(),(30,15))
    gunImg.set_colorkey((255,255,255))

    groundImg = pygame.transform.scale(pygame.image.load('images/ground.png').convert(),(48,48))
    groundImg.set_colorkey((255,255,255))

    soilImg = pygame.transform.scale(pygame.image.load('images/soil.png').convert(),(48,48))
    soilSkullImg = pygame.transform.scale(pygame.image.load('images/soilSkull.png').convert(),(48,48))

    gameMap = renderMap('map.txt') 

    currentMousePos = tuple()
    camera = [0,0] 
    shootValues = [] 
    right = False # player direction
    left = False # player direction
    gravity = 0
    animationCounter = 0
    animationValues = [5,10,15,20,25,30,35,40] # When the animationCounter is equal to any of these items, change player animation.
    num_jumps = 0 


    while True:
        checkQuit()
        DISPLAYSURF.fill((BGCOLOR))
        
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_a:
                    left = True
                if event.key == K_d:
                    right = True
                if event.key == K_w:
                    if num_jumps < MAX_NUM_JUMPS:
                        num_jumps += 1
                        gravity = -JUMP_HEIGHT

            if event.type == KEYUP:
                if event.key == K_a:
                    left = False
                if event.key == K_d:
                    right = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: # 1 means the left button on the mouse
                    shootValues.append(shootLogic(player,event.pos))
            if event.type == MOUSEMOTION:
                currentMousePos = event.pos

        movement = [0,0] # This variable will be used to update the player position, the first value is for the X axis and the second for the Y axis
        
        if not right and not left:
            if currentMousePos and currentMousePos[0] < player.x:
                playerImg = pygame.transform.flip(origPlayerImg,True,False)
            else:
                playerImg = origPlayerImg 

        if right:
            animationCounter += 1
            animationCounter,playerAnimation = checkAnimation(animationCounter,animationValues,'walking/walking',player,currentMousePos)
            if playerAnimation != None:
                playerImg = playerAnimation
            movement[0] += PLAYERSPEED

        if left:
            animationCounter += 1
            animationCounter,playerAnimation = checkAnimation(animationCounter,animationValues,'walking/walking',player,currentMousePos)
            if playerAnimation != None:
                playerImg = playerAnimation
            movement[0] -= PLAYERSPEED
        
        shootData(shootValues)
        drawShoot(shootValues)

        tiles = renderAndDrawRect(gameMap,camera)

        movement[1] += gravity
        player, collisionsTypes = move(player,tiles,movement)
        
        if collisionsTypes['ground'] == True:
            gravity = 0
            num_jumps = 0
        else:
            gravity += GRAVITY_FORCE

        if gravity > 10:
            gravity = 10
        
        DISPLAYSURF.blit(playerImg,player)
        drawGun(gunImg,player,currentMousePos)

        FPSCLOCK.tick(FPS)
        pygame.display.update()

if __name__ == main():
    main()
        

