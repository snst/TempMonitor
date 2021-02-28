import sys, os, random
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import serial
import time
from time import sleep
import threading
from random import uniform
import matplotlib.animation as animation
import yaml

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from data_collector import *
from smooth import *
from median_filter import *

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.emu = True
        self.emu = False

        self.min_x = 0
        self.max_x = 60
        self.step_x = 2
        self.min_y = 50
        self.max_y = 110
        self.step_y = 2
        self.dc = DataCollector()
        self.smooth = Smooth(3)
        self.median = MedianFilter()
        self.ser = None
        self.serial_thread = None
        self.xs = [0]
        self.ys = [0]
        self.ys2 = [0]
        self.ys3 = [0]
        self.cur_temp = 0
        self.marker = []
        self.last_y = 0
        self.water_start_ms = 0
        self.water_end_ms = 0
        self.water_duration_ms = 0
        self.temp_smooth = 0
        self.cfg_file = os.path.dirname(sys.argv[0]) + "/" + "temp.yaml"

        self.setWindowTitle('Temperature Monitor')

        self.temp_text = QLabel("-")
        self.water_duration_text = QLabel("-")

        self.create_main_frame()
        #self.create_status_bar()
        self.textbox_name.setText('FirstShot')
        self.load_settings()

    def load_settings(self):
        with open(self.cfg_file) as file:
            data = yaml.load(file)
            self.textbox_serial.setText(data['serial'])
            self.textbox_path.setText(data['path'])

    def save_settings(self):
        a = self.textbox_serial.text()
        with open(self.cfg_file, 'w') as file:
            data = {'serial':self.textbox_serial.text(), 'path':self.textbox_path.text()}
            yaml.dump(data, file)

    def on_save(self):
        path = self.textbox_path.text() + "/" + self.textbox_name.text()  
        if not path.endswith(".png"):
            path += ".png"
        print(path)
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)


    def serial_thread_func(self, name):
        c = 50
        s = 120
        while self.ser:
            try:
                if not self.emu:
                    s = self.ser.readline()
                else:
                    sleep(0.02)
                    #s = uniform(120, 200)
                    s += 0.1

                x = int(s)
                #c = -(v-2143) / 9.31
                #c = 115 - 0.145 * x + 0.000144 * x * x -0.0000000645 * x * x * x
                c = 116 - 0.162*x +2.08/10000*x*x - 1.57/10000000*x*x*x + 4.58/100000000000*x*x*x*x
                self.temp_smooth = self.smooth.add(c)
                self.median.add(c)
                self.dc.add(c)
                #print("%d\t%.1f" % (x,c))
            except:
                pass

    def on_connect(self):
        if self.connect_cb.isChecked():
            if self.emu:
                self.ser = True
            else:
                self.ser = serial.Serial(self.textbox_serial.text(), 115200)
            self.serial_thread = threading.Thread(target=self.serial_thread_func, args=(1,))
            self.serial_thread.start()
        else:
            self.ser_close()

    def ser_close(self):
        if self.ser:
            if self.emu:
                self.ser = False
            else:
                self.ser.close()
                self.ser = None

    def on_clear(self):
        self.dc.reset()
        self.xs.clear()
        self.ys.clear()
        self.ys2.clear()
        self.ys3.clear()
        self.marker = []
        self.smooth.reset()

    
    def create_main_frame(self):
        self.main_frame = QWidget()
        self.dpi = 100
        self.fig = Figure((10.0, 10.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_ylim(self.min_y, self.max_y)
        self.axes.set_xlim(self.min_x, self.max_x)
        self.axes.set_xticks(range(self.min_x, self.max_x, self.step_x))
        self.axes.set_yticks(range(self.min_y, self.max_y, self.step_y))
        self.axes.grid(True)

        self.line, = self.axes.plot(self.xs, self.ys)
        self.line2, = self.axes.plot(self.xs, self.ys2)
        self.line3, = self.axes.plot(self.xs, self.ys3)

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        self.textbox_name = QLineEdit()
        self.textbox_name.setMinimumWidth(200)

        self.textbox_path = QLineEdit()
        self.textbox_path.setMinimumWidth(200)

        self.folder_button = QPushButton("...")
        self.folder_button.clicked.connect( self.on_folder)

        self.textbox_serial = QLineEdit()
        self.textbox_serial.setMinimumWidth(200)

        self.m1_button = QPushButton("Start")
        self.m1_button.clicked.connect( lambda: self.on_mark("green"))
        self.m2_button = QPushButton("Pump On")
        self.m2_button.clicked.connect( lambda: self.on_mark("yellow"))
        self.m3_button = QPushButton("Pump Off")
        self.m3_button.clicked.connect( lambda: self.on_mark("orange"))
        self.m4_button = QPushButton("Water Start")
        self.m4_button.clicked.connect( self.water_start)
        self.m5_button = QPushButton("Water Stop")
        self.m5_button.clicked.connect( self.water_stop)

        self.save_button = QPushButton("&Save")
        self.save_button.clicked.connect(self.on_save)

        self.clear_button = QPushButton("&Clear")
        self.clear_button.clicked.connect(self.on_clear)

        self.connect_cb = QCheckBox("Connect")
        self.connect_cb.setChecked(False)
        self.connect_cb.stateChanged.connect(self.on_connect)

        hbox = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        
        for w in [  QLabel("Path"), self.textbox_path, self.folder_button, QLabel("Filename"), self.textbox_name, self.save_button
         ,self.clear_button, ]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        

        for w in [ self.temp_text, self.water_duration_text ]:
            hbox3.addWidget(w)

        for w in [ QLabel("Serial"), self.textbox_serial, self.connect_cb, self.m1_button,
        self.m2_button,self.m3_button,self.m4_button,self.m5_button  ]:
            hbox2.addWidget(w)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def on_folder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if len(file):
            self.textbox_path.setText(file)
    

    def water_start(self):
        self.water_start_ms = self.dc.now()
        self.on_mark("blue")

    def water_stop(self):
        self.water_stop_ms = self.dc.now()
        self.on_mark("red")
        self.water_duration_ms = self.water_stop_ms - self.water_start_ms
        self.water_duration_text.setText("Water duration: %.1f" % (self.water_duration_ms/1000) )


    def create_status_bar(self):
        self.status_text = QLabel("-")
        self.statusBar().addWidget(self.status_text, 1)
        
    def on_mark(self, col):
        self.marker.append((self.dc.now()/1000,self.last_y, col))

    def animate(self, i, xs, ys):
        r = [self.line, 
            self.line2, 
            self.line3
        ]
        
        for m in self.marker:
            r.append(self.axes.scatter(m[0], m[1], c=m[2]))

        val = self.dc.get()
        if val:
            median_temp = self.median.get()
            self.last_y = val[1]
            self.ys.append(val[1])
            self.xs.append(val[0] / 1000)
            self.line.set_ydata(self.ys)
            self.line.set_xdata(self.xs)

            self.ys2.append(self.temp_smooth)
            self.line2.set_ydata(self.ys2)
            self.line2.set_xdata(self.xs)

            self.ys3.append(median_temp)
            self.line3.set_ydata(self.ys3)
            self.line3.set_xdata(self.xs)

            self.temp_text.setText("Temp: %.1f / %.1f / %.1f" % (val[1], self.temp_smooth, median_temp))

        return r
        

    def anim(self):
        self.ani = animation.FuncAnimation(self.fig,
        self.animate,
        fargs=(self.xs, self.ys),
        interval=100,
        blit=True)

def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    form.anim()

    app.exec_()
    form.save_settings()
    form.ser_close()
    pass


if __name__ == "__main__":
    main()