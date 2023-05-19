from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog
import sys
import sqlite3
import pandas as pd
from datetime import datetime


class Report(QtWidgets.QDialog):
    def __init__(self, parent, df:pd.DataFrame):
        super(Report, self).__init__(parent)
        self.df = df
        uic.loadUi('report.ui', self)
        self.show()
        self.load_table()

    def load_table(self):
        table: QTableWidget = self.products
        table.setColumnCount(5)
        table.verticalHeader().setVisible(False)

        table.setHorizontalHeaderLabels(['Индекс','Название','Цена','Количество','Сумма'])

        index_filial_id = self.df['index'].count()-1
        filial_id = int(self.df['index'].loc[self.df.index[index_filial_id]])
        self.filial_id.setText(f"Номер филиала: {filial_id}")

        all_sum = 0

        for i in range(self.df['index'].count()-1):
            index = int(self.df['index'].loc[self.df.index[i]])
            name = self.df['name'].loc[self.df.index[i]]
            price = int(self.df['price'].loc[self.df.index[i]])
            count = int(self.df['count'].loc[self.df.index[i]])

            all_sum += count*price

            table.insertRow(i)
       
            item_index = QTableWidgetItem(str(index))
            item_index.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i,0, item_index)

            item_name = QTableWidgetItem(name)
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i,1, item_name)

            item_price = QTableWidgetItem(str(price))
            item_price.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i,2, item_price)

            item_count = QTableWidgetItem(str(count))
            item_count.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i,3, item_count)

            item_sum = QTableWidgetItem(str(count*price))
            item_sum.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i,4, item_sum)

        table.resizeColumnsToContents()

        self.all_sum.setText(f"Итого: {all_sum}")

