from pathlib import Path

from PySide6 import QtCore, QtWidgets


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 300)
        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

        self.message_box = QtWidgets.QMessageBox()

        self.destination_folder_label = QtWidgets.QLabel('Pasta')
        self.destination_folder_input = QtWidgets.QLineEdit()
        self.destination_folder_input.setReadOnly(True)
        self.destination_folder_button = QtWidgets.QPushButton('Selecionar')
        self.destination_folder_button.clicked.connect(
            self.choose_destination_folder
        )
        self.destination_folder_layout = QtWidgets.QHBoxLayout()
        self.destination_folder_layout.addWidget(self.destination_folder_label)
        self.destination_folder_layout.addWidget(self.destination_folder_input)
        self.destination_folder_layout.addWidget(
            self.destination_folder_button
        )

        self.url_label = QtWidgets.QLabel('Link')
        self.url_input = QtWidgets.QLineEdit()
        self.url_layout = QtWidgets.QHBoxLayout()
        self.url_layout.addWidget(self.url_label)
        self.url_layout.addWidget(self.url_input)

        self.generate_db_button = QtWidgets.QPushButton('Gerar DB')
        self.generate_db_button.clicked.connect(self.generate_db)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.url_layout)

    @QtCore.Slot()
    def choose_destination_folder(self):
        self.destination_folder_input.setText(
            QtWidgets.QFileDialog.getExistingDirectory()
        )

    @QtCore.Slot()
    def generate_db(self):
        result = ''
        if self.destination_folder_input.text():
            folder = Path(self.destination_folder_input.text())
        else:
            folder = Path('.')
        with open(folder / 'result_db.txt') as f:
            f.write(result)
        self.message_box.setText('Finalizado!')
        self.message_box.show()
