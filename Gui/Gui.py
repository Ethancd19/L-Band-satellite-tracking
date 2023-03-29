from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import qrc_resources
from pyqtgraph import *
from pylab import *
import numpy as np
import pyqtgraph as pg
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import os
import matplotlib.pyplot as plt
import random

        
class Window(QMainWindow):
    """Main Window."""
    def __init__(self, *args, **kwargs):
        """Initializer."""
        super(Window, self).__init__(*args, **kwargs)
        self.setWindowTitle("L-Band Satellite Tracking and Characterization Interface")
        self.resize(1500,500)
        self.setAcceptDrops(True)
        self.signal_setup()
        self._createActions()
        self._createMenuBar()
        widget = QWidget()

        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        tabs.addTab(self.characterizationTabUI(), "Characterization")
        tabs.addTab(self.commandTabUI(), "Command Center")
        layout.addWidget(tabs)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            if f.endswith('tle.txt'):
                file = open(f,'r')
                with file:
                    text = file.read()
                    self.queue.setPlainText(text) 


    def characterizationTabUI(self):
        characterizationTab = QWidget()

        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        tleinputlayout = QHBoxLayout()
        layout3 = QVBoxLayout()
        layout4 = QHBoxLayout()
        layout5 = QHBoxLayout()

        self.spectrumSelect = QComboBox()
        self.spectrumSelect.addItems(["Select Spectrum", "Average Frequency vs. Time",
                                       "Signal Strength vs. Time"])
        
        
        self.figure = plt.Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.spectrumSelect.activated.connect(self.plotSpectrum)
    

        self.textbox = QLineEdit(self)
        self.textbox.setPlaceholderText("Insert TLE here")
        self.textbox.setDragEnabled(True)
        self.addToQueue = QPushButton("Add to queue", self)
        self.addToQueue.clicked.connect(self.on_addToQueue_clicked)
        self.addToQueue.setAutoDefault(True)
        self.textbox.returnPressed.connect(self.addToQueue.click)

        self.satelliteProgress = QProgressBar(self)
        self.power = QPushButton("power",self)
        self.tracking = QCheckBox("Tracking?",self)
        self.download = QLabel("Download:",self)
        self.delete = QLabel("Delete:",self)
        self.downloadOption = QComboBox()
        self.downloadOption.addItems(["Select Trace","Trace 1","Trace 2","Trace 3","Trace 4","Trace 5"])
        self.deleteOption = QComboBox()
        self.deleteOption.addItems(["Select Trace","Trace 1","Trace 2","Trace 3","Trace 4","Trace 5"])
        self.queueLabel = QLabel("TLE Queue:",self)
        
        self.queue = QPlainTextEdit(self)
        self.queue.setReadOnly(True)   


 


        layout2.addWidget(self.spectrumSelect)
        layout2.addWidget(self.canvas)
        tleinputlayout.addWidget(self.textbox)
        tleinputlayout.addWidget(self.addToQueue)
        layout2.addLayout(tleinputlayout)
        layout2.addWidget(self.satelliteProgress)
        layout1.addLayout(layout2)
        layout3.addWidget(self.power)
        layout3.addWidget(self.tracking)
        layout4.addWidget(self.download)
        layout4.addWidget(self.delete)
        layout3.addLayout(layout4)
        layout5.addWidget(self.downloadOption)
        layout5.addWidget(self.deleteOption)
        layout3.addLayout(layout5)
        layout3.addWidget(self.queueLabel)
        layout3.addWidget(self.queue)
        layout1.addLayout(layout3)
        self.setCentralWidget(characterizationTab)

        
        
        characterizationTab.setLayout(layout1)
        
        return characterizationTab

    def commandTabUI(self):
        commandTab = QWidget()
        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        bottomLayout = QHBoxLayout()
        self.commandLabel = QLabel("Commands:",self)
        self.resultsLabel = QLabel("Results:",self)
        self.commands = QPlainTextEdit(self)
        self.results = QPlainTextEdit(self)
        topLayout.addWidget(self.commandLabel)
        topLayout.addWidget(self.resultsLabel)
        bottomLayout.addWidget(self.commands)
        bottomLayout.addWidget(self.results)
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(bottomLayout)
        commandTab.setLayout(mainLayout)
        return commandTab 

    def tle_file_open(self):
        name = QFileDialog.getOpenFileName(self, 'Open File')
        
        if name[0]:
            f = open(name[0],'r')
            with f:
                text = f.read()
                self.queue.setPlainText(text)

    def IQ_file_open(self):
        name = QFileDialog.getOpenFileName(self, 'Open File')
        
        if name[0]:
            f = open(name[0],'r')
            with f:
                text = f.read()
                self.results.setPlainText(text)       

    def _createMenuBar(self):
        menuBar = self.menuBar()

        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)

        #open menu
        openSubMenu = QMenu("&Open", self)
        fileMenu.addMenu(openSubMenu)
        openSubMenu.addAction(self.openTLE)
        openSubMenu.addAction(self.openIQ)

        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)

        helpMenu = menuBar.addMenu(QIcon(":help.png"), "&Help")
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)

    def _createActions(self):
        self.newAction = QAction("&New", self)

        self.openAction = QAction("&Open", self)
        self.openAction.setStatusTip('Open File')

        self.openTLE=QAction("&Open TLE", self)
        self.openTLE.triggered.connect(self.tle_file_open)

        self.openIQ=QAction("&Open IQ", self)
        self.openIQ.triggered.connect(self.IQ_file_open)   

        self.saveAction = QAction("&Save", self)
        
        self.exitAction = QAction("&Exit", self)

        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)
    
    def on_addToQueue_clicked(self):
        tle=self.textbox.text()
        # updated_tle = tle +'\n'
        self.queue.insertPlainText(tle + '\n')
        self.textbox.clear()
    
    def plotSpectrum(self):
        samples = [-0.36470588+0.78039216j, -0.09803922+0.09235294j, 0.14509804+0.01176471j, -0.14509904-0.18431373j, -0.16078431+0.05882353j, -0.1372549+0.39607843j, -0.1372549 +0.5372549j,  -0.4745098 +0.05098039j, 0.01176471+0.30196078j]
        data = plt.psd(samples, Fs=2.048, Fc=0)
        ax = self.figure.add_subplot(111)
        ax.plot(data, '*-')
        ax.set_title('Average Spectrum vs. time')
        self.canvas.draw()
        
    def signal_setup(self):
        np.random.seed(0)
        dt = 0.01
        Fs = 1/dt
        t = np.arange(0, 10, dt)
        nse = np.random.randn(len(t))
        r = np.exp(-t/0.05)
        cnse = np.convolve(nse, r)*dt
        cnse = cnse[:len(t)]

        s = 0.1*np.sin(2*np.pi*10*t) + cnse

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