def create_table(db):
    db.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name TEXT NOT NULL,
        price INT NOT NULL,
        count INT NOT NULL
    );""")

    db.commit()


def get_all_products(db):
    cur = db.execute("select * from products")
    return cur.fetchall()


def update_products_table(prog):
    table: QTableWidget = prog.ui.select_products
    table.clear()
    table.setRowCount(0)
    table.setColumnCount(6)
    table.verticalHeader().setVisible(False)

    labels = ['','Индекс','Название','Цена','Общее количество']

    if type(prog) == MainStorage:
        labels.append('Количество для перемещения')

    else:
        labels.append('Количество для продажи')

    table.setHorizontalHeaderLabels(labels)

    products = get_all_products(prog.db)
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


def move_or_sell(prog):
    table: QTableWidget = prog.ui.select_products
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
                    QMessageBox.about(prog.ui, "Ошибка", f"Укажите требуемое количество товара {item_name.text()} ({index})")
                    return

                elif count > count_all:
                    QMessageBox.about(prog.ui, "Ошибка", f"Товара {item_name.text()} ({index}) недостаточно на складе")
                    return
                
                else:
                    to_export.append({'index':index, 'name':item_name.text(), 'price':price, 'count':count, 'new_count':count_all-count})

            except:
                QMessageBox.about(prog.ui, "Ошибка", f"Укажите числом требуемое количество товара {item_name.text()} ({index})")
                return
            
    if len(to_export) > 0:
        for product in to_export:
            prog.db.execute("update products set count=? where id=?", (product['new_count'], product['index']))

        if type(prog) == Filial:
            prog.sells_to_export.extend(to_export)

        prog.db.commit()

        df = pd.DataFrame(to_export)
        df.pop('new_count')
        tm = datetime.now().strftime("%d.%m.%y %H.%M")

        if type(prog) == MainStorage:
            filename = f'files/Перемещение в филиал {tm}.csv'

        else:
            filename = f'files/Чек филиал {prog.filial_id} {tm}.csv'

        df.to_csv(filename)

        update_products_table(prog)

        if type(prog) == MainStorage:
            QMessageBox.about(prog.ui, "Готово", f'Документ "Перемещение в филиал" успешно сформирован!')

        else:
            QMessageBox.about(prog.ui, "Готово", f'Продажа совершена, чек сформирован!')


class MainStorage:
    def __init__(self, ui):
        self.db = sqlite3.connect("files/main_storage.db")
        create_table(self.db)
        self.ui = ui
        self.init_ui()
        update_products_table(self)


    def init_ui(self):
        uic.loadUi('main_storage.ui', self.ui)
        self.ui.back.clicked.connect(self.ui.start_ui)

        self.ui.move_to_filial_cklick = self.move_to_filial_cklick
        self.ui.move_to_filial.clicked.connect(self.ui.move_to_filial_cklick)

        self.ui.read_inv_click = self.read_inv_click
        self.ui.read_inv.clicked.connect(self.ui.read_inv_click)

    
    def move_to_filial_cklick(self):
        move_or_sell(self)


    def read_inv_click(self):
        dialog = QFileDialog(self.ui)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("CSV (*.csv)")

        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            df = pd.read_csv(filename)

            Report(self.ui, df)


class Filial:
    def __init__(self, ui, filial_id):
        self.sells_to_export = []
        self.filial_id = filial_id
        self.ui = ui
        self.db = sqlite3.connect(f"files/filial_{filial_id}.db")
        create_table(self.db)
        self.init_ui()
        update_products_table(self)


    def init_ui(self):
        uic.loadUi('filial.ui', self.ui)
        self.ui.back.clicked.connect(self.ui.start_ui)

        self.ui.receipt_invoice_click = self.receipt_invoice_click
        self.ui.receipt_invoice.clicked.connect(self.ui.receipt_invoice_click)

        self.ui.sell_click = self.sell_click
        self.ui.sell.clicked.connect(self.ui.sell_click)

        self.ui.export_sells_click = self.export_sells_click
        self.ui.export_sells.clicked.connect(self.ui.export_sells_click)


    def sell_click(self):
        move_or_sell(self)


    def export_sells_click(self):
        if len(self.sells_to_export) == 0:
            QMessageBox.about(self.ui, "Ошибка", f"Не совершено ни одной покупки!")

        else:
            products = dict()

            for sell in self.sells_to_export:
                prod = products.setdefault(sell['index'], {'index':sell['index'],'name':sell['name'],'price':sell['price'],'count':0})
                prod['count'] += sell['count']

            products[-10] = {'index':self.filial_id,'name':'Филиал','price':'','count':''}
            df = pd.DataFrame(products.values())
            tm = datetime.now().strftime("%d.%m.%y %H.%M")
            df.to_csv(f"files/Отчет Филиал {self.filial_id} {tm}.csv")

            self.sells_to_export = []
            QMessageBox.about(self.ui, "Готово", f"Отчет сформирован!")            


    def receipt_invoice_click(self):
        dialog = QFileDialog(self.ui)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("CSV (*.csv)")

        if dialog.exec():
            to_rewrite_prices = []

            filename = dialog.selectedFiles()[0]
            df = pd.read_csv(filename)

            for i in range(df['index'].count()):
                index = int(df['index'].loc[df.index[i]])
                name = df['name'].loc[df.index[i]]
                price = int(df['price'].loc[df.index[i]])
                count = int(df['count'].loc[df.index[i]])

                cur = self.db.execute("select * from products where id=?",(index,))
                res = cur.fetchone()

                if res == None:
                    self.db.execute(
                        "insert into products (id, name, price, count) values (?,?,?,?)", 
                        (index, name, price, count)
                    )

                else:
                    if res[2] != price:
                        to_rewrite_prices.append({'index':index, 'name':name, 'price':price})

                    self.db.execute("update products set price=?, count=? where id=?",(price,res[3]+count,index))
                
            self.db.commit()
            
            if len(to_rewrite_prices) > 0:
                df = pd.DataFrame(to_rewrite_prices)
                tm = datetime.now().strftime("%d.%m.%y %H.%M")
                df.to_csv(f'files/Изменение цен филиал {self.filial_id} {tm}.csv')

                QMessageBox.about(self.ui, "Изменение", f'Сформирован список изменения цен')

            update_products_table(self)

            QMessageBox.about(self.ui, "Готово", f'Накладная обработана!')


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
            Filial(self,filial_id)

        except:
            QMessageBox.about(self, "Error", "Введите число")


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec()