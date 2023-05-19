from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog
import pandas as pd
from datetime import datetime


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


def update_products_table(prog, main_storage:bool):
    table: QTableWidget = prog.ui.select_products
    table.clear()
    table.setRowCount(0)
    table.setColumnCount(6)
    table.verticalHeader().setVisible(False)

    labels = ['','Индекс','Название','Цена','Общее количество']

    if main_storage:
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


def move_or_sell(prog, main_storage:bool):
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

        if not main_storage:
            prog.sells_to_export.extend(to_export)

        prog.db.commit()

        df = pd.DataFrame(to_export)
        df.pop('new_count')
        tm = datetime.now().strftime("%d.%m.%y %H.%M")

        if main_storage:
            filename = f'files/Перемещение в филиал {tm}.csv'

        else:
            filename = f'files/Чек филиал {prog.filial_id} {tm}.csv'

        df.to_csv(filename)

        update_products_table(prog, main_storage)

        if main_storage:
            QMessageBox.about(prog.ui, "Готово", f'Документ "Перемещение в филиал" успешно сформирован!')

        else:
            QMessageBox.about(prog.ui, "Готово", f'Продажа совершена, чек сформирован!')