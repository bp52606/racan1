import numpy as np
import copy
import pyglet.clock
from pyglet.window import key
from pyglet import image
from pyglet.gl import *
from Vrh import Vrh
from PolyElem import PolyElem
from Brid import Brid
from pyglet.gl import *
from Point3D import Point3D
import math

width = 1000
height = 500
window = pyglet.window.Window(width, height)
triCol = [0.0, 0.0, 0.0]
glColor3f(triCol[0], triCol[1], triCol[2])
glClearColor(0.0, 0.0, 0.0, 0.0)
glClear(GL_COLOR_BUFFER_BIT)
cameraPositon = (1.0, 1.0, 1.3)
lookAt = (0.0, 0.0, 0.0)
upVector = (0.0, 1.0, 0.0)

f = open("palm.obj", "r")
lines = f.readlines()

ociste = Vrh(1,1,3)
glediste = Vrh(0,0,0)
izvor = Vrh(2,4,5)
vrhovi = []
polyelems = []
bridovi = []
bridovi2 = []

tocke = []
krivulja = []
t = 0

myTime = 0
mySeg = 0

gouraudChosen = False
shadow = False
state_down = False

for line in lines:
    elements = line.split(" ")
    if elements[0] == "v":
        v = Vrh()
        v.x = float(elements[1])
        v.y = float(elements[2])
        v.z = float(elements[3])

        vrhovi.append(v)

    elif elements[0] == "f":
        poliVrhovi = []
        for i in elements:
            if i != "f":
                copyV = int(i) - 1
                poliVrhovi.append(copyV)
        p = PolyElem(vrh=poliVrhovi)
        polyelems.append(p)


vrhs = copy.deepcopy(vrhovi)

x_center = np.sum(np.array([i.x for i in vrhs])) / len(vrhs)
y_center = np.sum(np.array([i.y for i in vrhs])) / len(vrhs)
z_center = np.sum(np.array([i.z for i in vrhs])) / len(vrhs)

xmin = vrhovi[np.argmin(np.array([i.x for i in vrhovi]))].x
ymin = vrhovi[np.argmin(np.array([i.y for i in vrhovi]))].y
zmin = vrhovi[np.argmin(np.array([i.z for i in vrhovi]))].z
xmax = vrhovi[np.argmax(np.array([i.x for i in vrhovi]))].x
ymax = vrhovi[np.argmax(np.array([i.y for i in vrhovi]))].y
zmax = vrhovi[np.argmax(np.array([i.z for i in vrhovi]))].z

for ind in range(0, len(polyelems)):
    x_origin = np.array([vrhovi[i].x for i in polyelems[ind].vrh])
    y_origin = np.array([vrhovi[i].y for i in polyelems[ind].vrh])
    z_origin = np.array([vrhovi[i].z for i in polyelems[ind].vrh])

    # skaliraj na [-1,1]
    x_scale = np.array([(((i - xmin) * (1 - (-1))) / (xmax - xmin)) + (-1) for i in x_origin])
    y_scale = np.array([(((i - ymin) * (1 - (-1))) / (ymax - ymin)) + (-1) for i in y_origin])
    z_scale = np.array([(((i - zmin) * (1 - (-1))) / (zmax - zmin)) + (-1) for i in z_origin])

    v1 = Vrh()
    v2 = Vrh()
    v3 = Vrh()
    v1.x = x_scale[0]
    v1.y = y_scale[0]
    v1.z = z_scale[0]
    v2.x = x_scale[1]
    v2.y = y_scale[1]
    v2.z = z_scale[1]
    v3.x = x_scale[2]
    v3.y = y_scale[2]
    v3.z = z_scale[2]

    vrhs[polyelems[ind].vrh[0]] = v1
    vrhs[polyelems[ind].vrh[1]] = v2
    vrhs[polyelems[ind].vrh[2]] = v3


# odredi koeficijente jednadzbe ravnine

for poligon in polyelems:
    brid = Brid()
    brid.a = (vrhs[poligon.vrh[1]].y - vrhs[poligon.vrh[0]].y) * (vrhs[poligon.vrh[2]].z - vrhs[poligon.vrh[0]].z) - \
             ((vrhs[poligon.vrh[1]].z - vrhs[poligon.vrh[0]].z) * (vrhs[poligon.vrh[2]].y - vrhs[poligon.vrh[0]].y))
    brid.b = -((vrhs[poligon.vrh[1]].x - vrhs[poligon.vrh[0]].x) * (vrhs[poligon.vrh[2]].z - vrhs[poligon.vrh[0]].z)) + \
             ((vrhs[poligon.vrh[1]].z - vrhs[poligon.vrh[0]].z) * (vrhs[poligon.vrh[2]].x - vrhs[poligon.vrh[0]].x))
    brid.c = (vrhs[poligon.vrh[1]].x - vrhs[poligon.vrh[0]].x) * (vrhs[poligon.vrh[2]].y - vrhs[poligon.vrh[0]].y) - \
             ((vrhs[poligon.vrh[1]].y - vrhs[poligon.vrh[0]].y) * (vrhs[poligon.vrh[2]].x - vrhs[poligon.vrh[0]].x))
    poligon.brid = brid
    poligon.D = -vrhs[poligon.vrh[0]].x * brid.a - vrhs[poligon.vrh[0]].y * brid.b - vrhs[poligon.vrh[0]].z * brid.c
    bridovi.append(brid)


