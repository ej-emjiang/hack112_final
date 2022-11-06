from cmu_112_graphics import *
import math, copy, random
import floorplan as fp
import floorPlanList as fpl
import testmap as tp
import tkinter as tk
import PIL
'''
Changelog (Emily woke up at 7:00 and fucked around):
Pause menu added
Kai now exists (as a bisque circle) and can move
TODO: game balancing once we do start spawning rats
TODO: make game look good
'''
################################################################################
#
# CLASSES
#
################################################################################

class Player:
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.inventory = dict()

    def drawPlayer(self, app, canvas):
        if 0 <= self.row < app.rows and 0 <= self.col < app.cols:
            # TODO: canvas.create_circle. idk how to do this
            x0, y0, x1, y1 = getCellBounds(app, self.row, self.col)
            margin = app.width*0.001
            canvas.create_oval(x0+margin, y0+margin, x1-margin, y1-margin, fill='red')
    
    def movePlayer(self, app, drow, dcol): 
        # TODO: finish this when the map is stored in app
        if not ((self.row + drow < 0) or (self.row + drow >= app.rows) or (self.col + dcol < 0) or (self.col + dcol >= app.cols)):
            self.row += drow
            self.col += dcol

            if not self.legalMove(app):
                self.row -= drow
                self.col -= dcol

    def legalMove(self, app):
        if app.map[self.row][self.col] is False:
            return False
        return True

class Button:
    buttonList = list()
    def __init__(self, cornX, cornY, width, height, label, fill='#dee4ed'):
        self.cornX, self.cornY = cornX, cornY
        self.width, self.height = width, height
        self.fill = fill
        self.label = label
        Button.buttonList.append(self)
        self.isVisible = False

    def __repr__(self):
        return f'{self.label} at ({self.cornX}, {self.cornY})'

    def drawButton(self, app, canvas):
        self.isVisible = True
        fontSize = int(0.1*self.width)
        canvas.create_rectangle(self.cornX, self.cornY, self.cornX + self.width, self.cornY + self.height, 
        fill = self.fill)
        canvas.create_text(self.cornX+self.width/2, self.cornY+self.height/2, font = f'arial {fontSize}', text = self.label)

    @staticmethod
    def getButton(app, event):
        mouseX, mouseY = event.x, event.y
        for button in Button.buttonList:
            if (button.cornX <= mouseX <= button.cornX+button.width and 
                button.cornY <= mouseY <= button.cornY + button.height):
                if button.isVisible:
                    return button
        return None

class Controls:
    def __init__(self):
        self.moveUp = 'w'
        self.moveLeft = 'a'
        self.moveRight = 'd'
        self.moveDown = 's'
        self.back = 'escape'
        self.confirm = ['enter'] # either one of these shall work as confirm


    def createControlButtons(self, app): # for the settings menu
        # sorry. This is awful.
        # Button drawings don't update after editing controls for some reason
        # TODO: GO TO OH AHHHHHHH
        width, height = 150, 30
        cornX, cornY = app.width/2 - 0.5*width, app.height*0.55
        dy = height + app.height*0.02
        app.changeUp = cButton(cornX, cornY, width, height,
                              f'up: {app.controls.moveUp}', app.controls.moveUp)
        app.changeLeft = cButton(cornX, cornY + dy, width, height,
                                f'left: {self.moveLeft}', app.controls.moveLeft)
        app.changeRight = cButton(cornX, cornY + 2*dy, width, height,
                                 f'right: {self.moveRight}', app.controls.moveRight)
        app.changeDown = cButton(cornX, cornY + 3*dy, width, height,
                                f'down: {self.moveDown}', app.controls.moveDown)
        app.changeBack = cButton(cornX, cornY + 4*dy, width, height,
                                f'back: {self.back}', app.controls.back)
        app.changeConfirm = cButton(cornX, cornY + 5*dy, width, height,
                                   f'confirm: {self.confirm[0]}', app.controls.confirm)
        app.controlButtons = [app.changeUp, app.changeLeft, app.changeRight, 
                              app.changeDown, app.changeBack, 
                              app.changeConfirm]

