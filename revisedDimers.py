import tkinter
import math
import csv


_top = tkinter.Tk()
_canvas = tkinter.Canvas(_top, bg="black", bd=0, width=1920, height=1080)
def drawCircle(position, size, rgb):
    #this is half my screen's resolution
    originX = 768#1536
    originY = 432#864
    scale = 175
    
    centerX = originX + position[0] * scale
    centerY = originY - position[1] * scale
    scaledSize = size * scale
    left  = int(centerX - scaledSize)
    top   = int(centerY + scaledSize)
    right = int(centerX + scaledSize)
    down  = int(centerY - scaledSize)
    
    colour = '#%02x%02x%02x' % rgb
    
    _canvas.create_oval(left, top, right, down, width=0, fill=colour)



colourMapLandmarks = []
with open('CETperceptual_csv_0_255\\CET-L16.csv') as colourMapFile:
    csvReader = csv.reader(colourMapFile)
    for row in csvReader:
        red   = int(row[0])
        green = int(row[1])
        blue  = int(row[2])
        colourMapLandmarks.append( (red, green, blue) )
    colourMapFile.close()

def colourMap(position):
    assert position >= 0
    assert position <= 1
    
    def weierstrass(x):
        k=15
        a=0.5
        b=3
        out=0
        for i in range(k):
            out += math.pow(a, i) * math.cos( math.pow(b,i) * math.pi * x )
        return 1/2 * (1 - (1-a)*out)
    
    scaledPosition = weierstrass(position) * (len(colourMapLandmarks) - 1)
    intPosition = int(scaledPosition)
    nonIntPosition = scaledPosition - intPosition
    
    if scaledPosition == intPosition:
        red   = colourMapLandmarks[intPosition][0]
        green = colourMapLandmarks[intPosition][1]
        blue  = colourMapLandmarks[intPosition][2]
        return (red, green, blue)
    
    prevColour = colourMapLandmarks[intPosition]
    nextColour = colourMapLandmarks[intPosition + 1]
    
    red   = round(nonIntPosition * prevColour[0] + (1-nonIntPosition) * nextColour[0])
    green = round(nonIntPosition * prevColour[1] + (1-nonIntPosition) * nextColour[1])
    blue  = round(nonIntPosition * prevColour[2] + (1-nonIntPosition) * nextColour[2])
    
    return (red, green, blue)


class Tree:
    def __init__(self, value):
        self.left = None
        self.right = None
        self.value = value

#these methods will handle doubles of reals (i.e. vectors)

#flip a vector along the line spanned by another
def flip(vec1, vec2):
    v1dotv2 = vec1[0]*vec2[0] + vec1[1]*vec2[1]
    v2dotv2 = vec2[0]*vec2[0] + vec2[1]*vec2[1]
    v1Parr = mult(v1dotv2 / v2dotv2, vec2)
    v1Perp = sub(vec1, v1Parr)
    return sub(v1Parr, v1Perp)

def add(vec1, vec2):
    return (vec1[0]+vec2[0], vec1[1]+vec2[1])

def sub(vec1, vec2):
    return (vec1[0]-vec2[0], vec1[1]-vec2[1])

def mult(scal, vec):
    return (scal * vec[0], scal * vec[1])

def rotate(vec, angle, CCW):
    if CCW:
        return ( vec[0] * math.cos(angle) - vec[1] * math.sin(angle)
               , vec[0] * math.sin(angle) + vec[1] * math.cos(angle))
    else:
        return ( vec[0] * math.cos(angle) + vec[1] * math.sin(angle)
               ,-vec[0] * math.sin(angle) + vec[1] * math.cos(angle))

#returns a tree of points at which to draw the simplified versions (circles?)
#only actually draw the simplest ones at the leaf nodes
#first 4 variables give the way to draw the dimer while the last 4 give the dimer type
def getDimerPoints(position, rotScale, flipped, level, rotM, flipM, rotP, flipP):
    if level < 1:
        return Tree(position)
    positionP = add(position, rotScale)
    rotScaleP = mult(1 / math.sqrt(2), rotScale)
    rotScaleP = rotate(rotScaleP, rotP, flipped)
    nextFlipP = flipped
    if flipP:
        rotScaleP = flip(rotScaleP, rotScale)
        nextFlipP = not flipped
    
    
    positionM = sub(position, rotScale)
    rotScaleM = mult(1 / math.sqrt(2), rotScale)
    rotScaleM = rotate(rotScaleM, rotM, flipped)
    nextFlipM = flipped
    if flipM:
        rotScaleM = flip(rotScaleM, rotScale)
        nextFlipM = not flipped
    
    
    dimerP = getDimerPoints(positionP, rotScaleP, nextFlipP, level-1, rotM, flipM, rotP, flipP)
    dimerM = getDimerPoints(positionM, rotScaleM, nextFlipM, level-1, rotM, flipM, rotP, flipP)
    
    currentDimer = Tree(position)
    currentDimer.left = dimerM
    currentDimer.right = dimerP
    
    return currentDimer


#revM and revP are for the colour map to deal with
def drawDimer(level, rotM, flipM, rotP, flipP, revM, revP):
    dimerPoints = getDimerPoints((0,0), (1,0), False, level, rotM, flipM, rotP, flipP)
    #if the rotScale is to be changed, scale circleSize by the magnitude of rotScale
    circleSize = ( math.sqrt(2) / (math.sqrt(2) - 1) ) / math.pow(math.sqrt(2), level)
    
    def drawCircles(pointTree, start, end):
        middle = (start + end) / 2
        if pointTree.left == None:
            drawCircle(pointTree.value, circleSize, colourMap(middle))
        else:
            if revM:
                drawCircles(pointTree.left, middle, start)
            else:
                drawCircles(pointTree.left, start, middle)
            
            if revP:
                drawCircles(pointTree.right, end, middle)
            else:
                drawCircles(pointTree.right, middle, end)
    
    drawCircles(dimerPoints, 0.0, 1.0)

pi = math.pi
drawDimer(16, 1*pi/4, True, 3*pi/4, False, False, False)

_canvas.pack()
_top.mainloop()