# spremi koordinate tocaka putanje
putanja = []
putanja.append(Vrh(0,0,0))
putanja.append(Vrh(0,10,5))
putanja.append(Vrh(10,10,10))
putanja.append(Vrh(10,0,15))
putanja.append(Vrh(0,0,20))
putanja.append(Vrh(0,10,25))
putanja.append(Vrh(10,10,30))
putanja.append(Vrh(10,0,35))
putanja.append(Vrh(0,0,40))
putanja.append(Vrh(0,10,45))
putanja.append(Vrh(10,10,50))
putanja.append(Vrh(10,0,55))

# odredi skupove tocaka koji definiraju segmente putanje

def segmentiPutanje():
    global putanja
    segmenti = []
    n = len(putanja)

    for i in range(1,n-2,1):
        segmenti.append((putanja[i-1], putanja[i], putanja[i+1], putanja[i+2]))

    return segmenti


def pronadi_orijentacije():
    segmenti = segmentiPutanje()
    B = np.array([[-1/6, 3/6, -3/6, 1/6], [3/6, -6/6, 3/6, 0/6], [-3/6, 0/6, 3/6, 0/6],[1/6,4/6,1/6,0/6]])

    orijentacije = []

    for segment in segmenti:

        pi = dict()

        for t in np.arange(0,1,0.1):
            t = round(t, 1)
            T = np.array([3*t**2,2*t,1,0])
            pi_t = np.dot(T,B)
            pi_t = np.dot(pi_t, np.array([segment[0].to_arr(),segment[1].to_arr(),segment[2].to_arr(),segment[3].to_arr()]))
            pi[t] = pi_t

        orijentacije.append(pi)

    return orijentacije


def rotacija(pocetak, cilj):
    os = np.array([[pocetak[1]*cilj[2]-(cilj[1]*pocetak[2])],[-(pocetak[0]*cilj[2]-(cilj[0]*pocetak[2]))],
          [pocetak[0]*cilj[1]-(cilj[0]*pocetak[1])]])

    cosfi = (np.dot(pocetak,cilj))/((math.sqrt(pocetak[0]**2+pocetak[1]**2+pocetak[2]**2))*(math.sqrt(cilj[0]**2+cilj[1]**2+cilj[2]**2)))
    return (os, math.degrees(math.acos(cosfi)))

def translacija():
    segmenti = segmentiPutanje()
    B = np.array([[-1/6, 3/6, -3/6, 1/6], [3/6, -6/6, 3/6, 0/6], [-3/6, 0/6, 3/6, 0/6],[1/6,4/6,1/6,0/6]])

    translacije = []

    for segment in segmenti:

        pi = dict()

        for t in np.arange(0, 1, 0.1):

            t = round(t,1)
            T = np.array([t**3, t ** 2, t, 1])
            pi_t = np.dot(T, B)
            pi_t = np.dot(pi_t, np.array([segment[0].to_arr(),segment[1].to_arr(),segment[2].to_arr(),segment[3].to_arr()]))

            pi[t] = pi_t

        translacije.append(pi)

    return translacije


def ticker(a,b):
    global myTime
    global mySeg

    if round(myTime,1)==0.9:
        myTime=0
        mySeg += 1
        if mySeg == len(segmentiPutanje()):
            mySeg = 0
    else:
        myTime += 0.1



@window.event
def on_draw():
    global vrhs
    global polyelems
    global putanja

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, 2, 0.2, 100)
    gluLookAt(cameraPositon[0], cameraPositon[1], cameraPositon[2],
              lookAt[0], lookAt[1], lookAt[2],
              upVector[0], upVector[1], upVector[2])
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(1.0, 1.0, 1.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)

    orijentacije = pronadi_orijentacije()
    translacije = translacija()
    glBegin(GL_LINE_STRIP)
    for i,value in enumerate(orijentacije):
        for key in value:
            glVertex3f(translacije[i][key][0]/55,
                       translacije[i][key][1]/55,
                       translacije[i][key][2]/55)

            glVertex3f(translacije[i][key][0]/55+orijentacije[i][key][0]/55,
                       translacije[i][key][1]/55+orijentacije[i][key][1]/55,
                       translacije[i][key][2]/55+orijentacije[i][key][2]/55
                       )


    glEnd()

    os, kut = rotacija([0,0,1], [orijentacije[mySeg][round(myTime,1)][0],orijentacije[mySeg][round(myTime,1)][1],orijentacije[mySeg][round(myTime,1)][2]])
    glTranslatef(translacije[mySeg][round(myTime,1)][0]/55,translacije[mySeg][round(myTime,1)][1]/55,translacije[mySeg][round(myTime,1)][2]/55)
    glRotatef(kut, os[0],os[1],os[2])

    glBegin(GL_LINES)

    for poly in polyelems:
        for i in range(0, len(poly.vrh) - 1):
            glVertex3f(vrhs[poly.vrh[i]].x/10,
                       vrhs[poly.vrh[i]].y/10,
                       vrhs[poly.vrh[i]].z/10)
            glVertex3f(vrhs[poly.vrh[i+1]].x/10,
                       vrhs[poly.vrh[i+1]].y/10,
                       vrhs[poly.vrh[i+1]].z/10)
        glVertex3f(vrhs[poly.vrh[len(poly.vrh) - 1]].x/10,
                   vrhs[poly.vrh[len(poly.vrh) - 1]].y/10,
                   vrhs[poly.vrh[len(poly.vrh) - 1]].z/10)
        glVertex3f(vrhs[poly.vrh[0]].x/10,
                   vrhs[poly.vrh[0]].y/10,
                   vrhs[poly.vrh[0]].z/10)
    glEnd()

    glFlush()


@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, - 1, 1)
    glMatrixMode(GL_MODELVIEW)


pyglet.clock.schedule(ticker,1/5.0)
pyglet.app.run()
