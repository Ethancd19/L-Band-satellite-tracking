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
from functools import partial

        
class Window(QMainWindow):
    """Main Window."""
    def __init__(self, *args, **kwargs):
        """Initializer."""
        super(Window, self).__init__(*args, **kwargs)
        self.setWindowTitle("L-Band Satellite Tracking and Characterization Interface")
        self.resize(1500,500)
        self.setAcceptDrops(True)
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
    def dragEnterEvent(self, event: QDragEnterEvent):
        # Check if the drag-and-drop operation contains a text file named 'tle.txt'
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.fileName() == 'tle.txt':
                    event.accept()
                    return

        event.ignore()

    def dropEvent(self, event: QDropEvent):
        # Check if the dropped file is a text file named 'tle.txt'
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.fileName() == 'tle.txt':
                filepath = url.toLocalFile()
                with open(filepath, 'r') as f:
                    file_content = f.read()
                msgBox = QMessageBox()
                msgBox.setText("Would you like to add this file to the queue or replace the queue?")
                msgBox.setWindowTitle("Options")
                msgBox.addButton("Add to queue", QMessageBox.YesRole)
                msgBox.addButton("Replace queue", QMessageBox.NoRole)
                msgBox.addButton("Cancel", QMessageBox.RejectRole)
                choice = msgBox.exec()
                if choice == QMessageBox.YesRole:
                    # Add the file content to the QPlainTextEdit without replacing the text
                    self.queue.insertPlainText(file_content)
                elif choice == QMessageBox.NoRole:
                    # Replace the content of the QPlainTextEdit with the file content
                    self.queue.clear()
                    self.queue.insertPlainText(file_content)

                event.accept()
                return

        event.ignore()


    # def dragEnterEvent(self, event):
    #     if event.mimeData().hasUrls():
    #         event.accept()
    #     else:
    #         event.ignore()
    # def dropEvent(self, event):
    #     if event.mimeData().hasUrls():
    #         event.accept()

    #         # get the list of file URLs
    #         urls = event.mimeData().urls()

    #         # create a pop-up dialog with options
    #         dialog = QDialog(self)
    #         dialog.setWindowTitle("Options")
    #         message = QLabel("Would you like to add this file to the queue or replace the queue?")
    #         add_button = QPushButton("Add to queue")
    #         replace_button = QPushButton("Replace queue")
    #         cancel_button = QPushButton("Cancel")
    #         add_button.setProperty('urls', urls)
    #         replace_button.setProperty('urls', urls)
    #         button_layout = QHBoxLayout()
    #         button_layout.addWidget(add_button)
    #         button_layout.addWidget(replace_button)
    #         button_layout.addWidget(cancel_button)
    #         main_layout = QVBoxLayout()
    #         main_layout.addWidget(message)
    #         main_layout.addLayout(button_layout)
    #         dialog.setLayout(main_layout)

    #         # connect the buttons to their respective functions
    #         print(type(add_button))  # should output <class 'PyQt5.QtWidgets.QPushButton'>
    #         add_button.clicked.connect(self.addToQueue)
    #         replace_button.clicked.connect(self.replaceQueue)
    #         cancel_button.clicked.connect(dialog.close)

    #         # show the pop-up dialog
    #         dialog.exec_()
    #     else:
    #         event.ignore()

    # def addToQueue(self):
    #     urls = self.sender().property('urls')
    #     for url in urls:
    #         file_path = url.toLocalFile()
    #         with open(file_path, 'r') as f:
    #             tle = f.read()
    #             self.queue.appendPlainText(tle)

    # def addToQueue(self,urls):
    #     for url in urls:
    #         file_path=url.toLocalFile()
    #         with open(file_path, 'r') as f:
    #             tle = f.read()
    #             self.queue.appendPlainText(tle)
    # def addToQueue(self, urls):
    #     for url in urls:
    #         url = QUrl(url.toLocalFile())
    #         # add the file to the queue

    def replaceQueue(self, urls):
        # clear the current queue
        for url in urls:
            url = QUrl(url.toLocalFile())
            # add the file to the queue

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
        self.spectrumSelect.activated.connect(self.plotAvgSpectrum)
    

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
        
    def plotAvgSpectrum(self):
        dt = 0.01
        t = np.arange(0, 30, dt)
        nse1 = np.random.randn(len(t))
        r = np.exp(-t / 0.05)

        cnse1 = np.convolve(nse1, r, mode ='same')*dt

        s1 = np.cos(np.pi * t) + cnse1 + np.sin(2 * np.pi * 10 * t)

        # create the spectrum plot using matplotlib's psd function
        ax = self.figure.add_subplot(111)
        ax.psd(s1, 2**14, dt)
        ax.set_ylabel('PSD(db)')
        ax.set_xlabel('Frequency')
        ax.set_title('matplotlib.pyplot.psd() Example\n', fontsize = 14, fontweight ='bold')

        # refresh the canvas to display the plot
        self.canvas.draw()
    
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

