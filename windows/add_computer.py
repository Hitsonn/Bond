from PyQt5.QtWidgets import QMainWindow, QMessageBox
from forms.Ui_add import AddWindow
import sqlite3
from PyQt5.QtCore import pyqtSignal


class AddComp(QMainWindow, AddWindow):
    closed = pyqtSignal()

    def __init__(self, id=None):
        super().__init__()
        self.id = id
        self.setupUi(self)
        self.pushButton.clicked.connect(self.add)
        self.pushButton_2.clicked.connect(self.exit)
        self.conn = sqlite3.connect('db/computers.sqlite3')
        self.cur = self.conn.cursor()
        if self.id:
            self.cur.execute("SELECT * FROM computers WHERE id=?", (id,))
            result = self.cur.fetchone()
            self.type_edt.setText(result[1])
            self.name_edt.setText(result[2])
            self.location_edt.setText(result[3])
            self.work_edt.setText(result[4])
            self.inventory_edt.setText(result[5])
            self.ip_edt.setText(result[6])
            self.warranty_edt.setText(result[7])

    def add(self):
        typ = self.type_edt.text()
        name = self.name_edt.text()
        location = self.location_edt.text()
        worker = self.work_edt.text()
        inventory = self.inventory_edt.text()
        ip = self.ip_edt.text()
        warranty = self.warranty_edt.text()
        if all([typ, name, location, worker, inventory, ip, warranty]):
            self.cur.execute(
                "INSERT INTO computers (type, name, location, worker, inventory, ip, warranty)"
                " VALUES (?,?,?,?,?,?,?)", (typ, name, location, worker, inventory, ip, warranty))
            last_row_id = self.cur.lastrowid
            self.cur.execute(
                "INSERT INTO service (id, service1, service2, service3) VALUES (?,?,?,?)",
                (last_row_id, '01.09.2020', '01.09.2020', '01.09.2020'))
            self.conn.commit()
            self.conn.close()

            self.close()
        else:
            QMessageBox.warning(None, "Ошибка", "Не все данные заполнены")
            return

    def exit(self):
        self.close()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
