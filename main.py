import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView
import sqlite3


# from Ui import Ui_MainWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Ui.ui', self)
        self.update_table_computers()
        self.tableWidget_1.itemChanged.connect(self.item_changed)

    def update_table_computers(self):
        con = sqlite3.connect("db/computers.sqlite3")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM computers""").fetchall()
        self.tableWidget_1.setColumnCount(10)
        self.tableWidget_1.setRowCount(0)
        self.tableWidget_1.setHorizontalHeaderLabels(
            ['id', 'тип', 'имя', 'кабинет', 'работник', 'инв_№', 'ip', 'гарантия', 'дата бслуживания',
             'след обслуживание'])
        for i, row in enumerate(result):
            self.tableWidget_1.setRowCount(
                self.tableWidget_1.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget_1.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget_1.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def item_changed(self, item):
        print(item.column())
        print(item.text())
        print(item.row())
        # self.tableWidget_1.modified[self.titles[item.column()]] = item.text()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
