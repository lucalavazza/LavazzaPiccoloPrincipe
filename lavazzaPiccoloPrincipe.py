from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL.Image import *
from math import *

# Memo per me:
#   x verso destra
#   y verso l'alto
#   z verso di me

# Alcuni valori utili
rot_asse = 0.0
rot_orbita = 0.0
raggio_terra = 2.3
raggio_luna = 0.6
limite_max = 1000
limite_min = 0.001
texture = 0
camera = [0.0, 0.0, -20.0]
angolo_sugiu = 0.0
angolo_sxdx = 0.0


# Importo le texture dai file
def caricaTexture(filename):
    image = open(filename)
    ix = image.size[0]
    iy = image.size[1]

    # Ho dovuto fare una conversione a RGBA per ottenere la trasparenza

    image = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, 4, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture


# Creo il rettangolo su cui "incollare" la texture degli elementi del mondo
def creaElemento(texture, larghezza, altezza, raggio_sfera):
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)

    # le istruzioni commentate sono come sono arrivato a ottenere "l'incastramento"
    # del rettangolo nella sfera a tentativi.
    # Poi ho accorciato la formula e resa più leggibile.

    # glVertex3f(-larghezza/2, 0.0, raggio_sfera - (raggio_sfera/25))
    # glVertex3f(larghezza/2, 0.0, raggio_sfera - (raggio_sfera/25))
    # glVertex3f(larghezza/2, 0.0, raggio_sfera - (raggio_sfera/25) + altezza)
    # glVertex3f(-larghezza/2, 0.0, raggio_sfera - (raggio_sfera/25) + altezza)

    glNormal3f(0.0, 0.0, -1.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-larghezza / 2, 0.0, 24 * (raggio_sfera / 25))
    glNormal3f(0.0, 0.0, -1.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(larghezza/2, 0.0, 24 * (raggio_sfera / 25))
    glNormal3f(0.0, 0.0, -1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(larghezza/2, 0.0, 24 * (raggio_sfera / 25) + altezza)
    glNormal3f(0.0, 0.0, -1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-larghezza/2, 0.0, 24 * (raggio_sfera / 25) + altezza)
    glEnd()


# Inizializzazione
def init(Width, Height):
    global quadrica, \
        baobab, cielo, luna, principe, terra, volpe, fuoco, rosa, dugtrio, vulcano, sole

    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0.0)

    glEnable(GL_TEXTURE_2D)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.8, 0.8, 0.8])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.7, 0.15, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 0.7, 0.15, 1.0])
    glLightModelf(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

    principe = caricaTexture("texture/principe.png")
    dugtrio = caricaTexture("texture/dugtrio.png")
    vulcano = caricaTexture("texture/volcano.png")
    baobab = caricaTexture("texture/baobab.png")
    cielo = caricaTexture("texture/cielo.jpg")
    terra = caricaTexture("texture/terra.jpg")
    volpe = caricaTexture("texture/volpe.png")
    fuoco = caricaTexture("texture/fuoco.png")
    rosa = caricaTexture("texture/rosa.png")
    luna = caricaTexture("texture/luna.jpg")
    sole = caricaTexture("texture/sole.jpg")

    quadrica = gluNewQuadric()
    gluQuadricNormals(quadrica, GLU_SMOOTH)
    gluQuadricTexture(quadrica, GL_TRUE)

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width) / float(Height), limite_min, limite_max)


# Ridimensionamento
def resizeScene(w, h):
    if h == 0:
        h = 1

    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w) / float(h), limite_min, limite_max)
    glMatrixMode(GL_MODELVIEW)


