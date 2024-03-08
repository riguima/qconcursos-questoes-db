from pathlib import Path

from PySide6 import QtCore, QtWidgets

from qconcursos_questoes_db.browser import Browser


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 200)
        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

        self.browser = Browser(headless=False)
        self.browser.make_login()

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
        self.main_layout.addLayout(self.destination_folder_layout)
        self.main_layout.addLayout(self.url_layout)
        self.main_layout.addWidget(self.generate_db_button)

    @QtCore.Slot()
    def choose_destination_folder(self):
        self.destination_folder_input.setText(
            QtWidgets.QFileDialog.getExistingDirectory()
        )

    @QtCore.Slot()
    def generate_db(self):
        result = self.browser.get_questions(self.url_input.text())
        if self.destination_folder_input.text():
            folder = Path(self.destination_folder_input.text())
        else:
            folder = Path('.')
        with open(folder / 'db.txt', 'w') as f:
            for question in result:
                for key, value in question.items():
                    if key == 'Alternativas' and '(A) \n(B)' in value:
                        f.write('Alternativas com imagens\n\n')
                    if key == 'Questão':
                        f.write(f'{key}:\n{value}\n\n')
                    else:
                        f.write(f'{key}: {value}\n\n')
                f.write('=' * 50)
                f.write('\n\n')
            f.write('Gabarito:\n\n')
            for question in result:
                if '(A) \n(B)' in question['Alternativas']:
                    f.write(f'{question["Número"]} - {question["Resposta"]} (Alternativas com imagens)\n')
                else:
                    f.write(f'{question["Número"]} - {question["Resposta"]}\n')
        self.message_box.setText('Finalizado!')
        self.message_box.show()
