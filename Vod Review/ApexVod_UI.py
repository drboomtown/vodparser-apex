import sys
from PyQt4 import QtCore, QtGui
from frame import ApexVod

import logging


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtGui.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class WorkThread(QtCore.QThread):
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
        self.wait()

    # def onfinish(self):
    #     self.finish()

    def run(self):
        apexvod = ApexVod()
        apexvod.main_vod(apexvod.ref, apexvod.frame_data, apexvod.frame_count, apexvod.health_bar_coord,
                         self.input_val, self.output_val, self.kill_only_val, self.merge_val,
                         self.frame_skip_val, self.range_val, self.buffer_val,
                         apexvod.debug, self.radio_val)
        self.quit()


class ApexGui(QtGui.QWidget, QPlainTextEditLogger):

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

        # Add the new logging box widget to the layout
        self.grid.addWidget(logTextBox.widget, 8, 0, 1, 3)

        # self.log_text = QtGui.QPlainTextEdit()
        # self.grid.addWidget(self.log_text, 8, 0, 1, 3)
        # self.log_text.setReadOnly(True)

        # button box
        self.buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        # self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setEnabled(False)
        self.grid.addWidget(self.buttonBox, 9, 1)
        # self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.run_code)

        self.setLayout(self.grid)

        # self.statusBar()
        self.setWindowTitle('Apex Vod Review')

        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

        self.show()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        centerPoint.setX(centerPoint.x() - frameGm.width() / 2)
        centerPoint.setY(centerPoint.y() - frameGm.height() / 2)
        frameGm.moveTo(centerPoint)
        self.move(frameGm.topLeft())

    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure you want to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def selectFileInput(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Select file', 'H:\ShadowPlay\Apex Legends')
        self.input_edit.setText(fname)

    def selectFileOutput(self):
        fname = QtGui.QFileDialog.getExistingDirectory(self, 'Select folder', 'H:\ShadowPlay\Apex Legends')
        self.output_edit.setText(fname)



    def done(self):
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setEnabled(False)
        logging.info('complete')
        QtGui.QMessageBox.information(self, "Finished", "Clip has finished proccessing.")


    def run_code(self):
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

# try:
#     _fromUtf8 = QtCore.QString.fromUtf8
# except AttributeError:
#     def _fromUtf8(s):
#         return s
#
# try:
#     _encoding = QtGui.QApplication.UnicodeUTF8
#
#     def _translate(context, text, disambig):
#         return QtGui.QApplication.translate(context, text, disambig, _encoding)
#
#
# except AttributeError:
#     def _translate(context, text, disambig):
#         return QtGui.QApplication.translate(context, text, disambig)
#
#
# class Ui_Dialog(object):
#     def __init__(self):
#         self.buttonBox = QtGui.QDialogButtonBox(Dialog)
#         self.horizontalLayoutWidget = QtGui.QWidget(Dialog)
#         self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
#         self.label_input = QtGui.QLabel(self.horizontalLayoutWidget)
#         self.lineEdit_input = QtGui.QLineEdit(self.horizontalLayoutWidget)
#         self.Btn_browse_input = QtGui.QPushButton(self.horizontalLayoutWidget)
#         self.horizontalLayoutWidget_2 = QtGui.QWidget(Dialog)
#         self.horizontalLayout_2 = QtGui.QHBoxLayout(self.horizontalLayoutWidget_2)
#         self.label_output = QtGui.QLabel(self.horizontalLayoutWidget_2)
#         self.lineEdit_output = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
#         self.Btn_browse_output = QtGui.QPushButton(self.horizontalLayoutWidget_2)
#         self.formLayoutWidget = QtGui.QWidget(Dialog)
#         self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
#         self.label_buffer = QtGui.QLabel(self.formLayoutWidget)
#         self.spinBox_buffer = QtGui.QSpinBox(self.formLayoutWidget)
#         self.label_range = QtGui.QLabel(self.formLayoutWidget)
#         self.spinBox_range = QtGui.QSpinBox(self.formLayoutWidget)
#         self.verticalLayoutWidget = QtGui.QWidget(Dialog)
#         self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
#         self.checkBox_merge = QtGui.QCheckBox(self.verticalLayoutWidget)
#         self.checkBox_kill = QtGui.QCheckBox(self.verticalLayoutWidget)
#         self.verticalLayoutWidget_2 = QtGui.QWidget(Dialog)
#         self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
#         self.radioButton_fast = QtGui.QRadioButton(self.verticalLayoutWidget_2)
#         self.radioButton_accurate = QtGui.QRadioButton(self.verticalLayoutWidget_2)
#         self.formLayoutWidget_2 = QtGui.QWidget(Dialog)
#         self.formLayout_2 = QtGui.QFormLayout(self.formLayoutWidget_2)
#         self.checkBox_skip = QtGui.QCheckBox(self.formLayoutWidget_2)
#         self.spinBox_skip = QtGui.QSpinBox(self.formLayoutWidget_2)
#
#
#
#     def setupUi(self, Dialog):
#         Dialog.setObjectName(_fromUtf8("Dialog"))
#         Dialog.resize(400, 275)
#         Dialog.setSizeGripEnabled(False)
#         Dialog.setModal(False)
#
#         self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
#         self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
#         self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
#         self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
#
#         self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 381, 31))
#         self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
#         self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
#
#
#         self.label_input.setMinimumSize(QtCore.QSize(0, 18))
#         self.label_input.setObjectName(_fromUtf8("label_input"))
#         self.horizontalLayout.addWidget(self.label_input, QtCore.Qt.AlignLeft)
#
#         self.lineEdit_input.setMinimumSize(QtCore.QSize(0, 18))
#         self.lineEdit_input.setObjectName(_fromUtf8("lineEdit_input"))
#         self.horizontalLayout.addWidget(self.lineEdit_input)
#
#         self.Btn_browse_input.setMinimumSize(QtCore.QSize(0, 18))
#         self.Btn_browse_input.setObjectName(_fromUtf8("Btn_browse_input"))
#         self.horizontalLayout.addWidget(self.Btn_browse_input)
#
#
#         self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 50, 381, 31))
#         self.horizontalLayoutWidget_2.setObjectName(_fromUtf8("horizontalLayoutWidget_2"))
#         self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
#
#         self.label_output.setMinimumSize(QtCore.QSize(0, 18))
#         self.label_output.setObjectName(_fromUtf8("label_output"))
#         self.horizontalLayout_2.addWidget(self.label_output, QtCore.Qt.AlignLeft)
#
#         self.lineEdit_output.setMinimumSize(QtCore.QSize(0, 18))
#         self.lineEdit_output.setObjectName(_fromUtf8("lineEdit_output"))
#         self.horizontalLayout_2.addWidget(self.lineEdit_output)
#
#         self.Btn_browse_output.setMinimumSize(QtCore.QSize(0, 18))
#         self.Btn_browse_output.setObjectName(_fromUtf8("Btn_browse_output"))
#         self.horizontalLayout_2.addWidget(self.Btn_browse_output)
#
#
#         self.formLayoutWidget.setGeometry(QtCore.QRect(40, 90, 81, 61))
#         self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
#         self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
#         self.formLayout.setObjectName(_fromUtf8("formLayout"))
#
#         self.label_buffer.setMinimumSize(QtCore.QSize(0, 18))
#         self.label_buffer.setObjectName(_fromUtf8("label_buffer"))
#         self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_buffer)
#
#         self.spinBox_buffer.setMinimumSize(QtCore.QSize(0, 18))
#         self.spinBox_buffer.setMaximumSize(QtCore.QSize(34, 16777215))
#         self.spinBox_buffer.setProperty("value", 3)
#         self.spinBox_buffer.setObjectName(_fromUtf8("spinBox_buffer"))
#         self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.spinBox_buffer)
#
#         self.label_range.setMinimumSize(QtCore.QSize(0, 18))
#         self.label_range.setObjectName(_fromUtf8("label_range"))
#         self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_range)
#
#         self.spinBox_range.setMinimumSize(QtCore.QSize(0, 18))
#         self.spinBox_range.setMaximumSize(QtCore.QSize(34, 16777215))
#         self.spinBox_range.setProperty("value", 20)
#         self.spinBox_range.setObjectName(_fromUtf8("spinBox_buffer_2"))
#         self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.spinBox_range)
#
#         self.verticalLayoutWidget.setGeometry(QtCore.QRect(190, 90, 81, 51))
#         self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
#         self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
#
#         self.checkBox_merge.setMinimumSize(QtCore.QSize(0, 18))
#         self.checkBox_merge.setChecked(True)
#         self.checkBox_merge.setTristate(False)
#         self.checkBox_merge.setObjectName(_fromUtf8("checkBox_merge"))
#         self.verticalLayout.addWidget(self.checkBox_merge)
#
#         self.checkBox_kill.setMinimumSize(QtCore.QSize(0, 18))
#         self.checkBox_kill.setObjectName(_fromUtf8("checkBox_kill"))
#         self.verticalLayout.addWidget(self.checkBox_kill)
#
#         self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(280, 90, 91, 51))
#         self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
#         self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
#
#         self.radioButton_fast.setMinimumSize(QtCore.QSize(0, 18))
#         self.radioButton_fast.setObjectName(_fromUtf8("radioButton_fast"))
#         self.verticalLayout_2.addWidget(self.radioButton_fast)
#
#         self.radioButton_accurate.setMinimumSize(QtCore.QSize(0, 18))
#         self.radioButton_accurate.setObjectName(_fromUtf8("radioButton_accurate"))
#         self.verticalLayout_2.addWidget(self.radioButton_accurate)
#
#         self.formLayoutWidget_2.setGeometry(QtCore.QRect(100, 90, 81, 61))
#         self.formLayoutWidget_2.setObjectName(_fromUtf8("formLayoutWidget_2"))
#         self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
#         self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
#
#         self.checkBox_skip.setMinimumSize(QtCore.QSize(0, 18))
#         self.checkBox_skip.setObjectName(_fromUtf8("checkBox_skip"))
#         self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.checkBox_skip)
#
#         self.spinBox_skip.setMinimumSize(QtCore.QSize(0, 18))
#         self.spinBox_skip.setMinimum(2)
#         self.spinBox_skip.setMaximum(3)
#         self.spinBox_skip.setObjectName(_fromUtf8("spinBox_skip"))
#         self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.spinBox_skip)
#
#         self.retranslateUi(Dialog)
#         QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
#         QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
#         QtCore.QMetaObject.connectSlotsByName(Dialog)
#
#     def retranslateUi(self, Dialog):
#         Dialog.setWindowTitle(_translate("Dialog", "Apex Vod Review", None))
#         self.label_input.setText(_translate("Dialog", "Input  ", None))
#         self.Btn_browse_input.setText(_translate("Dialog", "Browse", None))
#         self.label_output.setText(_translate("Dialog", "Output", None))
#         self.Btn_browse_output.setText(_translate("Dialog", "Browse", None))
#         self.label_buffer.setText(_translate("Dialog", "Buffer", None))
#         self.label_range.setText(_translate("Dialog", "Range", None))
#         self.checkBox_merge.setText(_translate("Dialog", "Merge", None))
#         self.checkBox_kill.setText(_translate("Dialog", "Kill only", None))
#         self.radioButton_fast.setText(_translate("Dialog", "Fast", None))
#         self.radioButton_accurate.setText(_translate("Dialog", "Accurate", None))
#         self.checkBox_skip.setText(_translate("Dialog", "frame skip", None))
#
#
# if __name__ == "__main__":
#     import sys
#     app = QtGui.QApplication(sys.argv)
#     Dialog = QtGui.QDialog()
#     ui = Ui_Dialog()
#     ui.setupUi(Dialog)
#     Dialog.show()
#     sys.exit(app.exec_())
#