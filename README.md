# vodparser-apex

need FFMPEG installed and working correctly

opencv, imutils, numpy

Frame processor class? 
"And pass different functions into it so you can have different UI elements scanned at different intervals"
"I don't know how I'd lay it out yet, but I feel like a UI class to contain all the coords / ui locations" 
"so you don't have to ever edit the classes with all the logic" 


def selectFile():
    lineEdit.setText(QFileDialog.getOpenFileName())

pushButton.clicked.connect(selectFile)