class cButton(Button): # controlButton
    def __init__(self, cornX, cornY, width, height, label, control):
        super().__init__(cornX, cornY, width, height, label, fill='#dee4ed')
        self.control = control


class Rat(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        initLvl = 3
        self.speedLvl = initLvl
        initXDir, initYDir = random.randint(-1, 2), random.randint(-1, 2)
        self.xDir, self.yDir = initXDir, initYDir
        self.illegals = 0

    def isLegalMove(self, app, x, y, i):
        if x >= app.cols or y >= app.rows or x < 0 or y < 0:
            return False
        if app.map[x][y] == False:
            return False
        for j in range(len(app.mischief)):
            if j != i:
                rat = app.mischief[j]
                if rat.x == x and rat.y == y:
                    return False
        if app.kai.row == y and app.kai.col == x:
            return False
        return True

    def moveRat(self, app, i):
        self.x += self.xDir
        self.y += self.yDir
        if not self.isLegalMove(app, self.x, self.y, i):
            self.x -= self.xDir
            self.y -= self.yDir
            self.xDir, self.yDir = random.randint(-1, 2), random.randint(-1, 2)
            self.illegals += 1

# 🐀
def exterminate(app):
    for rat in app.mischief:
        if rat.illegals > 50:
            app.mischief.remove(rat)


def spawnRat(app):
    x = random.randint(0, app.rows-1)
    y = random.randint(0, app.cols-1)
    if app.map[x][y]==False:
        return False
    else:
        app.mischief.append(Rat(x, y))

def timerFired(app):
    if not app.paused and app.currScreen == 'game':
        for i in range(len(app.mischief)):
            rat = app.mischief[i]
            rat.moveRat(app, i)
        if app.timerCount % 10 == 0:
            spawnRat(app)
        exterminate(app)
        isRatCaught(app)
    
    app.timerCount += 1
    if len(app.mischief) > 6:
        app.paused = True
        app.currScreen = 'gameOver'

def drawRats(app, canvas):
    for rat in app.mischief:
        x0, y0, x1, y1 = getCellBounds(app, rat.x, rat.y)
        margin = app.width*0.001
        canvas.create_oval(x0+margin, y0+margin, x1-margin, y1-margin, fill='gray')

def winCond(app):
    if app.caught > 5:
        app.currScreen == 'win'

def isRatCaught(app):
    for i in range(len(app.mischief)-1, -1, -1):
        rat = app.mischief[i]
        if rat.x == app.kai.row and rat.y == app.kai.col:
            app.caught += 1
            app.mischief.pop(i)

################################################################################
#
# NOT CLASSES
#
################################################################################

def appStarted(app):
    restartGame(app)
    app.map = tp.testmap
    app.rows = len(app.map)
    app.cols = len(app.map[0])
    app.margin = 5
    app.backButton = Button(30, app.height - 60, 80, 40, 'back')
    app.controls = Controls()
    app.controls.createControlButtons(app)
    app.timerDelay = 100
    app.timerCount = 0
    app.caught = 0
    app.splashScreen = app.loadImage('https://media.discordapp.net/attachments/1038491384644124702/1038849857013678091/donner.png?width=589&height=589')

def restartGame(app):
    app.currScreen = 'splash'
    app.prevScreen = list()
    app.prevScreen.append(app.currScreen)
    app.mischief = []
    app.kai = Player(2, 2)
    app.paused = True

################################################################################
#
# GRAPHICS
#
################################################################################
def redrawAll(app, canvas):
    if app.currScreen == 'splash':
        drawSplashScreen(app, canvas)
    elif app.currScreen == 'game':
        drawGameScreen(app, canvas)
        if app.paused == True:
            drawPauseScreen(app, canvas)
        drawRats(app, canvas)
    elif app.currScreen == 'credits':
        drawCreditsScreen(app, canvas)
    elif app.currScreen == 'controls':
        drawSettingsScreen(app, canvas)
    elif app.currScreen == 'gameOver':
        drawGameOverScreen(app, canvas)
    elif app.currScreen == 'win':
        drawGameWinScreen(app, canvas)


def drawSplashScreen(app, canvas):
    introFontSize = 40
    canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.splashScreen))
    startButton = Button(app.width/2-75, app.height*0.57, 150, 50, 'start')
    creditsButton = Button(app.width/2-75, app.height*0.83, 150, 50, 'credits')
    settingsButton = Button(app.width/2-75, app.height*0.7, 150, 50, 'controls')
    creditsButton.drawButton(app, canvas)
    settingsButton.drawButton(app, canvas)
    startButton.drawButton(app, canvas)

