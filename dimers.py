import tkinter

def convert(mag, angle): #if angle is odd, mag is actual mangitude / sqrt(2)
    if angle % 2 >= 1:
        output = (mag,mag)
    else:
        output = (mag,0)

    if angle % 4 >= 2:
        output = (-output[1], output[0])

    if angle % 8 >= 4:
        output = (-output[0], -output[1])

    return output

def createDimer(canvas, level, angle1, flip1, angle2, flip2, x, y, flipped, speed, direction, colour):
    #print(level, angle1, flip1, angle2, flip2, speed, direction, flipped, x, y)
    if level == 0:
        #print(x,y)
        canvas.create_rectangle(int(x), int(y), int(x+2), int(y+2), fill=colour, outline="")
    else:
        #print(direction)
        newSpeed = speed
        if direction % 2 == 0:
            newSpeed = newSpeed // 2
        if flipped:
            newDirA = direction - angle1
        else:
            newDirA = direction + angle1
        vel = convert(speed, direction)
        newXA = x + vel[0]
        newYA = y + vel[1]
        newFlipA = flipped
        if flip1:
            newFlipA = not newFlipA

        createDimer(canvas, level-1, angle1, flip1, angle2, flip2, newXA, newYA, newFlipA, newSpeed, newDirA, colour)

        if flipped:
            newDirB = direction - angle2
        else:
            newDirB = direction + angle2
        newXB = x - vel[0]
        newYB = y - vel[1]
        newFlipB = flipped
        if flip2:
            newFlipB = not newFlipB

        createDimer(canvas, level-1, angle1, flip1, angle2, flip2, newXB, newYB, newFlipB, newSpeed, newDirB, colour)

def showcaseDimer(canvas, level, angle1, flip1, angle2, flip2, x, y, cardinalDir):
    speed = 2 ** int((level-1) / 2)
    trueDir = cardinalDir * 2
    if level % 2 == 0:
        trueDir += 1

    newSpeed = speed
    if trueDir % 2 == 0:
        newSpeed = newSpeed // 2
    newDirA = trueDir + angle1
    vel = convert(speed, trueDir)
    newXA = x + vel[0]
    newYA = y + vel[1]
    newFlipA = False
    if flip1:
        newFlipA = not newFlipA

    createDimer(canvas, level-1, angle1, flip1, angle2, flip2, newXA, newYA, newFlipA, newSpeed, newDirA, "red")
    #print()


    newDirB = trueDir + angle2
    newXB = x - vel[0]
    newYB = y - vel[1]
    newFlipB = False
    if flip2:
        newFlipB = not newFlipB

    createDimer(canvas, level-1, angle1, flip1, angle2, flip2, newXB, newYB, newFlipB, newSpeed, newDirB, "blue")

top = tkinter.Tk()

C = tkinter.Canvas(top, bg="white", bd=0, width=1920, height=1080)

showcaseDimer(C, 15, 7, False, 3, True, 650, 400, 2)

C.pack()
top.mainloop()
