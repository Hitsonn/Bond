import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from forms.Add_window import AddWindow
import sqlite3


class AddComp(QMainWindow, AddWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.add)
        self.pushButton_2.clicked.connect(self.exit)

    def add(self):
        typ = self.type_edt.text()
        name = self.name_edt.text()
        location = self.location_edt.text()
        worker = self.work_edt.text()
        inventory = self.inventory_edt.text()
        ip = self.ip_edt.text()
        warranty = self.warranty_edt.text()
        service = self.servece_edt.text()
        nex = self.next_edt.text()

        conn = sqlite3.connect('db/computers.sqlite3')
        cur = conn.cursor()
        cur.execute("INSERT INTO computers (type, name, location, worker, inventory, ip, warranty, service, next_service)"
                    " VALUES (?,?,?,?,?,?,?,?,?)", (typ, name, location, worker, inventory, ip, warranty, service, nex))
        conn.commit()
        conn.close()
        # Нужно организовать обновление таблица в главном окне


    def exit(self):
        self.close()

