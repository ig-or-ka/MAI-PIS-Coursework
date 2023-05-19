from PyQt6 import uic
from PyQt6.QtWidgets import QMessageBox, QFileDialog
import sqlite3
import pandas as pd
from datetime import datetime
from utils import create_table, update_products_table, move_or_sell


class Filial:
    def __init__(self, ui, filial_id):
        self.sells_to_export = []
        self.filial_id = filial_id
        self.ui = ui
        self.db = sqlite3.connect(f"files/filial_{filial_id}.db")
        create_table(self.db)
        self.init_ui()
        update_products_table(self,False)


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
        move_or_sell(self,False)


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

            update_products_table(self,False)

            QMessageBox.about(self.ui, "Готово", f'Накладная обработана!')