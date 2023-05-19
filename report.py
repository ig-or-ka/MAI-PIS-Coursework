from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
import pandas as pd


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