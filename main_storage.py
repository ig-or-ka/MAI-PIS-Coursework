from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog
import sqlite3
import pandas as pd
from utils import create_table, update_products_table, move_or_sell
from report import Report


class MainStorage:
    def __init__(self, ui):
        self.db = sqlite3.connect("files/main_storage.db")
        create_table(self.db)
        self.ui = ui
        self.init_ui()
        update_products_table(self, True)


    def init_ui(self):
        uic.loadUi('main_storage.ui', self.ui)
        self.ui.back.clicked.connect(self.ui.start_ui)

        self.ui.move_to_filial_cklick = self.move_to_filial_cklick
        self.ui.move_to_filial.clicked.connect(self.ui.move_to_filial_cklick)

        self.ui.read_inv_click = self.read_inv_click
        self.ui.read_inv.clicked.connect(self.ui.read_inv_click)

    
    def move_to_filial_cklick(self):
        move_or_sell(self, True)


    def read_inv_click(self):
        dialog = QFileDialog(self.ui)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("CSV (*.csv)")

        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            df = pd.read_csv(filename)

            Report(self.ui, df)