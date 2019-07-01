import sys
from PyQt4 import QtCore, QtGui
from frame import ApexVod

import logging


class QPlainTextEditLogger(logging.Handler):
    """ Logging module """
    def __init__(self, parent):
        super().__init__()
        self.widget = QtGui.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class WorkThread(QtCore.QThread):
    """ Thread for video proccessing """
    def __init__(self, input_val, output_val, frame_skip_val, merge_val, kill_only_val, buffer_val, range_val, radio_val):

        QtCore.QThread.__init__(self)
        self.input_val = input_val
        self.output_val = output_val
        self.frame_skip_val = frame_skip_val
        self.merge_val = merge_val
        self.kill_only_val = kill_only_val
        self.buffer_val = buffer_val
        self.range_val = range_val
        self.radio_val = radio_val

    def __del__(self):

        self.exiting = True
        # quits the thread once finished running, emits finished() signal 
        self.wait()

    # def onfinish(self):
    #     self.finish()

    def run(self):
        apexvod = ApexVod()
        apexvod.main_vod(apexvod.ref, apexvod.frame_data, apexvod.frame_count, apexvod.health_bar_coord,
                         self.input_val, self.output_val, self.kill_only_val, self.merge_val,
                         self.frame_skip_val, self.range_val, self.buffer_val,
                         apexvod.debug, self.radio_val)
        # self.quit()


