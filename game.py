import pygame, sys, math
from pygame.locals import *

pygame.init()
flags = pygame.SCALED|pygame.RESIZABLE
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT),flags)

FPS = 60
FPSCLOCK = pygame.time.Clock()

BGCOLOR = (143,219,242) 

PLAYERSPEED = 5
GRAVITY_FORCE = 0.5
MAX_NUM_JUMPS = 2
JUMP_HEIGHT = 10
GAP_BLIT = 5 # When blitting something from the map.txt, subtract the Y position by GAP_BLIT

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
                    rowList.append(x)
                mapNum.append(rowList)

        return mapNum

def renderAndDrawRect(mapNum,camera):
    """
    This function gets every item in the 2D mapNum list and 
    draws them with the specified images and also creates a list of rects and
    returns it.
    """
    rects = []
    diagonalRects = []

    for row in range(len(mapNum)):
        for column in range(len(mapNum[row])):
            if mapNum[row][column] == '1':
                DISPLAYSURF.blit(groundImg,(column*48-camera[0],row*48-camera[1]-GAP_BLIT))
            if mapNum[row][column] == '2':
                DISPLAYSURF.blit(soilImg,(column*48-camera[0],row*48-camera[1]-GAP_BLIT))
            if mapNum[row][column] == '3':
                DISPLAYSURF.blit(soilSkullImg,(column*48-camera[0],row*48-camera[1]-GAP_BLIT))
            if mapNum[row][column] == '4':
                DISPLAYSURF.blit(cloudImg1,(column*100-camera[0]*0.25,row*100-camera[1]*0.25))
            if mapNum[row][column] != '0' and mapNum[row][column] != '4' and mapNum[row][column] != 'd' and mapNum[row][column] != 'D':
                rects.append(Rect(column*48,row*48,48,48))

            # diagonal rects
            if mapNum[row][column] == 'd':
                diagonalRects.append({'rightUp':Rect(column*48,row*48,48,48)})
                DISPLAYSURF.blit(ramp_d,(column*48-camera[0],row*48-camera[1]-GAP_BLIT))
            if mapNum[row][column] == 'D':
                DISPLAYSURF.blit(ramp_D,(column*48-camera[0],row*48-camera[1]-GAP_BLIT))
                diagonalRects.append({'leftUp':Rect(column*48,row*48,48,48)})
            if mapNum[row][column] == 'c':
                DISPLAYSURF.blit(corner_c,(column*48-camera[0],row*48-camera[1]-GAP_BLIT))
            if mapNum[row][column] == 'C':
                DISPLAYSURF.blit(corner_C,(column*48-camera[0],row*48-camera[1]-GAP_BLIT))

    return rects,diagonalRects

def get_collisions(player,tiles):
    """
    Returns all the tiles the have collided with the player
    """
    collisions = []

    for tile in tiles:
        if tile.colliderect(player):
            collisions.append(tile)
    return collisions

def move(player,tiles,movement,ramps=False):
    """
    1- Update player's position
    2- Check for collisions
    3- Update player's position so It doesn't cross the tiles it has collided with
    All of those steps are made separately for each axis
    """
    collisionsTypes = {'ground':False,'top':False} # Store in dictionary because if I need more types I can easily add them

    player.x += movement[0]
    collisions = get_collisions(player,tiles)  # only getting collisions for X
    for rect in collisions:
        if movement[0] > 0:
            player.right = rect.left
        if movement[0] < 0:
            player.left = rect.right

    player.y += movement[1]
    collisions = get_collisions(player, tiles)  # only getting collisions for Y
    for rect in collisions:
        if movement[1] > 0:
            player.bottom = rect.top
            collisionsTypes['ground'] = True
        if movement[1] < 0:
            player.top = rect.bottom
            collisionsTypes['top'] = True
    
    if ramps:
        for ramp in ramps:
            if 'rightUp' in ramp:
                if ramp['rightUp'].colliderect(player):
                    gap = player.right - ramp['rightUp'].x
                    target_y = ramp['rightUp'].bottom - gap

                    if player.bottom >= target_y:
                        player.bottom = target_y  
                        collisionsTypes['ground'] = True
            elif 'leftUp' in ramp:
                if ramp['leftUp'].colliderect(player):
                    gap = ramp['leftUp'].right - player.x
                    target_y = ramp['leftUp'].bottom - gap

                    if player.bottom >= target_y:
                        player.bottom = target_y
                        collisionsTypes['ground'] = True

    return player, collisionsTypes

def shootLogic(player,mouseCoord, camera):
    """
    Each shoot must pass through the mouse position
    This funcion guarentess mathematically that 
    the shoots will follow a consistent straight path relative to the player center and mouse position
    """
    mousex,mousey = mouseCoord
    mousex = mousex+camera[0]
    mousey = mousey+camera[1]
    
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

