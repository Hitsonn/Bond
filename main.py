import datetime
import json
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableWidgetItem, QApplication
from forms.general import Ui_mainWindow
from windows.add_computer import *
from windows.edt_computer import *
from windows.setting_window import *


class MyWidget(QMainWindow, Ui_mainWindow):
    def __init__(self):
        super().__init__()
        with open("data\set.json", "r") as f:
            settings = json.load(f)
        self.service1 = settings["service1"]
        self.service2 = settings["service2"]
        self.service3 = settings["service3"]
        self.setupUi(self)
        self.update_table_computers()
        self.tableWidget_1.itemSelectionChanged.connect(self.update_textedit)
        self.add_btn.clicked.connect(self.show_add_form)
        self.del_btn.clicked.connect(self.delete_row)
        self.edt_btn.clicked.connect(self.edit_row)
        self.tableWidget_1.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.serv1_btn.clicked.connect(lambda: self.update_service(1))
        self.serv2_btn.clicked.connect(lambda: self.update_service(2))
        self.serv3_btn.clicked.connect(lambda: self.update_service(3))
        self.current_computer_id = None
        self.dubll_btn.clicked.connect(self.add_duplicate)
        self.action_3.triggered.connect(self.setting)

    def update_table_computers(self):
        con = sqlite3.connect("db/computers.sqlite3")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM computers""").fetchall()
        self.tableWidget_1.setColumnCount(8)
        self.tableWidget_1.setRowCount(0)
        self.tableWidget_1.setHorizontalHeaderLabels(
            ['id', 'наименование', 'сетевое имя', 'кабинет', 'работник', 'инв_№', 'ip', 'гарантия'])
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
        self.treeView.selectionModel().selectionChanged.connect(self.filter_data)
        con.close()

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
            ['id', 'наименование', 'сетевое имя', 'кабинет', 'работник', 'инв_№', 'ip', 'гарантия'])
        for i, row in enumerate(results):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.tableWidget_1.setItem(i, j, item)
        db.close()

    def show_add_form(self):
        self.ex1 = AddComp()
        self.ex1.closed.connect(self.update_table_computers)
        self.ex1.show()

    def add_duplicate(self):
        if not self.current_computer_id:
            QMessageBox.warning(None, "Ошибка", "Вы не выбрали строку")
            return
        self.ex3 = AddComp(id=self.current_computer_id)
        self.ex3.closed.connect(self.update_table_computers)
        self.ex3.show()

    def show_edit_dialog(self, row):
        self.ex2 = EdtComp(row)
        self.ex2.closed.connect(self.update_table_computers)
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

    def check_date(self, date_str):
        date_format = '%d.%m.%Y'
        today = datetime.datetime.today()
        date = datetime.datetime.strptime(date_str, date_format)
        delta = today - date
        return delta.days

    def update_textedit(self):
        result = None
        name = None
        # получаем выделенную строку
        selected_row = self.tableWidget_1.currentRow()
        # получаем содержимое первой ячейки в этой строке
        if self.tableWidget_1.item(selected_row, 0):
            id = self.tableWidget_1.item(selected_row, 0).text()
            self.current_computer_id = id
            name = self.tableWidget_1.item(selected_row, 2).text()
            self.conn = sqlite3.connect('db/computers.sqlite3')
            cur = self.conn.cursor()
            result = cur.execute(f"""SELECT * FROM service WHERE id={id}""").fetchall()
            self.conn.commit()
            self.conn.close()
        # Если данные найдены, заполняем текстовое поле
        if result:
            self.textEdit.clear()
            self.textEdit.append(f"Данные для {name}:\n")
            if self.check_date(result[0][1]) > self.service1:
                self.textEdit.append(f'Дата ТО_1: <font color="red">{result[0][1]}</font>')
            else:
                self.textEdit.append(f'Дата ТО_1: {result[0][1]}')
            if self.check_date(result[0][2]) > self.service2:
                self.textEdit.append(f'Дата ТО_2: <font color="red">{result[0][2]}</font>')
            else:
                self.textEdit.append(f'Дата ТО_2: {result[0][2]}')
            if self.check_date(result[0][3]) > self.service3:
                self.textEdit.append(f'Дата ТО_3: <font color="red">{result[0][3]}</font>')
            else:
                self.textEdit.append(f'Дата ТО_3: {result[0][3]}')
        else:
            self.textEdit.setText(f"Для отображения выделите объект")

    def update_service(self, service_number):
        service_column = f'service{service_number}'
        today = datetime.date.today().strftime('%d.%m.%Y')

        con = sqlite3.connect("db/computers.sqlite3")
        cur = con.cursor()
        if self.current_computer_id:
            cur.execute(f"UPDATE service SET {service_column} = ? WHERE id = ?", (today, self.current_computer_id))
        con.commit()
        con.close()
        self.update_textedit()

    def setting(self):
        self.ex4 = SettingWindow()
        self.ex4.closed.connect(self.update_table_computers)
        self.ex4.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
