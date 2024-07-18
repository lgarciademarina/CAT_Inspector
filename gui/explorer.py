import sys
from PyQt5.QtWidgets import QWidget, QFileDialog


class Explorer(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.title = 'Explorador de ficheros'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.openFileNameDialog()
        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Seleccione un fichero", "","zip (*.zip)", 
        options=options)
        if fileName:
            self.parent.path.setText(fileName)
        