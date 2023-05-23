from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox
import sys
from main_storage import MainStorage
from filial import Filial


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()        
        self.show()
        self.start_ui()


    def open_main_storage(self):
        MainStorage(self)


    def open_filial(self):
        uic.loadUi('ui/filial_id.ui', self)
        self.back.clicked.connect(self.start_ui)
        self.filial_done.clicked.connect(self.enter_filial_id)


    def start_ui(self):
        uic.loadUi('ui/start.ui', self)
        self.setWindowTitle("Главный экран")
        self.main_storage.clicked.connect(self.open_main_storage)
        self.filial.clicked.connect(self.open_filial)


    def enter_filial_id(self):
        try:
            filial_id = int(self.filial_id_text.text())
            Filial(self,filial_id)

        except:
            QMessageBox.about(self, "Error", "Введите число")


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec()