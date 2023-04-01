from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtOpenGLWidgets import *
from OpenGL.GLU import *
from OpenGL.GL import *
from PIL import Image
import numpy as np
from .blend_image import blend_image
from . import config

class Navball(QWidget):
    def __init__(self):
        super().__init__()
        self.glw = NavballGL(self)
        r = self.size()
        self.cursor = QLabel(self)
        self.cursor.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.update_style()
        self.resizeEvent(None)
        QApplication.instance().paletteChanged.connect(self.update_style)

    def update_style(self, palette=None):
        palette = palette or self.palette()
        color = palette.color(QPalette.Highlight)
        self.cursor.setPixmap(QPixmap(blend_image(config.CURSOR_MASK, color)))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        w, h = self.size().width(), self.size().height()
        mn = min(w, h)
        # center the widget
        self.glw.setGeometry((w - mn) // 2, (h - mn) // 2, mn, mn)
        self.cursor.setGeometry((w - mn) // 2, (h - mn) // 2, mn, mn)
        self.glw.update()

    def setAngle(self, x, y, z):
        self.glw.angle[0] = x
        self.glw.angle[1] = y
        self.glw.angle[2] = z
        self.glw.update()


class NavballGL(QOpenGLWidget):
    def __init__(self, parent):
        super().__init__(parent)
        r = self.geometry()
        self.angle = [0, 0, 0]
        self.update_gl = True
        self.tex = None
        QApplication.instance().paletteChanged.connect(self.update_style)
        self.update_style()

    def update_style(self):
        self.update_gl = True
        self.color = self.palette().color(QPalette.Window)
        img = Image.open(blend_image(config.NAVBALL_MASK, self.color))
        self.img_data = np.asarray(img, np.int8)
        self.img_data = self.img_data[:, :, :3]
        print(self.img_data.shape)
        self.img_data = np.array(self.img_data, copy=True)

    def initializeGL(self):
        width, height = self.size().width(), self.size().height()
        glEnable(GL_MULTISAMPLE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        lightZeroPosition = [10., 4., 10., 1.]
        lightZeroColor = [0.8, 1.0, 0.8, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)
        glViewport(0, 0, self.width(), self.height())
        glMatrixMode(GL_PROJECTION)
        gluPerspective(40., 1., 1., 40.)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 10,
                  0, 0, 0,
                  0, 1, 0)
        glEnable(GL_MULTISAMPLE)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def paintGL(self):
        if self.update_gl:
            self.update_gl = False
            glClearColor(self.color.redF(), self.color.greenF(), self.color.blueF(), 1)
            if self.tex:
                glDeleteTextures(1, self.tex)
            self.tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.tex)
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
            h = self.img_data.shape[0]
            w = self.img_data.shape[1]
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0,
                         GL_RGB, GL_UNSIGNED_BYTE, self.img_data)  # TODO

        glPushMatrix()
        qobj = gluNewQuadric()
        gluQuadricTexture(qobj, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.tex)

        glRotatef(self.angle[2], 0, 0, 1)
        glRotatef(self.angle[0] + 90, 1, 0, 0)
        glRotatef(self.angle[1] - 180, 0, 0, 1)

        gluSphere(qobj, 3.2, 360, 360)
        gluDeleteQuadric(qobj)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40., 1., 1., 40.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, 10,
                  0, 0, 0,
                  0, 1, 0)


if __name__ == "__main__":
    import sys

    class MainWindow(QDialog):
        def __init__(self, parent=None):
            super(MainWindow, self).__init__(parent)
            self.timer = QTimer(self)
            self.navball = Navball()
            self.setGeometry(0, 0, 512, 512)
            layout = QGridLayout()
            layout.addWidget(self.navball, 0, 0, 1, 1)
            self.setLayout(layout)
            self.timer.timeout.connect(self.update_widget)
            self.timer.start(1000 / 60)
            self.data = np.zeros(3)

        def update_widget(self):
            self.data += 1
            self.navball.setAngle(*self.data)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    r = app.exec()
    sys.exit(r)