def shootData(shootValues,tiles, camera):
    """
    This function updates the shootValues list and also removes the items
    if they leave the screen
    """
    rects, diagonals = tiles
    
    for i in range(len(shootValues)):
        shootValues[i][0] += shootValues[i][4][0]*3
        shootValues[i][1] += shootValues[i][4][1]*3
        shootValues[i][2] += shootValues[i][4][0]*4
        shootValues[i][3] += shootValues[i][4][1]*4
    for shoot in shootValues[:]:
        if shoot[4][0]-camera[0] == 0 and shoot[4][1]-camera[1] == 0:
            shootValues.remove(shoot)

        for tile in rects:
            if tile.collidepoint(shoot[2]-camera[0],shoot[3]-camera[1]):
                shootValues.remove(shoot)
        
        # Instead of using complex math to create a check system for the ramps, I simply draw the bullet behind the ramp
        # and waits for the bullet collide with a normal rect that is not a ramp
        # However if for some reason I need to create that system, here's the basis for it:

        if 0 > 1: # Just so python doesn't need to iterate over the ramps
            for ramp in diagonals:
                if 'rightUp' in ramp:
                    if ramp['rightUp'].collidepoint(shoot[2],shoot[3]):
                        pass

                elif 'leftUp' in ramp:
                    if ramp['leftUp'].collidepoint(shoot[2],shoot[3]):
                        pass

def drawShoot(shootValues, camera):
     for line in shootValues:
        pygame.draw.line(DISPLAYSURF,(255,126,0),(line[0]-camera[0],line[1]-camera[1]),(line[2]-camera[0],line[3]-camera[1]),width=5)
        pygame.draw.line(DISPLAYSURF,(255,255,255),(line[0]-camera[0],line[1]-camera[1]),(line[2]-camera[0],line[3]-camera[1]),width=2)


def gunRotate(gunImg,player,mouse_pos):
    """
    This function rotates the gun
    so the front sight is aligned with the mouse cursor
    Return the gun surface and it's location with a rect data type
    """
    if mouse_pos[0] == -1 or mouse_pos[1] == -1:
        gun = gunImg.get_rect()
        gun.center = player.center

        return gunImg,gun

    if mouse_pos:

        flipGun = False

        co1 = mouse_pos[0] - player.centerx  
        ca1 = mouse_pos[1] - player.centery
        
        co = player.centerx - mouse_pos[0]
        ca = player.centery - mouse_pos[1]

        if (co < 0 and ca < 0) or (co < 0 and ca > 0):
            co = player.centerx - mouse_pos[0]
            ca = player.centery - mouse_pos[1]
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
            gunRotating = pygame.transform.rotate(gunRotated,degrees).convert()
        else:
            gunRotating = pygame.transform.rotate(gunImg,degrees).convert()
        
        gun = gunRotating.get_rect()
        gun.center = player.center
        
        return gunRotating,gun

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

def drawExplosion(location,number,camera):
    name = 'images/explosion'  + str(number) + '.png'
    
    explosionImg = pygame.transform.scale(pygame.image.load(name).convert(),(20,10))
    explosionImg.set_colorkey((255,255,255))

    DISPLAYSURF.blit(explosionImg,(location.x-camera[0],location.y-camera[1]))

def introMenu():
    menuIntro = pygame.transform.scale(pygame.image.load('images/menu intro.png'),(WINDOWWIDTH,WINDOWHEIGHT))
    fontColor = (248,224,117)
    
    mouseCoord = None # If the game starts and the mouse is not on the screen it's position will be set to None
    while True:
        checkQuit()
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                mouseCoord = event.pos

        DISPLAYSURF.blit(menuIntro,(0,0))

        bigRect = Rect(180,270,420,270)
        smallRect = Rect(190,280,400,250)
        bigRect.centery = WINDOWHEIGHT/2
        smallRect.centery = WINDOWHEIGHT/2

        pygame.draw.rect(DISPLAYSURF,(255,255,255),bigRect,border_radius=5)
        pygame.draw.rect(DISPLAYSURF,(34,48,68),smallRect,border_radius=5)
        
        playSurf = pygame.font.SysFont('chilanka',70).render('PLAY',False,fontColor)
        playRect = playSurf.get_rect()
        playRect.center = smallRect.center

        if mouseCoord != None and smallRect.collidepoint(mouseCoord):
            pygame.draw.rect(DISPLAYSURF,(164,59,57),smallRect,border_radius=5)
            if pygame.mouse.get_pressed()[0]:
                return

        messageSurf = pygame.font.SysFont('ubuntumono',22).render('by: @patrickReiis',False,fontColor)

        DISPLAYSURF.blit(messageSurf,(40,680))
        DISPLAYSURF.blit(playSurf,playRect)

        pygame.display.update()

def get_camera(tiles,diagonals,camera):
    squares = []
    ramps = []

    for tile in tiles:
        squares.append(Rect(tile.x-camera[0],tile.y-camera[1] -GAP_BLIT,tile.width,tile.height))

    for ramp in diagonals:
        if 'rightUp' in ramp:
            ramps.append({'rightUp':Rect(ramp['rightUp'].x-camera[0],ramp['rightUp'].y-camera[1]-GAP_BLIT,ramp['rightUp'].width,ramp['rightUp'].height)})
        elif 'leftUp' in ramp:
            ramps.append({'leftUp':Rect(ramp['leftUp'].x-camera[0],ramp['leftUp'].y-camera[1]-GAP_BLIT,ramp['leftUp'].width,ramp['leftUp'].height)})

    return squares,ramps

