import datetime
import json
import os
import shutil
import sys

import xlsxwriter as xlsxwriter
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableWidgetItem, QApplication, QHeaderView, QInputDialog, QFileDialog
from forms.ui import Ui_mainWindow
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

        self.update_table_computers(self.tableWidget_1, self.treeView, 'computers')
        self.update_table_computers(self.tableWidget_2, self.treeView_2, 'office_equipment')
        self.update_table_computers(self.tableWidget_3, self.treeView_3, 'other')
        self.tableWidget_1.itemSelectionChanged.connect(
            lambda: self.update_textedit(self.tableWidget_1, self.textEdit, "service"))
        self.tableWidget_2.itemSelectionChanged.connect(
            lambda: self.update_textedit(self.tableWidget_2, self.textEdit_2, "service2"))
        self.tableWidget_3.itemSelectionChanged.connect(
            lambda: self.update_textedit(self.tableWidget_3, self.textEdit_3, "service3"))
        self.add_btn.clicked.connect(
            lambda: self.show_add_form('computers', 'service', self.tableWidget_1, self.treeView))
        self.add_btn_2.clicked.connect(
            lambda: self.show_add_form('office_equipment', 'service2', self.tableWidget_2, self.treeView_2))
        self.add_btn_3.clicked.connect(
            lambda: self.show_add_form('other', 'service3', self.tableWidget_3, self.treeView_3))
        self.del_btn.clicked.connect(
            lambda: self.delete_row(self.tableWidget_1, self.treeView, 'computers', 'service'))
        self.del_btn_4.clicked.connect(
            lambda: self.delete_row(self.tableWidget_2, self.treeView_2, 'office_equipment', 'service2'))
        self.del_btn_5.clicked.connect(
            lambda: self.delete_row(self.tableWidget_3, self.treeView_3, 'other', 'service3'))
        self.edt_btn.clicked.connect(lambda: self.edit_row(self.tableWidget_1, self.treeView, 'computers'))
        self.edit_btn_3.clicked.connect(lambda: self.edit_row(self.tableWidget_2, self.treeView_2, 'office_equipment'))
        self.edit_btn_4.clicked.connect(lambda: self.edit_row(self.tableWidget_3, self.treeView_3, 'other'))
        self.tableWidget_1.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.serv1_btn.clicked.connect(lambda: self.update_service(1, self.tableWidget_1, self.textEdit, 'service'))
        self.serv2_btn.clicked.connect(lambda: self.update_service(2, self.tableWidget_1, self.textEdit, 'service'))
        self.serv3_btn.clicked.connect(lambda: self.update_service(3, self.tableWidget_1, self.textEdit, 'service'))
        self.serv1_btn_2.clicked.connect(
            lambda: self.update_service(1, self.tableWidget_2, self.textEdit_2, 'service2'))
        self.serv1_btn_3.clicked.connect(
            lambda: self.update_service(1, self.tableWidget_3, self.textEdit_3, 'service3'))
        self.current_computer_id = None
        self.dubll_btn.clicked.connect(
            lambda: self.add_duplicate('computers', 'service', self.tableWidget_1, self.treeView))
        self.dupl_btn_2.clicked.connect(
            lambda: self.add_duplicate('office_equipment', 'service2', self.tableWidget_2, self.treeView_2))
        self.dupl_btn_3.clicked.connect(
            lambda: self.add_duplicate('other', 'service3', self.tableWidget_3, self.treeView_3))
        self.action_3.triggered.connect(self.setting)
        self.action_2.triggered.connect(self.worker_report)
        self.action.triggered.connect(self.close)

    def update_table_computers(self, widget_table, widget_view, table):
        # Обновление таблиц с оборудованием
        con = sqlite3.connect("db/computers.sqlite3")
        cur = con.cursor()
        result = cur.execute(f"""SELECT * FROM {table}""").fetchall()
        widget_table.setColumnCount(8)
        widget_table.setRowCount(0)
        widget_table.setHorizontalHeaderLabels(
            ['id', 'наименование', 'сетевое имя', 'кабинет', 'работник', 'инв_№', 'ip', 'гарантия'])
        for i, row in enumerate(result):
            widget_table.setRowCount(
                widget_table.rowCount() + 1)
            for j, elem in enumerate(row):
                widget_table.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        widget_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        widget_table.setColumnHidden(0, 1)
        widget_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        results = cur.execute(f"SELECT DISTINCT location FROM {table}").fetchall()
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
        widget_view.setModel(model)
        widget_view.selectionModel().selectionChanged.connect(
            lambda: self.filter_data(widget_table, widget_view, table))
        con.close()

    def filter_data(self, widget_table, widget_view, table):
        # фильтрация по локации
        if not (selected_indexes := widget_view.selectedIndexes()):
            return
        selected_location = selected_indexes[0].data()
        db = sqlite3.connect('db/computers.sqlite3')
        cursor = db.cursor()
        if selected_indexes[0].data() == 'все':
            cursor.execute(f"SELECT * FROM {table}")
        else:
            cursor.execute(f"SELECT * FROM {table} WHERE location=?", (selected_location,))
        results = cursor.fetchall()
        if results:
            widget_table.setRowCount(len(results))
            widget_table.setColumnCount(len(results[0]))
            widget_table.setHorizontalHeaderLabels([description[0] for description in cursor.description])
            widget_table.setHorizontalHeaderLabels(
                ['id', 'наименование', 'сетевое имя', 'кабинет', 'работник', 'инв_№', 'ip', 'гарантия'])
            for i, row in enumerate(results):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    widget_table.setItem(i, j, item)
        db.close()

    def show_add_form(self, table1, table2, widget_table, widget_text):
        # запуск окон добавления записей
        self.ex1 = AddComp(table1, table2)
        self.ex1.closed.connect(lambda: self.update_table_computers(widget_table, widget_text, table1))
        self.ex1.show()

    def add_duplicate(self, table1, table2, widget_table, widget_text):
        # запуск окон добавления дубликатов записей
        if not self.current_computer_id:
            QMessageBox.warning(None, "Ошибка", "Вы не выбрали строку")
            return
        self.ex3 = AddComp(table1, table2, id=self.current_computer_id)
        self.ex3.closed.connect(lambda: self.update_table_computers(widget_table, widget_text, table1))
        self.ex3.closed.connect(self.none_computer_id)
        self.ex3.show()

    def none_computer_id(self):
        self.current_computer_id = None

    def show_edit_dialog(self, row, widget_table, widget_text, table):
        # запуск окон редактирования
        self.ex2 = EdtComp(row, widget_table, table)
        self.ex2.closed.connect(lambda: self.update_table_computers(widget_table, widget_text, table))
        self.ex2.show()

    def delete_row(self, widget_table, widget_text, table, table2):
        # удаление записей
        # Получаем индекс выбранной строки
        selected_row = widget_table.currentRow()
        if selected_row == -1:
            # Если ни одна строка не выбрана, выводим сообщение и выходим из функции
            QMessageBox.warning(None, "Ошибка", "Вы не выбрали строку")
            return

        # Получаем ID записи, которую нужно удалить
        id_ = widget_table.item(selected_row, 0).text()

        # Удаляем запись из базы данных
        conn = sqlite3.connect("db/computers.sqlite3")
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE id=?", (id_,))
        cur.execute(f"DELETE FROM {table2} WHERE id=?", (id_,))
        conn.commit()
        conn.close()

        # Удаляем выбранную строку из таблицы
        widget_table.removeRow(selected_row)
        self.update_table_computers(widget_table, widget_text, table)

    def edit_row(self, widget_table, treeView, table):
        # Получаем индекс выбранной строки
        selected_row = widget_table.currentRow()
        if selected_row == -1:
            # Если ни одна строка не выбрана, выводим сообщение и выходим из функции
            QMessageBox.warning(None, "Ошибка", "Вы не выбрали строку")
            return

        # Получаем ID записи, которую нужно изменить
        id_ = widget_table.item(selected_row, 0).text()

        # Открываем соединение с базой данных
        conn = sqlite3.connect("db/computers.sqlite3")
        cur = conn.cursor()

        # Получаем текущие значения полей записи из базы данных
        cur.execute(f"SELECT * FROM {table} WHERE id=?", (id_,))
        row = cur.fetchone()
        # Открываем диалог редактирования записи
        self.show_edit_dialog(row, widget_table, treeView, table)

    def check_date(self, date_str):
        # проверка сроков ТО
        date_format = '%d.%m.%Y'
        today = datetime.datetime.today()
        date = datetime.datetime.strptime(date_str, date_format)
        delta = today - date
        return delta.days

    def update_textedit(self, widget_table, widget_edit, table):
        # отображение информации о сроках ТО
        result = None
        name = None
        # получаем выделенную строку
        selected_row = widget_table.currentRow()
        # получаем содержимое первой ячейки в этой строке
        if widget_table.item(selected_row, 0):
            id = widget_table.item(selected_row, 0).text()
            self.current_computer_id = id
            name = widget_table.item(selected_row, 1).text()
            network_name = widget_table.item(selected_row, 2).text()
            self.conn = sqlite3.connect('db/computers.sqlite3')
            cur = self.conn.cursor()
            result = cur.execute(f"""SELECT * FROM {table} WHERE id={id}""").fetchall()
            self.conn.commit()
            self.conn.close()
        # Если данные найдены, заполняем текстовое поле
        if result:
            widget_edit.clear()
            widget_edit.append(f"Данные для {name}, сетевое имя {network_name}:\n")
            if self.check_date(result[0][1]) > self.service1:
                widget_edit.append(f'Дата ТО_1: <font color="red">{result[0][1]}</font>')
            else:
                widget_edit.append(f'Дата ТО_1: {result[0][1]}')
            if widget_table == self.tableWidget_2 or widget_table == self.tableWidget_3:
                return
            if self.check_date(result[0][2]) > self.service2:
                widget_edit.append(f'Дата ТО_2: <font color="red">{result[0][2]}</font>')
            else:
                widget_edit.append(f'Дата ТО_2: {result[0][2]}')
            if self.check_date(result[0][3]) > self.service3:
                widget_edit.append(f'Дата ТО_3: <font color="red">{result[0][3]}</font>')
            else:
                widget_edit.append(f'Дата ТО_3: {result[0][3]}')
        else:
            widget_edit.setText(f"Для отображения выделите объект")

    def update_service(self, service_number, widget_table, textedit, table):
        # обновление таблиц ТО
        service_column = f'service{service_number}'
        today = datetime.date.today().strftime('%d.%m.%Y')
        con = sqlite3.connect("db/computers.sqlite3")
        cur = con.cursor()
        if self.current_computer_id:
            cur.execute(f"UPDATE {table} SET {service_column} = ? WHERE id = ?", (today, self.current_computer_id))
        con.commit()
        con.close()
        self.update_textedit(widget_table, textedit, table)

    def setting(self):
        # вызов окна настроек ТО
        self.ex4 = SettingWindow()
        self.ex4.closed.connect(self.update_table_computers)
        self.ex4.show()

    def worker_report(self):
        worker, ok = QInputDialog.getText(self, 'Введите фамилию работника', 'Фамилия:')
        if not ok:
            return

        # Открываем соединение с базой данных
        conn = sqlite3.connect('db/computers.sqlite3')
        c = conn.cursor()

        # Выбираем данные из всех таблиц по полю worker
        c.execute(
            f"SELECT type, name, location, worker, inventory, ip, warranty FROM computers WHERE worker = '{worker}'")
        computers_data = c.fetchall()

        c.execute(
            f"SELECT type, name, location, worker, inventory, ip, warranty FROM office_equipment WHERE worker = '{worker}'")
        office_equipment_data = c.fetchall()

        c.execute(f"SELECT type, name, location, worker, inventory, ip, warranty FROM other WHERE worker = '{worker}'")
        other_data = c.fetchall()

        # Закрытие соединения с базой данных
        conn.close()

        # Создаем документ Excel
        workbook = xlsxwriter.Workbook(f'{worker}.xlsx')
        worksheet = workbook.add_worksheet()

        # Записываем данные в документ Excel
        headings = ['Наименование', 'Сетевое имя', 'Расположение', 'Работник', 'Инв.номер', 'ip', 'Гарантия']
        row = 0
        col = 0
        for heading in headings:
            worksheet.write(row, col, heading)
            col += 1

        row = 1
        for data in computers_data:
            col = 0
            for value in data:
                worksheet.write(row, col, value)
                col += 1
            row += 1

        for data in office_equipment_data:
            col = 0
            for value in data:
                worksheet.write(row, col, value)
                col += 1
            row += 1

        for data in other_data:
            col = 0
            for value in data:
                worksheet.write(row, col, value)
                col += 1
            row += 1

        # Настраиваем ширину столбцов
        for col in range(len(headings)):
            worksheet.set_column(col, col, 20)

        # Закрываем документ
        workbook.close()

        # Открываем диалоговое окно для выбора пути сохранения файла
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет",
                                                   f"{worker}.xlsx",
                                                   "Excel Files (*.xlsx)", options=options)

        # Если пользователь выбрал путь, сохраняем файл
        if file_name:
            shutil.move(f'{worker}.xlsx', file_name)
        else:
            os.remove(f'{worker}.xlsx')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
