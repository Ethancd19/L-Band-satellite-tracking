from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import qrc_resources
from pyqtgraph import *
import numpy as np
import pyqtgraph as pg
import os

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, *args, **kwargs):
        """Initializer."""
        super(Window, self).__init__(*args, **kwargs)
        self.setWindowTitle("L-Band Satellite Tracking and Characterization Interface")
        self.resize(1500,500)

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
        
        self.graphWidget = pg.PlotWidget()
        
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
        layout2.addWidget(self.graphWidget)
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
        time = [0, 1, 2, 3, 4, 5, 6]
        averaged_frequency = [1400, 1450, 1500, 1550, 1600, 1650, 1700]
        self.graphWidget.plot(time, averaged_frequency)
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

    def file_open(self):
        name = QFileDialog.getOpenFileName(self, 'Open File')
        
        if name[0]:
            f = open(name[0],'r')
            with f:
                text = f.read()
                self.queue.setPlainText(text)

    def _createMenuBar(self):
        menuBar = self.menuBar()

        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)

        helpMenu = menuBar.addMenu(QIcon(":help.png"), "&Help")
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)

    def _createActions(self):
        self.newAction = QAction("&New", self)

        self.openAction = QAction("&Open", self)
        self.openAction.setShortcut("Ctrl+o")
        self.openAction.setStatusTip('Open File')
        self.openAction.triggered.connect(self.file_open)

        self.saveAction = QAction("&Save", self)
        
        self.exitAction = QAction("&Exit", self)

        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)
    
    def on_addToQueue_clicked(self):
        tle=self.textbox.text()
        # updated_tle = tle +'\n'
        self.queue.insertPlainText(tle + '\n')
        self.textbox.clear()
       



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())