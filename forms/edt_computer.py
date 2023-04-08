import sys
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from forms.Edt_windows import EdtWindow
import sqlite3


class EdtComp(QMainWindow, EdtWindow):
    closed = pyqtSignal()

    def __init__(self, row):
        super().__init__()
        self.row = row
        self.setupUi(self)
        self._id, typ, name, location, worker, inventory, ip, warranty, service, nex = self.row
        self.type_edt.setText(typ)
        self.name_edt.setText(name)
        self.location_edt.setText(location)
        self.work_edt.setText(worker)
        self.inventory_edt.setText(inventory)
        self.ip_edt.setText(ip)
        self.warranty_edt.setText(warranty)
        self.servece_edt.setText(service)
        self.next_edt.setText(nex)
        self.pushButton.clicked.connect(self.save)
        self.pushButton_2.clicked.connect(self.exit)

    def save(self):
        typ = self.type_edt.text()
        name = self.name_edt.text()
        location = self.location_edt.text()
        worker = self.work_edt.text()
        inventory = self.inventory_edt.text()
        ip = self.ip_edt.text()
        warranty = self.warranty_edt.text()
        service = self.servece_edt.text()
        nex = self.next_edt.text()
        self.close()
        edited_row = typ, name, location, worker, inventory, ip, warranty, service, nex, self._id
        if edited_row is None:
            # Если диалог был закрыт без сохранения, выходим из функции
            return
        print(edited_row)
        # Открываем соединение с базой данных
        conn = sqlite3.connect("db/computers.sqlite3")
        cur = conn.cursor()
        # Обновляем запись в базе данных
        cur.execute(
            "UPDATE computers SET type=?, name=?, location=?, worker=?, inventory=?, ip=?, warranty=?, service=?, next_service=? WHERE id=?",
            (edited_row))
        conn.commit()
        conn.close()
        self.close()
        # Нужно организовать обновление таблица в главном окне

    def exit(self):
        self.close()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

