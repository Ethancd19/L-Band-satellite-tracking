from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
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
import pickle
import io
import folium


        
class Window(QMainWindow):
    """Main Window."""
    def __init__(self, *args, **kwargs):
        """Initializer."""
        super(Window, self).__init__(*args, **kwargs)

        #Initializes the window that the layouts defined below are going to be placed in. Giving things such as the window size
        #And other characteristics such as wether or not it accepts drag and drop files
        self.setWindowTitle("L-Band Satellite Tracking and Characterization Interface")
        self.resize(2000,800)
        self.setAcceptDrops(True)
        self._createActions()
        self._createMenuBar()
        self.timer = QTimer(self)
        self.elapsed_time = 0
        widget = QWidget()

        layout = QVBoxLayout()
        
        
        #creating the tabs that will be used in the GUI that will allow us to switch between the 
        #characterization tab and the command tab
        self.tabs = QTabWidget()
        self.tabs.addTab(self.calibrationTabUI(), "Calibration")
        self.tabs.addTab(self.characterizationTabUI(), "Characterization")
        self.tabs.addTab(self.commandTabUI(), "Command Center")
        layout.addWidget(self.tabs)
        self.tabs.currentChanged.connect(self._tabChanged)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def dragEnterEvent(self, event: QDragEnterEvent):
        #Function that allows the user to drag and drop a file into the queue instead of manually adding it or
        #having to search for the file using the file browser
        # Check if the drag-and-drop operation contains a text file named 'tle.txt'
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.fileName() == 'tle.txt':
                    event.accept()
                    return
        #if after checking the file, it is not a text file named 'tle.txt', then ignore the event
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
    def calibrationTabUI(self):
        calibrationTab = QWidget()
        mainLayout = QHBoxLayout()

        coordinate = (37.229572, -80.413940)
        m = folium.Map(
            title="Location",
            zoom_start=18,
            location=coordinate
        )
        folium.Marker(coordinate, popup="Virginia Tech").add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)

        # Map (QWebEngineView) Configuration
        webView = QWebEngineView()
        webView.setHtml(data.getvalue().decode())
        webView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Set size policy for webView
        mainLayout.addWidget(webView, 2)  # give more stretch to the map

        # Info Panel Configuration
        infoLayout = QVBoxLayout()

        coordsLabel = QLabel(f"Coordinates: {coordinate}")
        infoLayout.addWidget(coordsLabel)
        headingLabel = QLabel("Heading: 0")
        infoLayout.addWidget(headingLabel)

        # Center Frequency
        centerFreqLabel = QLabel("Center Frequency:")
        self.centerFreqLineEdit = QLineEdit()  # Create a line edit for center frequency
        infoLayout.addWidget(centerFreqLabel)
        infoLayout.addWidget(self.centerFreqLineEdit)

        
        # Sample Rate
        sampleRateLabel = QLabel("Sample Rate:")
        self.sampleRateLineEdit = QLineEdit()  # Create a line edit for sample rate
        infoLayout.addWidget(sampleRateLabel)
        infoLayout.addWidget(self.sampleRateLineEdit)

        # Test1
        test1Label = QLabel("Test1:")
        self.test1LineEdit = QLineEdit()  # Create a line edit for test1
        infoLayout.addWidget(test1Label)
        infoLayout.addWidget(self.test1LineEdit)

        # Test2
        test2Label = QLabel("Test2:")
        self.test2LineEdit = QLineEdit()  # Create a line edit for test2
        infoLayout.addWidget(test2Label)
        infoLayout.addWidget(self.test2LineEdit)

        
        self.progressBar = QProgressBar()
        self.progressBar.setMaximum(60)
        self.calibrationButton = QPushButton("Start Calibration")

        self.calibrationTimer = QTimer()
        self.calibrationTimer.timeout.connect(self.updateProgressBar)
        self.calibrationButton.clicked.connect(self.toggleCalibration)
        infoLayout.addWidget(self.progressBar)
        infoLayout.addWidget(self.calibrationButton)

        infoLayoutWidget = QWidget()  # wrap the infoLayout in a widget
        infoLayoutWidget.setLayout(infoLayout)
        infoLayoutWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)  # Set size policy for info panel

        mainLayout.addWidget(infoLayoutWidget, 2)  # give less stretch to the info panel

        calibrationTab.setLayout(mainLayout)
        return calibrationTab

    
    def toggleCalibration(self):
        if self.calibrationButton.text() == "Start Calibration":
            self.progressBar.setValue(0)
            self.calibrationTimer.start(1000)
            self.calibrationButton.setText("Stop Calibration")
        else:
            self.calibrationTimer.stop()
            self.calibrationButton.setText("Start Calibration")
    def updateProgressBar(self):
        value = self.progressBar.value()
        if value < 60:
            self.progressBar.setValue(value + 1)
        else:
            self.calibrationTimer.stop()
            self.calibrationButton.setText("Start Calibration")
    def characterizationTabUI(self):
        characterizationTab = QWidget()

        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        tleinputlayout = QHBoxLayout()
        layout3 = QVBoxLayout()
        layout4 = QHBoxLayout()
        trackSatelliteLayout = QVBoxLayout()

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
        self.hostClientSelect = QComboBox()
        self.hostClientSelect.addItems(["Select Device","Host","Client"])
        self.selectTrace = QComboBox()
        self.selectTrace.addItems(["Select Trace","Trace 1","Trace 2","Trace 3","Trace 4","Trace 5"])
        self.download = QPushButton("Download",self)
        self.delete = QPushButton("Delete",self)
        self.plot= QPushButton("Plot",self)
        # self.downloadOption = QComboBox()
        # self.downloadOption.addItems(["Select Trace","Trace 1","Trace 2","Trace 3","Trace 4","Trace 5"])
        # self.deleteOption = QComboBox()
        # self.deleteOption.addItems(["Select Trace","Trace 1","Trace 2","Trace 3","Trace 4","Trace 5"])
        self.track_satellite = QWidget()
        self.queueLabel = QLabel("TLE Queue:",self)
        
        self.queue = QPlainTextEdit(self)
        self.queue.setReadOnly(True)
        self.fixed_az_el_widget = QWidget()
        self.fixed_az_el_layout = QFormLayout()
        self.azimuth_edit = QLineEdit()
        self.elevation_edit = QLineEdit()
        self.length_of_recording_edit = QLineEdit()
        self.point_button = QPushButton("Point")
        self.start_recording_button = QPushButton("Start Recording")

        self.graphing_settings_widget = QWidget()
        self.graphing_settings_layout = QFormLayout()
        self.center_frequency = QLineEdit()
        self.test_line_edit = QLineEdit()
        self.test_line_edit_2 = QLineEdit()
        self.update_graph_button = QPushButton("Update Graph")
           
        #developing the layout of the characterization tab, making it more user friendly and understandable
        layout2.addWidget(self.spectrumSelect)
        layout2.addWidget(self.canvas)
        tleinputlayout.addWidget(self.textbox)
        tleinputlayout.addWidget(self.addToQueue)
        layout2.addLayout(tleinputlayout)
        layout2.addWidget(self.satelliteProgress)
        layout1.addLayout(layout2)
        layout3.addWidget(self.power)
        layout3.addWidget(self.tracking)
        layout3.addWidget(self.hostClientSelect)
        layout3.addWidget(self.selectTrace)
        layout4.addWidget(self.download)
        layout4.addWidget(self.delete)
        layout4.addWidget(self.plot)
        layout3.addLayout(layout4)
        # layout5.addWidget(self.downloadOption)
        # layout5.addWidget(self.deleteOption)
        # layout3.addLayout(layout5)

        #setting what each of thre subsections of the layout is doing
        self.tab_widget = QTabWidget()
        trackSatelliteLayout.addWidget(self.queueLabel)
        trackSatelliteLayout.addWidget(self.queue)
        self.track_satellite.setLayout(trackSatelliteLayout)
        self.tab_widget.addTab(self.track_satellite,"Track Satellites")
        self.fixed_az_el_layout.addRow("Enter Azimuth:",self.azimuth_edit)
        self.fixed_az_el_layout.addRow("Enter Elevation:",self.elevation_edit)
        self.fixed_az_el_layout.addRow("Length of Recording:",self.length_of_recording_edit)
        self.fixed_az_el_layout.addRow(self.point_button, self.start_recording_button)
        self.start_recording_button.clicked.connect(self.start_timer)
        
        self.timer_label = QLabel("Time Elapsed: 0 s")
        self.fixed_az_el_layout.addRow(self.timer_label)

        self.fixed_az_el_widget.setLayout(self.fixed_az_el_layout)
        self.tab_widget.addTab(self.fixed_az_el_widget, "Fixed AZ-EL")

        self.graphing_settings_layout.addRow("Center Frequency:", self.center_frequency)
        self.graphing_settings_layout.addRow("Test Line Edit:", self.test_line_edit)
        self.graphing_settings_layout.addRow("Test Line Edit 2:", self.test_line_edit_2)
        self.graphing_settings_layout.addRow(self.update_graph_button)
        self.graphing_settings_widget.setLayout(self.graphing_settings_layout)

        self.tab_widget.addTab(self.graphing_settings_widget, "Graphing Settings")

        layout3.addWidget(self.tab_widget)
        
        layout1.addLayout(layout3)
        self.setCentralWidget(characterizationTab)

        
        
        characterizationTab.setLayout(layout1)
        
        return characterizationTab
    def start_timer(self):
        self.elapsed_time = 0
        self.timer.start(1000)
        self.timer.timeout.connect(self.update_timer)
    def update_timer(self):
        self.elapsed_time += 1
        self.timer_label.setText(f"Time Elapsed: {self.elapsed_time} s")

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

    def _tabChanged(self, index):
        #if moving away from Calibration tab
        if index != 0:
            msg = QMessageBox(self)
            msg.setWindowTitle("Calibration Check")
            msg.setText("Have you completed the calibration?")
            yes_button = msg.addButton("Yes", QMessageBox.YesRole)
            no_button = msg.addButton("No", QMessageBox.NoRole)
            just_looking_button = msg.addButton("Just looking", QMessageBox.NoRole)

            msg.exec_()

            clicked_button = msg.clickedButton()

            if clicked_button == no_button:
                # prevent the user from moving to the next tab
                self.tabs.setCurrentIndex(0)
            elif clicked_button == just_looking_button:
                warning_msg = QMessageBox.warning(self,
                                                  "Warning",
                                                  "Proceeding without calibration will result in errors in readings.",
                                                  QMessageBox.Ok | QMessageBox.Cancel)
                if warning_msg == QMessageBox.Cancel:
                    self.tabs.setCurrentIndex(0)

    def tle_file_open(self):
        name = QFileDialog.getOpenFileName(self, 'Open File')
        
        if name[0]:
            f = open(name[0],'r')
            with f:
                lines = f.readlines()

            # remove first line
            lines.pop(0)

            # remove every third line
            lines = [line for index, line in enumerate(lines) if (index + 1) % 3 != 0]

            # join remaining lines into a single string
            text = "".join(lines)
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
        # dt = 0.01
        # t = np.arange(0, 30, dt)
        # nse1 = np.random.randn(len(t))
        # r = np.exp(-t / 0.05)

        # cnse1 = np.convolve(nse1, r, mode ='same')*dt

        # s1 = np.cos(np.pi * t) + cnse1 + np.sin(2 * np.pi * 10 * t)
        with open(r"C:\Users\Ethan\Documents\MDE\L-Band-satellite-tracking\Gui\test_data.dat", 'rb') as f:
            data_dict = pickle.load(f)

        raw_iq_data = data_dict['raw_iq_data']
        center_frequency = data_dict['center_frequency']
        sample_rate = data_dict['sample_rate']

        # Compute the FFT and normalize
        iq_fft = np.fft.fftshift(np.fft.fft(raw_iq_data))
        iq_fft_norm = np.abs(iq_fft) / np.max(np.abs(iq_fft))

        # Compute the frequency axis
        freqs = np.fft.fftshift(np.fft.fftfreq(len(raw_iq_data), 1 / sample_rate)) + center_frequency

        # Compute the time axis
        time_steps = np.arange(len(raw_iq_data)) / sample_rate

        # Reshape the FFT data into chunks of 100 samples (adjust as needed)
        fft_chunk_size = 100
        num_chunks = len(raw_iq_data) // fft_chunk_size
        fft_data = iq_fft_norm[:num_chunks*fft_chunk_size].reshape(num_chunks, fft_chunk_size)
        time_data = time_steps[:num_chunks*fft_chunk_size].reshape(num_chunks, fft_chunk_size)

        # Compute the average spectrum vs time
        avg_spectrum = np.mean(fft_data, axis=1)
        avg_time = np.mean(time_data, axis=1)

        # Plot the average spectrum vs time
        ax = self.figure.add_subplot(111)
        ax.plot(avg_time, avg_spectrum)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Average Spectrum')
        ax.set_title('Average Spectrum vs Time')
        # ax = self.figure.add_subplot(111)
        # ax.psd(raw_iq_data, NFFT=1024, Fs=sample_rate, window=np.hamming(1024))
        # ax.set_xlabel('Frequency (Hz)')
        # ax.set_ylabel('PSD (dB/Hz)')
        # ax.set_title('Power Spectral Density')

        # create the spectrum plot using matplotlib's psd function
        
        # ax.psd(s1, 2**14, dt)
        # ax.set_ylabel('Power(db)')
        # ax.set_xlabel('Frequency (Hz)')
        # ax.set_title('Average Spectrum VS. Time\n', fontsize = 14, fontweight ='bold')

        # refresh the canvas to display the plot
        self.canvas.draw()
    
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

