import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from video_main import ApexVod

import logging

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class Logger(logging.Handler):
    """ Logging module """
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class WorkThread(QtCore.QThread):
    """ Thread for video proccessing """
    def __init__(self,
                 input_val,
                 output_val,
                 frame_skip_val,
                 merge_val,
                 kill_only_val,
                 buffer_val,
                 range_val,
                 radio_val):

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
        apexvod.proccess_vod(apexvod.ref,
                             apexvod.frame_data,
                             apexvod.frame_count,
                             apexvod.health_bar_coord,
                             self.input_val,
                             self.output_val,
                             self.kill_only_val,
                             self.merge_val,
                             self.frame_skip_val,
                             self.range_val,
                             self.buffer_val,
                             apexvod.debug,
                             self.radio_val)
        # self.quit()


class ApexGui(QtWidgets.QWidget, Logger):
    """ Gui  """
    def __init__(self):
        super(ApexGui, self).__init__()

        self.initUI()

    def initUI(self):

        self.resize(642, 254)
        self.center()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

        # input and output file browsers
        self.input = QtWidgets.QLabel('Input')
        self.output = QtWidgets.QLabel('Output')

        self.input_edit = QtWidgets.QLineEdit()
        self.input_edit.setMinimumSize(QtCore.QSize(450, 20))
        self.output_edit = QtWidgets.QLineEdit()
        self.output_edit.setMinimumSize(QtCore.QSize(450, 20))

        self.input_btn = QtWidgets.QPushButton('Browse', self)
        self.output_btn = QtWidgets.QPushButton('Browse', self)
        self.input_btn.clicked.connect(self.selectFileInput)
        self.output_btn.clicked.connect(self.selectFileOutput)

        self.grid.addWidget(self.input, 1, 0)
        self.grid.addWidget(self.input_edit, 1, 1)
        self.grid.addWidget(self.input_btn, 1, 2)

        self.grid.addWidget(self.output, 2, 0)
        self.grid.addWidget(self.output_edit, 2, 1)
        self.grid.addWidget(self.output_btn, 2, 2)

        # check boxes
        self.frame_skip_cb = QtWidgets.QCheckBox('Frame Skip', self)
        self.merge_cb = QtWidgets.QCheckBox('Merge', self)
        self.kill_only_cb = QtWidgets.QCheckBox('Kill only', self)
        self.grid.addWidget(self.frame_skip_cb, 3, 0)
        self.grid.addWidget(self.merge_cb, 6, 0)
        self.grid.addWidget(self.kill_only_cb, 6, 1)

        # spin boxes
        self.spinBox_frame_skip = QtWidgets.QSpinBox(self)
        self.spinBox_buffer = QtWidgets.QSpinBox(self)
        self.spinBox_range = QtWidgets.QSpinBox(self)

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

        self.buffer_label = QtWidgets.QLabel('Buffer')
        self.range_label = QtWidgets.QLabel('Range')
        self.grid.addWidget(self.buffer_label, 4, 0)
        self.grid.addWidget(self.range_label, 5, 0)

        # radio buttons
        self.radioButton_fast = QtWidgets.QRadioButton('Fast', self)
        self.radioButton_accurate = QtWidgets.QRadioButton('Accurate', self)

        self.grid.addWidget(self.radioButton_fast, 7, 0)
        self.grid.addWidget(self.radioButton_accurate, 7, 1)

        # text box
        logTextBox = Logger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(message)s', "%H:%M:%S"))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)

        self.grid.addWidget(logTextBox.widget, 8, 0, 1, 3)

        # button box
        self.buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setEnabled(False)
        self.grid.addWidget(self.buttonBox, 9, 1)
        
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.start_vod_proccessing)

        self.setLayout(self.grid)

        # self.statusBar()
        self.setWindowTitle('Apex Vod Auto Editor')

        # QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))

        self.show()

    def center(self):
        """ centers the window to the center of the screen when opened """
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        centerPoint.setX(centerPoint.x() - frameGm.width() / 2)
        centerPoint.setY(centerPoint.y() - frameGm.height() / 2)
        frameGm.moveTo(centerPoint)
        self.move(frameGm.topLeft())

    def closeEvent(self, event):
        """ spawns a pop up to check if you intended to exit """

        reply = QtWidgets.QMessageBox.question(self,
                                           'Message',
                                           "Are you sure you want to quit?",
                                           QtWidgets.QMessageBox.Yes |
                                           QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def selectFileInput(self):
        """ File selection pop up for input """
        fname = QtWidgets.QFileDialog.getOpenFileName(self,
                                                  'Select file',
                                                  'C:\\',
                                                  "Video files (*.mp4 *.avi *.mkv )"
        self.input_edit.setText(fname)

    def selectFileOutput(self):
        """ Folder selection pop up for output """
        fname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder', 'C:\\')
        self.output_edit.setText(fname)

    def start_vod_proccessing(self):
        """ Connected to Ok button, collects info from GUI and passes it to the code """
        logging.info('start')

        self.input_val = self.input_edit.text()
        self.output_val = self.output_edit.text() + '\\' if self.output_edit.text() else ''
        self.frame_skip_val = self.spinBox_frame_skip.value() if self.frame_skip_cb.isChecked() else 1
        self.merge_val = self.merge_cb.isChecked()
        self.kill_only_val = self.kill_only_cb.isChecked()
        self.buffer_val = self.spinBox_buffer.value()
        self.range_val = self.spinBox_range.value()
        self.radio_val = self.radioButton_accurate.isChecked()

        self.workThread = WorkThread(self.input_val,
                                     self.output_val,
                                     self.frame_skip_val,
                                     self.merge_val,
                                     self.kill_only_val,
                                     self.buffer_val,
                                     self.range_val,
                                     self.radio_val)
        
        # enables the cancel button and connects it to the thread termination function
        # disables OK button to limit one clip being proccessed at a time
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setEnabled(True)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.workThread.exit)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        self.workThread.start()

        # self.connect(self.workThread, QtCore.SIGNAL("finished()"), self.done)
        self.workThread.finished.connect(self.done)
        
    def done(self):
        """ displays log and pop up to be displayed once clip has finished proccessing """
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setEnabled(False)
        logging.info('complete')
        QtWidgets.QMessageBox.information(self, "Finished", f"{self.input_val} has finished proccessing.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = ApexGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
