import tkinter
import math
import csv

screenWidth = 16*120
screenHeight = 9*120

background = (0,0,0)
colourMap = "CET-L16"

_top = tkinter.Tk()
_canvas = tkinter.Canvas(_top, bg="black", bd=0, width=screenWidth, height=screenHeight)
img = tkinter.PhotoImage(width=screenWidth, height=screenHeight)
_canvas.create_image((0, 0), image=img, state="normal", anchor="nw")


center = (0.0, 0.0)
scale = 200.0


#x and y are pixel coordinates
def drawPoint(x, y, level, rotM, flipM, rotP, flipP, revM, revP):
	screenCenterX = screenWidth/2
	screenCenterY = screenHeight/2
	
	pixelX = x - screenCenterX
	pixelY = screenCenterY - y
	
	pointX = pixelX / scale + center[0]
	pointY = pixelY / scale + center[1]
	
	rgb = getColourOf((pointX, pointY), level, rotM, flipM, rotP, flipP, revM, revP)
	
	colour = '{#%02x%02x%02x}' % rgb
	
	img.put(colour, to=(x,y))



colourMapLandmarks = []
with open('CETperceptual_csv_0_255\\' + colourMap + '.csv') as colourMapFile:
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



#these methods will handle doubles of reals (i.e. vectors)

#flip a vector along the x axis
def flip(vec):
	return (vec[0], -vec[1])

def add(vec1, vec2):
	return (vec1[0]+vec2[0], vec1[1]+vec2[1])

def sub(vec1, vec2):
	return (vec1[0]-vec2[0], vec1[1]-vec2[1])

def mult(scal, vec):
	return (scal * vec[0], scal * vec[1])

def rotate(vec, angle):
	return ( vec[0] * math.cos(angle) - vec[1] * math.sin(angle)
		   , vec[0] * math.sin(angle) + vec[1] * math.cos(angle))

def magSqr(vec):
	return vec[0]*vec[0] + vec[1]*vec[1]

#returns the place within the dimer that the point is at (and an invalid location if nowhere)
#this place can be read as being the location of going along X path at each step
def getDimerPosition(position, level, rotM, flipM, rotP, flipP):
	escCircleRSqr = (math.sqrt(2) / (math.sqrt(2) - 1)) * (math.sqrt(2) / (math.sqrt(2) - 1))
	
	if magSqr(position) > escCircleRSqr:
		return "Out"
	
	
	prevLevelPositions = {(position, "")}
	for i in range(level):
		nextLevelPositions = set()
		
		for currentPositionTuple in prevLevelPositions:
			currentPosition = currentPositionTuple[0]
			pathToReach = currentPositionTuple[1]
			
			#find the position if the M transformation is undone:
			#undo the translation
			positionDeM = add(currentPosition, (1,0))
			#undo the rotation
			positionDeM = rotate(positionDeM, -rotM)
			#undo the flip
			if flipM:
				positionDeM = flip(positionDeM)
			positionDeM = mult(math.sqrt(2), positionDeM)
	
			#find the position if the P transformation is undone:
			#undo the translation
			positionDeP = add(currentPosition, (-1,0))
			#undo the rotation
			positionDeP = rotate(positionDeP, -rotP)
			#undo the flip
			if flipP:
				positionDeP = flip(positionDeP)
			positionDeP = mult(math.sqrt(2), positionDeP)
			
			# add the valid ones that remain to the set of positions to check
			if magSqr(positionDeM) <= escCircleRSqr:
				nextLevelPositions.add( (positionDeM, pathToReach + "M") )
			if magSqr(positionDeP) <= escCircleRSqr:
				nextLevelPositions.add( (positionDeP, pathToReach + "P") )
		
		#if we've reached a point where no path fits, that means we're not in the dimer at all
		if not nextLevelPositions:
			return "Out"
		
		prevLevelPositions = nextLevelPositions
	
	#by this point, all the prevLevelPositions agree with this point so...
	finalPositionTuple = prevLevelPositions.pop()
	return finalPositionTuple[1]


#revM and revP are for the colour map to deal with
def getColourOf(position, level, rotM, flipM, rotP, flipP, revM, revP):
	dimerLocation = getDimerPosition(position, level, rotM, flipM, rotP, flipP)
	
	if dimerLocation == "Out":
		return background
	
	start = 0.0
	end   = 1.0
	for instr in dimerLocation:
		middle = (start + end)/2
		if instr == 'M':
			if revM:
				end = start
				start = middle
			else:
				end = middle
		elif instr == 'P':
			if revP:
				start = end
				end = middle
			else:
				start = middle
		else:
			assert False
	
	return colourMap( (start + end)/2 )

pi = math.pi
#drawDimer(16, 1*pi/4, True, 3*pi/4, False, False, False)


def task(y):
	print(y/screenHeight)
	for x in range(screenWidth):
		drawPoint(x, y, 50, 1*pi/4, False, 1*pi/4, False, False, False)
	if y < screenHeight:
		_top.after(10, task, y+1)


_canvas.pack()
_top.after(10, task, 0)
_top.mainloop()