class ApexGui(QtGui.QWidget, QPlainTextEditLogger):
    """ Gui  """
    def __init__(self):
        super(ApexGui, self).__init__()

        self.initUI()

    def initUI(self):

        self.resize(642, 254)
        self.center()
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        # input and output file browsers
        self.input = QtGui.QLabel('Input')
        self.output = QtGui.QLabel('Output')

        self.input_edit = QtGui.QLineEdit()
        self.input_edit.setMinimumSize(QtCore.QSize(450, 20))
        self.output_edit = QtGui.QLineEdit()
        self.output_edit.setMinimumSize(QtCore.QSize(450, 20))

        self.input_btn = QtGui.QPushButton('Browse', self)
        self.output_btn = QtGui.QPushButton('Browse', self)
        self.input_btn.clicked.connect(self.selectFileInput)
        self.output_btn.clicked.connect(self.selectFileOutput)

        self.grid.addWidget(self.input, 1, 0)
        self.grid.addWidget(self.input_edit, 1, 1)
        self.grid.addWidget(self.input_btn, 1, 2)

        self.grid.addWidget(self.output, 2, 0)
        self.grid.addWidget(self.output_edit, 2, 1)
        self.grid.addWidget(self.output_btn, 2, 2)

        # check boxes
        self.frame_skip_cb = QtGui.QCheckBox('Frame Skip', self)
        self.merge_cb = QtGui.QCheckBox('Merge', self)
        self.kill_only_cb = QtGui.QCheckBox('Kill only', self)
        self.grid.addWidget(self.frame_skip_cb, 3, 0)
        self.grid.addWidget(self.merge_cb, 6, 0)
        self.grid.addWidget(self.kill_only_cb, 6, 1)

        # spin boxes
        self.spinBox_frame_skip = QtGui.QSpinBox(self)
        self.spinBox_buffer = QtGui.QSpinBox(self)
        self.spinBox_range = QtGui.QSpinBox(self)

        self.spinBox_frame_skip.setProperty("value", 1)
        self.spinBox_frame_skip.setMaximum(3)
        self.spinBox_frame_skip.setMinimum(1)
        self.spinBox_frame_skip.setMaximumSize(QtCore.QSize(35, 20))
        self.spinBox_buffer.setProperty("value", 3)
        self.spinBox_buffer.setMaximum(10)
        self.spinBox_buffer.setMinimum(1)
        self.spinBox_buffer.setMaximumSize(QtCore.QSize(35, 20))
        self.spinBox_range.setProperty("value", 20)
        self.spinBox_range.setMaximum(50)
        self.spinBox_range.setMinimum(1)
        self.spinBox_range.setMaximumSize(QtCore.QSize(35, 20))

        self.grid.addWidget(self.spinBox_frame_skip, 3, 1)
        self.grid.addWidget(self.spinBox_buffer, 4, 1)
        self.grid.addWidget(self.spinBox_range, 5, 1)

        self.buffer_label = QtGui.QLabel('Buffer')
        self.range_label = QtGui.QLabel('Range')
        self.grid.addWidget(self.buffer_label, 4, 0)
        self.grid.addWidget(self.range_label, 5, 0)

        # radio buttons
        self.radioButton_fast = QtGui.QRadioButton('Fast', self)
        self.radioButton_accurate = QtGui.QRadioButton('Accurate', self)

        self.grid.addWidget(self.radioButton_fast, 7, 0)
        self.grid.addWidget(self.radioButton_accurate, 7, 1)

        # text box
        logTextBox = QPlainTextEditLogger(self)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(message)s', "%H:%M:%S"))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        self.grid.addWidget(logTextBox.widget, 8, 0, 1, 3)


        # button box
        self.buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setEnabled(False)
        self.grid.addWidget(self.buttonBox, 9, 1)
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.run_code)

        self.setLayout(self.grid)

        # self.statusBar()
        self.setWindowTitle('Apex Vod Review')

        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

        self.show()

    def center(self):
        """ centers the window to the center of the screen when opened """
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        centerPoint.setX(centerPoint.x() - frameGm.width() / 2)
        centerPoint.setY(centerPoint.y() - frameGm.height() / 2)
        frameGm.moveTo(centerPoint)
        self.move(frameGm.topLeft())

    def closeEvent(self, event):
        """ spawns a pop up to check if you intended to exit """

        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure you want to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def selectFileInput(self):
        """ File selection pop up for input """
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Select file', 'H:\ShadowPlay\Apex Legends')
        self.input_edit.setText(fname)

    def selectFileOutput(self):
        """ Folder selection pop up for output """
        fname = QtGui.QFileDialog.getExistingDirectory(self, 'Select folder', 'H:\ShadowPlay\Apex Legends')
        self.output_edit.setText(fname)

    def done(self):
        """ displays log and pop up once clip has finished proccessing """
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setEnabled(False)
        logging.info('complete')
        QtGui.QMessageBox.information(self, "Finished", "Clip has finished proccessing.")

    def run_code(self):
        """ Connected to Ok button, collects info from GUI and passes it to the code """
        logging.info('start')

        self.input_val = self.input_edit.text()

        if self.output_edit.text():
            self.output_val = self.output_edit.text()
            self.output_val = self.output_val + '\\'
        else:
            self.output_val = ''

        # frame_skip_check = self.frame_skip_cb.checkState()
        if self.frame_skip_cb.isChecked():
            self.frame_skip_val = self.spinBox_frame_skip.value()
        else:
            self.frame_skip_val = 1

        # merge_check = self.merge_val_cb.checkState()
        if self.merge_cb.isChecked():
            self.merge_val = True
        else:
            self.merge_val = False

        # kill_only_check = self.kill_only_cb.checkState()
        if self.kill_only_cb.isChecked():
            self.kill_only_val = True
        else:
            self.kill_only_val = False

        self.buffer_val = self.spinBox_buffer.value()
        self.range_val = self.spinBox_range.value()

        if self.radioButton_accurate.isChecked():
            self.radio_val = True
        elif self.radioButton_fast.isChecked():
            self.radio_val = False
        else:
            self.radio_val = False

        self.workThread = WorkThread(self.input_val, self.output_val, self.frame_skip_val, self.merge_val, self.kill_only_val, self.buffer_val, self.range_val, self.radio_val)
        # self.connect(self.workThread, QtCore.SIGNAL("update(QString)"), self.add)

        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setEnabled(True)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.workThread.terminate)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

        self.workThread.start()

        self.connect(self.workThread, QtCore.SIGNAL("finished()"), self.done)


def main():
    app = QtGui.QApplication(sys.argv)
    ui = ApexGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