# Creo la scena
def drawScene():
    global rot_asse, rot_orbita, texture, quadrica, \
        baobab, cielo, luna, principe, terra, volpe, fuoco, rosa, dugtrio, vulcano, sole, \
        raggio_terra, raggio_luna, limite_max, limite_min, \
        angolo_sugiu, angolo_sxdx

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)

    # Sky Dome
    glPushMatrix()
    # tolgo la proprietà di diffusione (altrimenti la fonte di luce crea problemi)
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.0, 0.0, 0.0, 1.0])
    # assegno una luce ambientale, altrimenti è troppo scuro
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.6, 0.6, 0.6, 1.0])
    glTranslatef(0.0, 0.0, -30.0)
    glRotatef(90, 1.0, 1.0, 0.0)
    glBindTexture(GL_TEXTURE_2D, cielo)
    gluSphere(quadrica, (limite_max/2), 32, 32)
    # restituisco la proprietà di diffusione
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glPopMatrix()

    glLoadIdentity()

    # Telecamera
    gluLookAt(camera[0], camera[1], camera[2],
              camera[0] + sin(radians(angolo_sxdx)) * cos(radians(angolo_sugiu)),
              camera[1] + sin(radians(angolo_sugiu)),
              camera[2] + cos(radians(angolo_sxdx)) * cos(radians(angolo_sugiu)),
              0.0, 1.0, 0.0)

    glPushMatrix()
    glRotate(90, 0.0, 1.0, 0.0)
    glRotate(-90, 1.0, 0.0, 0.0)

    # Sole luminoso
    glPushMatrix()
    glTranslatef(100.0, 450.0, 150.0)
    glRotatef(rot_asse/5, 0.0, 0.0, 1.0)
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])
    glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 0.7, 0.15, 1.0])
    glBindTexture(GL_TEXTURE_2D, sole)
    gluSphere(quadrica, 50, 32, 32)
    glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
    glPopMatrix()

    # Asteroide
    glPushMatrix()
    glRotatef(rot_asse, 1.0, -1.0, 0.0)
    glBindTexture(GL_TEXTURE_2D, terra)
    gluSphere(quadrica, raggio_terra, 32, 32)

    # Elementi sull'asteroide
    glPushMatrix()
    glRotatef(15, 0.0, 1.0, 0.0)
    glRotatef(65, -1.0, 0.0, 0.0)
    creaElemento(principe, 1.0, 2.0, raggio_terra)
    glPopMatrix()

    glPushMatrix()
    glRotatef(65, -1.0, 0.0, 0.0)
    creaElemento(volpe, 0.8, 0.8, raggio_terra)
    glPopMatrix()

    glPushMatrix()
    glRotatef(45, 1.0, 0.0, 0.0)
    for r in range(0, 180, 30):
        glPushMatrix()
        glRotatef(r,0.0, 0.0, 1.0)
        creaElemento(baobab, 3.5, 4.0, raggio_terra)
        glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glRotatef(200, 1.0, 0.0, 0.0)
    for r in range(0, 180, 30):
        glPushMatrix()
        glRotatef(r, 0.0, 0.0, 1.0)
        creaElemento(vulcano, 2.0, 0.8, raggio_terra - 0.05)
        glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glRotatef(87, 1.0, 0.0, 0.0)
    glRotatef(78, 0.0, 1.0, 0.0)
    for r in range(0, 180, 90):
        glPushMatrix()
        glRotatef(r, 0.0, 0.0, 1.0)
        creaElemento(fuoco, 1.3, 0.9, raggio_terra)
        glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glRotatef(55, 1.0, 0.0, 0.0)
    glRotatef(95, 0.0, -1.0, 0.0)
    creaElemento(rosa, 0.8, 0.8, raggio_terra - 0.05)
    glPopMatrix()

    glPopMatrix()

    # Orbita del satellite intorno all'asteroide
    glPushMatrix()
    glRotatef(rot_orbita, 1.0, 1.0, 0.0)

    # Satellite
    glPushMatrix()
    glTranslatef(0.0, 0.0, -9.0)
    glRotatef(rot_asse, 1.0, -1.0, 0.0)
    glBindTexture(GL_TEXTURE_2D, luna)
    gluSphere(quadrica, raggio_luna, 50, 50)

    # Divertente elemento sul satellite
    glPushMatrix()
    glRotatef(65, -1.0, 0.0, 0.0)
    creaElemento(dugtrio, 0.4, 0.4, raggio_luna-0.05)
    glPopMatrix()

    glPopMatrix()

    glPopMatrix()

    glPopMatrix()

    glDisable(GL_TEXTURE_2D)

    rot_asse = rot_asse + 0.1
    rot_orbita = rot_orbita + 0.05

    glutSwapBuffers()


# Realizzato in autonomia, copiando dall'esercizio della lezione.
# Va bene finchè non giro la testa
# def keyboard(key, x, y):
#     global camera
#
#     if key.decode() == 'q':
#         sys.exit()
#     if key.decode() == 'w':
#         camera[2] += 1.0
#         glutPostRedisplay()
#         return
#     if key.decode() == 'a':
#         camera[0] += 1.0
#         glutPostRedisplay()
#         return
#     if key.decode() == 's':
#         camera[2] -= 1.0
#         glutPostRedisplay()
#         return
#     if key.decode() == 'd':
#         camera[0] -= 1.0
#         glutPostRedisplay()
#         return