def drawCreditsScreen(app, canvas):
    # TODO: write when we're basically done
    canvas.create_text(app.width/2, app.height/2 - 0.35*app.height, 
                       font='Arial 40 bold', text='Credits')
    canvas.create_text(app.width/2, app.height/2 - 0.25*app.height, 
                       font='Arial 20', text='apmenon, cnnadozi, gyanepss, emilyjia')
    canvas.create_text(app.width/2, app.height/2 - 0.1*app.height, font='Arial 20', text='Rat tamer: gyanepss')
    canvas.create_text(app.width/2, app.height/2 + 0.05*app.height, font='Arial 20', text='Splash screen: emilyjia')
    canvas.create_text(app.width/2, app.height/2 + .2*app.height, font='Arial 20', text='Video: apmenon, cnnadozi')
    canvas.create_text(app.width/2, app.height/2 + 0.35*app.height, font='Arial 20', text='Rat catcher: Kai')
    app.backButton.drawButton(app, canvas)

def drawSettingsScreen(app, canvas):
    canvas.create_text(app.width/2, app.height/2 - 0.35*app.height, 
                       font='Arial 40 bold', text='Controls')
    canvas.create_text(app.width/2, app.height/2 - 0.2*app.height, font='arial 20', text='You are Kai. You live in Donner.')
    canvas.create_text(app.width/2, app.height/2, font='Arial 20', text='Run into the rats to catch them!')
    for button in app.controlButtons:
        button.drawButton(app, canvas)
    app.backButton.drawButton(app, canvas)

def drawGameScreen(app, canvas):
    drawBoard(app, canvas)
    app.kai.drawPlayer(app, canvas)

def drawPauseScreen(app, canvas):
    margin = app.width*0.05
    canvas.create_rectangle(margin, margin, app.width-margin, app.height-margin, fill='#ccd9ff')
    canvas.create_text(app.width/2, margin+app.height*0.06, font='Arial 20', text='Paused')
    resumeButton = Button(app.width/2-0.18*app.width, app.height/2 - 70, 0.36*app.width, 60, 'resume')
    resumeButton.drawButton(app, canvas)
    exitGame = Button(app.width/2-0.18*app.width, app.height/2 + 40, 0.36*app.width, 60, 'menu')
    exitGame.drawButton(app, canvas)
    creditsButton = Button(app.width/2-75, app.height*0.83, 150, 40, 'credits')
    settingsButton = Button(app.width/2-75, app.height*0.7, 150, 40, 'controls')
    settingsButton.drawButton(app, canvas)
    creditsButton.drawButton(app, canvas)
    app.backButton.drawButton(app, canvas)

def drawGameOverScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill='pink')
    canvas.create_text(app.width/2, app.height/2 - 10, font='Arial 20', text='Game Over')
    canvas.create_text(app.width/2, app.height/2 + 30, font='Arial 14', text='You were overrun by rats.')
    canvas.create_text(app.width/2, app.height/2 + 50, font='Arial 14', text='Press escape to restart')

def drawGameWinScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill='pink')
    canvas.create_text(app.width/2, app.height/2 - 10, font='Arial 20', text='You have vanquished the vermin of Donner Dungeon!')
    canvas.create_text(app.width/2, app.height/2 + 30, font='Arial 14', text='You have earned your freedom. You may now return to debugging code instead of buildings.')
    canvas.create_text(app.width/2, app.height/2 + 50, font='Arial 14', text='Press escape to restart')

