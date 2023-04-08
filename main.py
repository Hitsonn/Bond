import sys

from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QWidget, QMessageBox
import sqlite3
from General import Gen_window
from forms.add_computer import *
from forms.edt_computer import *


# from Ui import Ui_MainWindow


class MyWidget(QMainWindow, Gen_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.update_table_computers()
        # self.tableWidget_1.itemChanged.connect(self.item_changed)
        self.add_comp.clicked.connect(self.show_add_form)
        self.del_comp.clicked.connect(self.delete_row)
        self.edt_comp.clicked.connect(self.edit_row)
        # self.up_comp.clicked.connect(self.update_table_computers)
        self.treeView.selectionModel().selectionChanged.connect(self.filter_data)

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
        results = cur.execute("SELECT DISTINCT location FROM computers").fetchall()
        model = QStandardItemModel()
        all_item = QStandardItem("все")
        all_item.setCheckable(False)
        all_item.setEditable(False)
        model.appendRow(all_item)
        for row in results:
            if location := row[0]:
                item = QStandardItem(location)
                item.setCheckable(False)
                item.setEditable(False)
                model.appendRow(item)
        self.treeView.setModel(model)
        print('Обновление прошло')
        con.close()

    # def item_changed(self, item):
    #     print(item.column())
        # print(item.text())
        # print(item.row())
        # self.tableWidget_1.modified[self.titles[item.column()]] = item.text()

    def filter_data(self):
        if not (selected_indexes := self.treeView.selectedIndexes()):
            return
        selected_location = selected_indexes[0].data()
        db = sqlite3.connect('db/computers.sqlite3')
        cursor = db.cursor()
        if selected_indexes[0].data() == 'все':
            cursor.execute("SELECT * FROM computers")
        else:
            cursor.execute("SELECT * FROM computers WHERE location=?", (selected_location,))
        results = cursor.fetchall()
        self.tableWidget_1.setRowCount(len(results))
        self.tableWidget_1.setColumnCount(len(results[0]))
        self.tableWidget_1.setHorizontalHeaderLabels([description[0] for description in cursor.description])
        self.tableWidget_1.setHorizontalHeaderLabels(
            ['id', 'тип', 'имя', 'кабинет', 'работник', 'инв_№', 'ip', 'гарантия', 'дата бслуживания',
             'след обслуживание'])
        for i, row in enumerate(results):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.tableWidget_1.setItem(i, j, item)
        db.close()


    def show_add_form(self):
        self.ex1 = AddComp()
        self.ex1.show()

    def show_edit_dialog(self, row):
        self.ex2 = EdtComp(row)
        self.ex2.show()

    def delete_row(self, db_path):
        # Получаем индекс выбранной строки
        selected_row = self.tableWidget_1.currentRow()
        if selected_row == -1:
            # Если ни одна строка не выбрана, выводим сообщение и выходим из функции
            QMessageBox.warning(None, "Ошибка", "Вы не выбрали строку")
            return

        # Получаем ID записи, которую нужно удалить
        id_ = self.tableWidget_1.item(selected_row, 0).text()

        # Удаляем запись из базы данных
        conn = sqlite3.connect("db/computers.sqlite3")
        cur = conn.cursor()
        cur.execute("DELETE FROM computers WHERE id=?", (id_,))
        conn.commit()
        conn.close()

        # Удаляем выбранную строку из таблицы
        self.tableWidget_1.removeRow(selected_row)

    def edit_row(self):
        # Получаем индекс выбранной строки
        selected_row = self.tableWidget_1.currentRow()
        if selected_row == -1:
            # Если ни одна строка не выбрана, выводим сообщение и выходим из функции
            QMessageBox.warning(None, "Ошибка", "Вы не выбрали строку")
            return

        # Получаем ID записи, которую нужно изменить
        id_ = self.tableWidget_1.item(selected_row, 0).text()

        # Открываем соединение с базой данных
        conn = sqlite3.connect("db/computers.sqlite3")
        cur = conn.cursor()

        # Получаем текущие значения полей записи из базы данных
        cur.execute("SELECT * FROM computers WHERE id=?", (id_,))
        row = cur.fetchone()
        # Открываем диалог редактирования записи
        self.show_edit_dialog(row)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