def keyboard(key, x, y):
    global camera, rot_asse, rot_orbita

    # Metodo trovato su un forum e modificato a mia necessità per integrarlo al metodo visto a lezione
    # Nei commenti cerco di capire come e perchè funziona

    x_matrix = glGetFloat(GL_MODELVIEW_MATRIX)[0]  # = [1,0,0]
    y_matrix = glGetFloat(GL_MODELVIEW_MATRIX)[1]  # = [0,1,0]
    z_matrix = glGetFloat(GL_MODELVIEW_MATRIX)[2]  # = [0,0,1]

    if key.decode() == 'q':
        sys.exit()
        # la seguente è una piccola istruzione inutile, ma che ho trovato divertente e piacevole da aggiungere
    if key.decode() == 't':
        rot_asse += 50.0
        rot_orbita += 50.0
        glutPostRedisplay()
    if key.decode() == 'w':
        camera[0] -= x_matrix[2] * 1.0  # "La videocamera" nella direzione x (i.e. verso destra)
        camera[1] -= y_matrix[2] * 1.0  # "La videocamera" nella direzione y (i.e. verso l'alto)
        camera[2] -= z_matrix[2] * 1.0  # "La videocamera" nella direzione z (i.e. verso me)
        # print(x_matrix[2] * 1.0)
        # print(y_matrix[2] * 1.0)
        # print(z_matrix[2] * 1.0)
        glutPostRedisplay()
        return
        # Se non muovo "la testa", i print restituiscono
        #   0.0
        #   0.0
        #   -1.0
        # In effetti sto osservando lungo la direzione (0.0, 0.0, -1.0), i.e. perpendicolare "nello schermo"
        # Se muovo "la testa" a destra, i print restituiscono
        #   0.01
        #   0.0
        #   -0.99
        # Avendo guardato a destra, è comparsa una componente positiva lungo l'asse x
        # In sostanza questo metodo compensa per la rotazione e fa in modo che
        # 'w' mi faccia sempre muovere "perpendicolarmente allo schermo"
        # Quello che fa è sottrarre rispetto a tutte le componenti lungo x,y,z in modo da "andare dritto"

        # Cambiando il fattore di moltiplicazione (nel mio caso 1.0) cambia la quantità/velocità di spostamento

        # Il concetto è lo stesso per le altre direzioni

    if key.decode() == 'a':
        camera[0] -= x_matrix[0] * 1.0
        camera[1] -= y_matrix[0] * 1.0
        camera[2] -= z_matrix[0] * 1.0
        glutPostRedisplay()
        return
    if key.decode() == 's':
        camera[0] += x_matrix[2] * 1.0
        camera[1] += y_matrix[2] * 1.0
        camera[2] += z_matrix[2] * 1.0
        glutPostRedisplay()
        return
    if key.decode() == 'd':
        camera[0] += x_matrix[0] * 1.0
        camera[1] += y_matrix[0] * 1.0
        camera[2] += z_matrix[0] * 1.0
        glutPostRedisplay()
        return


def specialKeyboard(key, x, y):
    global angolo_sugiu, angolo_sxdx

    # Continuazione del metodo precedente trovato in rete.
    # Cerco di capire il motivo dei min, max e +-89
    # Il '% 360' è facile intuire sia legato all'aritmetica modulare
    #   --> dopotutto 360 gradi equivale a 0 gradi e così via

    if key == GLUT_KEY_UP:
        massimo = max(angolo_sugiu + 1.0, -89)
        angolo_sugiu = min(massimo, 89)
        glutPostRedisplay()
        return

        # Prima di tutto trova il massimo tra il valore dell'angolo+1 e -89
        #   se l'angolo è >= -90 --> ottengo l'angolo+1
        #   se l'angolo è <= -91 --> ottengo -89
        # Dopodichè trova il minimo tra quello ottenuto prima e 89
        #   se l'angolo era >= -90
        #       se -90 <= angolo <= 88 --> tengo l'angolo+1
        #       se angolo > 88 --> ottengo 89
        #   se l'angolo era <= -91 --> ottengo -89

        # Ricapitolando:
        # se angolo <= -91 --> -89
        # se -90 <= angolo <= 88 --> angolo
        # se angolo >= 89 -->  89
        # Ovvero:
        #   se è meno di -90 gradi -> -90 gradi
        #   se è tra -90 e 90 -> angolo
        #   se è più di 90 gradi -> 90 gradi

        # Sostanzialmente impedisce di "spezzarsi il collo".
        # Limita la visuale su e giù tra il guardare dritto sopra di sè e "guardarsi i piedi"

        # Stesso concetto per la frecia in giù

    if key == GLUT_KEY_LEFT:
        angolo_sxdx = (angolo_sxdx + 1.0) % 360
        return

        # Semplicemente, una volta che ho fatto un giro completo, riparto da 0 gradi.

        # Stessa cosa per la freccia a destra

    if key == GLUT_KEY_DOWN:
        angolo_sugiu = min(max(angolo_sugiu - 1.0, -89), 89)
        return
    if key == GLUT_KEY_RIGHT:
        angolo_sxdx = (angolo_sxdx - 1.0) % 360
        return


def main():
    glutInit()

    messaggio = "\nBenvenuto nel mondo del Piccolo Principe!\n" \
                "Usare i tasti WASD per muovere la telecamera,\n" \
                "le freccette per girare la testa,\n" \
                "e tenere premuto il tasto T per avviare il turbo!"

    print(messaggio)

    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_ALPHA)
    glutInitWindowSize(1920, 1080)
    glutInitWindowPosition(100, 100)
    glutCreateWindow("Luca Lavazza - Piccolo Principe")

    glutDisplayFunc(drawScene)
    glutIdleFunc(drawScene)
    glutReshapeFunc(resizeScene)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(specialKeyboard)
    init(1920, 1080)

    glutMainLoop()


if __name__ == "__main__":
    main()