def mousePressed(app, event):
    buttonPressed = Button.getButton(app, event)
    if buttonPressed != None:
        buttonName = buttonPressed.label.lower()
        for button in Button.buttonList:
            button.isVisible = False
        if buttonName == 'back' and len(app.prevScreen) != 0: # should work for whatever 
            # TODO: properly update app.prevScreen
            app.currScreen = app.prevScreen[-1]
        if app.currScreen == 'splash':
            # pressing the buttons that are on the splashscreen
            if buttonName == 'start':
                app.paused = False
                app.currScreen = 'game'
            elif buttonName == 'controls':
                app.currScreen = 'controls'
            elif buttonName == 'credits':
                app.currScreen = 'credits'
        elif app.currScreen == 'game':
            if buttonName == 'resume':
                app.paused = False
            elif buttonName == 'controls':
                app.currScreen = 'controls'
            elif buttonName == 'credits':
                app.currScreen = 'credits'
            elif buttonName == 'menu':
                app.prevScreen.append('splash')
                app.currScreen = 'splash'
        if not app.currScreen == 'game':
            app.paused = True


def keyPressed(app, event):
    key = event.key.lower() # use key so we don't have to worry about capitalization
    if not app.paused and app.currScreen == 'game':
        if key == 'w':
            app.kai.movePlayer(app, -1, 0)
        elif key == 'a':
            app.kai.movePlayer(app, 0, -1)
        elif key == 's':
            app.kai.movePlayer(app, 1, 0)
        elif key == 'd':
            app.kai.movePlayer(app, 0, 1)
        elif key == 'escape':
            app.paused = True
            app.prevScreen.append('game')
    elif app.paused and app.currScreen == 'game':
        if key == 'escape':
            app.paused = False
    elif key == 'escape' and app.currScreen == 'gameOver':
        restartGame(app)
    elif key == 'escape' and len(app.prevScreen) != 0: # go back. might be fucky if this is also used to close inventory IDFK
        app.currScreen = app.prevScreen[-1]


def drawBoard(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            if app.map[row][col] == False:
                drawCell(app, canvas, row, col,'#2d3c52')
            else:
                drawCell(app,canvas,row,col,'white')


def getCellBounds(app, row, col):
    # aka "modelToView"
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = app.margin + col * cellWidth
    x1 = app.margin + (col+1) * cellWidth
    y0 = app.margin + row * cellHeight
    y1 = app.margin + (row+1) * cellHeight
    return (x0, y0, x1, y1)
    
def gameDimensions():
    rows = 150
    cols = 100
    cellSize = 2
    margin = 1
    return (rows, cols, cellSize, margin)

def drawCell(app, canvas, row, col, colour):
    if colour == None:
        x0, y0, x1, y1 = getCellBounds(app, row, col)
        canvas.create_rectangle(x0, y0, x1, y1, fill=app.board[row][col],
                                outline='black', width=4)
    else:
        x0, y0, x1, y1 = getCellBounds(app, row, col)
        canvas.create_rectangle(x0,y0, x1, y1, fill=colour,outline='#2d3c52', 
                                width=1)

# def getCell(app, x, y):
#     # aka "viewToModel"
#     # return (row, col) in which (x, y) occurred or (-1, -1) if outside grid.
#     if (not pointInGrid(app, x, y)):
#         return (-1, -1)
#     gridWidth  = app.width - 2*app.margin
#     gridHeight = app.height - 2*app.margin
#     cellWidth  = gridWidth / app.cols
#     cellHeight = gridHeight / app.rows

#     # Note: we have to use int() here and not just // because
#     # row and col cannot be floats and if any of x, y, app.margin,
#     # cellWidth or cellHeight are floats, // would still produce floats.
#     row = int((y - app.margin) / cellHeight)
#     col = int((x - app.margin) / cellWidth)
#     return (row, col)

def main():
    runApp(width=589, height=589)

main()