from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import os
from time import sleep
from multiprocessing import Process, Manager
import numpy as np
import sys

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, gas=None, temp=None, humid=None, radio=None, img=None):
        super().__init__()

        self.layout()

        self.gas = gas
        self.temp = temp
        self.humid = humid
        self.radio = radio
        self.img = img

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()


    def layout(self):
        self.view = pg.GraphicsView()
        l = pg.GraphicsLayout(border=(100,100,100))
        self.view.setCentralItem(l)
        self.view.show()
        self.view.setWindowTitle('PyRover v0.1')

        self.p1 = l.addPlot(title="temp/humid")
        self.p1.showGrid(x=True, y=True)
        vb = l.addViewBox(lockAspect=True, colspan=2, rowspan=2)
        self.img_display = pg.ImageItem(np.random.uniform(size=(640,480,3)))
        vb.addItem(self.img_display)
        vb.autoRange()
        self.p2 = l.addPlot(title="radio")

        l.nextRow()

        self.p3 = l.addPlot(title="gas")
        self.p3.showGrid(x=True, y=True)
        l2 = l.addLayout()
        vb = pg.ViewBox()
        self.t = pg.TextItem()
        vb.addItem(self.t)
        l2.addItem(vb)


    def update_plot_data(self):
        try:
            if self.temp is not None:
                self.p1.clear()
                self.p1.plot(list(self.temp))

            if self.img is not None:
                self.update_img(list(self.img))

        except BrokenPipeError as e:
            print(e)
            self.timer.stop()

    def update_img(self, img, boxes=None, classes=None):
        if type(img) == list:
            img = np.array(img)
        img = np.rot90(img, k=3)
        self.img_display.setImage(img)

def GUI(temp, img=None):
    app = QtWidgets.QApplication([])
    window = MainWindow(temp=temp, img=img)
    sys.exit(app.exec_())

def start():
    manager = Manager()
    temp = manager.list(np.zeros(100))
    img = manager.list(list(np.random.uniform(size=(640,480,3))))
    p = Process(target=GUI, args=(temp, img))
    p.start()
    return temp, img


if __name__ == '__main__':
    start()