def main():
    global groundImg,soilImg,soilSkullImg,cloudImg1,ramp_D,ramp_d,corner_C,corner_c

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
    
    ramp_D = pygame.transform.scale(pygame.image.load('images/ramp.png').convert(),(48,48))
    ramp_D.set_colorkey((255,255,255))

    ramp_d = pygame.transform.flip(ramp_D,True,False)
    
    corner_C = pygame.transform.scale(pygame.image.load('images/corner.png').convert(),(48,48)) 

    corner_c = pygame.transform.flip(corner_C,True,False)

    cloudImg1 = pygame.transform.scale(pygame.image.load('images/cloud1.png').convert(),(100,100))
    cloudImg1.set_colorkey((143,219,242))

    gameMap = renderMap('map.txt') 

    currentMousePos = -1,-1
    true_camera = [0,0] 
    shootValues = [] 
    right = False # player direction
    left = False # player direction
    gravity = 0
    animationCounter = 0
    animationValues = [5,10,15,20,25,30,35,40] # When the animationCounter is equal to any of these items, change player animation.
    num_jumps = 0 
    jumpStop = 30
    jumpCounter = [] # This list will append the player location and also a 'counter' value

    introMenu()

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
                        jumpCounter.append([0,player.copy()])
                        num_jumps += 1
                        gravity = -JUMP_HEIGHT

            if event.type == KEYUP:
                if event.key == K_a:
                    left = False
                if event.key == K_d:
                    right = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: # 1 means the left button on the mouse
                    shootValues.append(shootLogic(player,event.pos, camera))
            if event.type == MOUSEMOTION:
                currentMousePos = event.pos
        
        movement = [0,0] # This variable will be used to update the player position, the first value is for the X axis and the second for the Y axis
        true_camera[0] += (player.x - true_camera[0] - WINDOWWIDTH/2)/20
        true_camera[1] += (player.y - true_camera[1] - WINDOWHEIGHT/2)/20
        camera = true_camera.copy()
        camera[0] = int(camera[0])
        camera[1] = int(camera[1])
        
        player_camera = player.copy() # Player camera is used as 
        player_camera.x -= camera[0] #  argument in shootLogic function
        player_camera.y -= camera[1] 
        if not right and not left:
            if currentMousePos and currentMousePos[0] < player_camera.x:
                playerImg = pygame.transform.flip(origPlayerImg,True,False)
            else:
                playerImg = origPlayerImg 

        if right:
            animationCounter += 1
            animationCounter,playerAnimation = checkAnimation(animationCounter,animationValues,'walking/walking',player_camera,currentMousePos)
            if playerAnimation != None:
                playerImg = playerAnimation
            movement[0] += PLAYERSPEED

        if left:
            animationCounter += 1
            animationCounter,playerAnimation = checkAnimation(animationCounter,animationValues,'walking/walking',player_camera,currentMousePos)
            if playerAnimation != None:
                playerImg = playerAnimation
            movement[0] -= PLAYERSPEED
        
        drawShoot(shootValues, camera)

        tiles,rampTiles = renderAndDrawRect(gameMap,camera)
        tilesWithCamera,rampsWithCamera = get_camera(tiles,rampTiles,camera)

        shootData(shootValues,(tilesWithCamera,rampsWithCamera), camera)

        movement[1] += gravity
        player, collisionsTypes = move(player,tiles,movement,rampTiles)
        
        if collisionsTypes['ground']:
            gravity = 0
            num_jumps = 0
        else:
            gravity += GRAVITY_FORCE

        if collisionsTypes['top']:
            gravity = 0
        if gravity > 10:
            gravity = 10
        
        for i in range(len(jumpCounter)):
            jumpCounter[i][0] += 1
            if jumpCounter[i][0] <= jumpStop/3*1: 
                drawExplosion(jumpCounter[i][1],1,camera)

            elif jumpCounter[i][0] <= jumpStop/3*2: 
                drawExplosion(jumpCounter[i][1],2,camera)

            elif jumpCounter[i][0] <= jumpStop/3*3: 
                drawExplosion(jumpCounter[i][1],3,camera)

        for jumpData in jumpCounter[:]:
            if jumpData[0] > jumpStop:
                jumpCounter.remove(jumpData)

        DISPLAYSURF.blit(playerImg,(player.x-camera[0],player.y-camera[1]))
        
        gun_with_rotation, gun = gunRotate(gunImg,player,(currentMousePos[0]+camera[0],currentMousePos[1]+camera[1]))
        DISPLAYSURF.blit(gun_with_rotation,(gun.x-camera[0],gun.y-camera[1]))

        FPSCLOCK.tick(FPS)
        pygame.display.update()

if __name__ == main():
    main()
        

