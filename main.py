from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem
import sys
import sqlite3
import pandas as pd
from datetime import datetime


class MainStorage:
    def __init__(self, ui):
        self.db = sqlite3.connect("main_storage.db")
        self.create_tables()
        self.ui = ui
        self.init_ui()


    def init_ui(self):
        uic.loadUi('main_storage.ui', self.ui)
        self.ui.back.clicked.connect(self.ui.start_ui)

        self.ui.move_to_filial_cklick = self.move_to_filial_cklick
        self.ui.move_to_filial.clicked.connect(self.ui.move_to_filial_cklick)

        self.update_products_table()

    
    def move_to_filial_cklick(self):
        table: QTableWidget = self.ui.select_products
        to_export = []

        for i in range(table.rowCount()):
            item_check:QTableWidgetItem = table.item(i,0)

            if item_check.checkState() == Qt.CheckState.Checked:
                item_index:QTableWidgetItem = table.item(i,1)
                index = int(item_index.text())

                item_name:QTableWidgetItem = table.item(i,2)

                item_count:QTableWidgetItem = table.item(i,5)
                item_count_all:QTableWidgetItem = table.item(i,4)
                count_all = int(item_count_all.text())

                item_price:QTableWidgetItem = table.item(i,3)
                price = int(item_price.text())

                try:
                    count = int(item_count.text())

                    if count <= 0:
                        QMessageBox.about(self.ui, "Ошибка", f"Укажите требуемое количество товара {item_name.text()} ({index})")
                        return

                    elif count > count_all:
                        QMessageBox.about(self.ui, "Ошибка", f"Товара {item_name.text()} ({index}) недостаточно на складе")
                        return
                    
                    else:
                        to_export.append({'index':index, 'name':item_name.text(), 'price':price, 'count':count, 'new_count':count_all-count})

                except:
                    QMessageBox.about(self.ui, "Ошибка", f"Укажите числом требуемое количество товара {item_name.text()} ({index})")
                    return
                
        if len(to_export) > 0:
            for product in to_export:
                self.db.execute("update products set count=? where id=?", (product['new_count'], product['index']))

            self.db.commit()

            df = pd.DataFrame(to_export)
            tm = datetime.now().strftime("%d.%m.%y %H.%M")
            df.to_csv(f'files/Перемещение в филиал {tm}.csv')

            self.update_products_table()

            QMessageBox.about(self.ui, "Готово", f'Документ "Перемещение в филиал" успешно сформирован!')


    def update_products_table(self):
        table: QTableWidget = self.ui.select_products
        table.clear()
        table.setColumnCount(6)
        table.verticalHeader().setVisible(False)
        table.setHorizontalHeaderLabels(['','Индекс','Название','Цена','Общее количество','Количество для перемещения'])

        products = self.get_all_products()
        for i, product in enumerate(products):
            table.insertRow(i)

            item_check = QTableWidgetItem()
            item_check.data(Qt.ItemDataRole.CheckStateRole)
            item_check.setCheckState(Qt.CheckState.Unchecked)
            table.setItem(i,0, item_check)
        
            item_index = QTableWidgetItem(str(product[0]))
            item_index.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i,1, item_index)

            item_name = QTableWidgetItem(product[1])
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i,2, item_name)

            item_price = QTableWidgetItem(str(product[2]))
            item_price.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i,3, item_price)

            item_count = QTableWidgetItem(str(product[3]))
            item_count.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i,4, item_count)

            table.setItem(i,5, QTableWidgetItem("0"))

        table.resizeColumnsToContents()


    def create_tables(self):
        self.db.execute("""CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL,
            price INT NOT NULL,
            count INT NOT NULL
        );""")

        self.db.commit()
        

    def get_all_products(self):
        cur = self.db.execute("select * from products")
        return cur.fetchall()


class Filial:
    def __init__(self, ui, filial_id):
        self.filial_id = filial_id
        self.ui = ui


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()        
        self.show()
        self.start_ui()


    def open_main_storage(self):
        MainStorage(self)


    def open_filial(self):
        uic.loadUi('filial_id.ui', self)
        self.back.clicked.connect(self.start_ui)
        self.filial_done.clicked.connect(self.enter_filial_id)


    def start_ui(self):
        uic.loadUi('start.ui', self)
        self.main_storage.clicked.connect(self.open_main_storage)
        self.filial.clicked.connect(self.open_filial)


    def enter_filial_id(self):
        try:
            filial_id = int(self.filial_id_text.text())
            QMessageBox.about(self, "Ok", str(filial_id))

        except:
            QMessageBox.about(self, "Error", "Введите число")


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec()