from itertools import count
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets
from selenium.common.exceptions import StaleElementReferenceException
from sqlalchemy import select

from qconcursos_questoes_db.browser import Browser
from qconcursos_questoes_db.database import Session
from qconcursos_questoes_db.models import Question


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 250)
        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

        self.browser = Browser(headless=False)

        self.message_box = QtWidgets.QMessageBox()

        self.login_label = QtWidgets.QLabel('Login')
        self.login_input = QtWidgets.QLineEdit()
        self.login_layout = QtWidgets.QHBoxLayout()
        self.login_layout.addWidget(self.login_label)
        self.login_layout.addWidget(self.login_input)

        self.password_label = QtWidgets.QLabel('Senha')
        self.password_input = QtWidgets.QLineEdit()
        self.password_layout = QtWidgets.QHBoxLayout()
        self.password_layout.addWidget(self.password_label)
        self.password_layout.addWidget(self.password_input)

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

        self.page_label = QtWidgets.QLabel('Página')
        self.page_input = QtWidgets.QLineEdit()
        self.page_input.setText('1')
        self.page_input.setValidator(QtGui.QIntValidator())
        self.page_layout = QtWidgets.QHBoxLayout()
        self.page_layout.addWidget(self.page_label)
        self.page_layout.addWidget(self.page_input)

        self.generate_db_button = QtWidgets.QPushButton('Gerar DB')
        self.generate_db_button.clicked.connect(self.generate_db)

        self.scraping_layout = QtWidgets.QVBoxLayout()
        self.scraping_layout.addLayout(self.login_layout)
        self.scraping_layout.addLayout(self.password_layout)
        self.scraping_layout.addLayout(self.destination_folder_layout)
        self.scraping_layout.addLayout(self.url_layout)
        self.scraping_layout.addLayout(self.page_layout)
        self.scraping_layout.addWidget(self.generate_db_button)

        self.subject_label = QtWidgets.QLabel('Disciplina')
        self.subject_combobox = QtWidgets.QComboBox()
        self.subject_layout = QtWidgets.QHBoxLayout()
        self.subject_layout.addWidget(self.subject_label)
        self.subject_layout.addWidget(self.subject_combobox)

        self.banking_label = QtWidgets.QLabel('Banca')
        self.banking_combobox = QtWidgets.QComboBox()
        self.banking_layout = QtWidgets.QHBoxLayout()
        self.banking_layout.addWidget(self.banking_label)
        self.banking_layout.addWidget(self.banking_combobox)

        self.organ_label = QtWidgets.QLabel('Órgão')
        self.organ_combobox = QtWidgets.QComboBox()
        self.organ_layout = QtWidgets.QHBoxLayout()
        self.organ_layout.addWidget(self.organ_label)
        self.organ_layout.addWidget(self.organ_combobox)

        self.year_label = QtWidgets.QLabel('Ano')
        self.year_combobox = QtWidgets.QComboBox()
        self.year_layout = QtWidgets.QHBoxLayout()
        self.year_layout.addWidget(self.year_label)
        self.year_layout.addWidget(self.year_combobox)

        self.generate_txt_button = QtWidgets.QPushButton('Gerar DB TXT')
        self.generate_txt_button.clicked.connect(self.generate_db_txt)

        self.generate_txt_layout = QtWidgets.QVBoxLayout()
        self.generate_txt_layout.addLayout(self.subject_layout)
        self.generate_txt_layout.addLayout(self.banking_layout)
        self.generate_txt_layout.addLayout(self.organ_layout)
        self.generate_txt_layout.addLayout(self.year_layout)
        self.generate_txt_layout.addWidget(self.generate_txt_button)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.addLayout(self.scraping_layout)
        self.main_layout.addLayout(self.generate_txt_layout)

        self.update_comboboxes()

    @QtCore.Slot()
    def choose_destination_folder(self):
        self.destination_folder_input.setText(
            QtWidgets.QFileDialog.getExistingDirectory()
        )

    @QtCore.Slot()
    def generate_db(self):
        self.browser.make_login(
            self.login_input.text(), self.password_input.text()
        )
        for page in count(int(self.page_input.text())):
            self.browser.driver.get(f'{self.url_input.text()}&page={page}')
            while True:
                try:
                    result = self.browser.get_questions()
                    break
                except StaleElementReferenceException:
                    continue
            for question in result:
                session = Session()
                print(question['Número'])
                query = select(Question).where(
                    Question.numero == question['Número']
                )
                if session.scalars(query).first() is None:
                    question_model = Question(
                        numero=question['Número'],
                        questao=question['Questão'],
                        resposta=question['Resposta'],
                        materia=question['Matéria'],
                        ano=int(question['Ano']),
                        banca=question['Banca'],
                        orgao=question['Órgão'],
                        prova=question['Prova'],
                        alternativas=question['Alternativas'],
                        imagens=question['Imagens'],
                    )
                    session.add(question_model)
                    session.commit()
                session.close()
            print('Pagina:', page)
        self.message_box.setText('Finalizado!')
        self.message_box.show()

    @QtCore.Slot()
    def generate_db_txt(self):
        session = Session()
        query = select(Question)
        if self.subject_combobox.currentText() != 'Todas':
            query = query.where(
                Question.materia == self.subject_combobox.currentText()
            )
        if self.banking_combobox.currentText() != 'Todas':
            query = query.where(
                Question.banca == self.banking_combobox.currentText()
            )
        if self.organ_combobox.currentText() != 'Todos':
            query = query.where(
                Question.orgao == self.organ_combobox.currentText()
            )
        if self.year_combobox.currentText() != 'Todos':
            query = query.where(
                Question.ano == self.year_combobox.currentText()
            )
        if self.destination_folder_input.text():
            folder = Path(self.destination_folder_input.text())
        else:
            folder = Path('.')
        with open(folder / 'db.txt', 'w', encoding='utf-8') as f:
            for question in session.scalars(
                query.where(Question.imagens == '')
            ).all():
                f.write(
                    f'Questão {question.numero}. ({question.banca} - {question.orgao} - {question.prova} - {question.ano} - {question.materia})\n'
                )
                f.write(question.questao + '\n\n')
                f.write(f'Alternativas:\n{question.alternativas}\n\n')
                f.write(f'Resposta: {question.resposta}\n\n')
                f.write('=' * 50)
                f.write('\n\n')
            f.write('Gabarito:\n\n')
            for question in session.scalars(
                query.where(Question.imagens == '')
            ).all():
                f.write(f'{question.numero} - {question.resposta}\n')
            if session.scalars(query.where(Question.imagens != '')).all():
                f.write('\nQuestões com imagens:\n\n')
                for question in session.scalars(
                    query.where(Question.imagens != '')
                ).all():
                    f.write(f'{question.numero} - {question.resposta}\n')
        self.message_box.setText('Finalizado!')
        self.message_box.show()
        session.close()

    def update_comboboxes(self):
        session = Session()
        questions = session.scalars(select(Question)).all()
        self.subject_combobox.clear()
        self.subject_combobox.addItem('Todas')
        self.subject_combobox.addItems(
            list(set([q.materia for q in questions]))
        )
        self.banking_combobox.clear()
        self.banking_combobox.addItem('Todas')
        self.banking_combobox.addItems(list(set([q.banca for q in questions])))
        self.organ_combobox.clear()
        self.organ_combobox.addItem('Todos')
        self.organ_combobox.addItems(list(set([q.orgao for q in questions])))
        self.year_combobox.clear()
        self.year_combobox.addItem('Todos')
        self.year_combobox.addItems(list(set([str(q.ano) for q in questions])))
        session.close()
