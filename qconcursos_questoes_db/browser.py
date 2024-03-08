import re
import string
from time import sleep

from rich import print
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from qconcursos_questoes_db.config import config


class Browser:
    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
        self.driver = Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def make_login(self):
        self.driver.get('https://www.qconcursos.com/conta/entrar')
        self.find_element('#login_email').send_keys(config['LOGIN'])
        self.find_element('#login_password').send_keys(config['PASSWORD'])
        self.find_element('input[type=submit]').click()
        try:
            self.find_element('a[title="Sair"]')
        except TimeoutException:
            return 'Login Inválido'

    def get_questions(self, url):
        self.driver.get(url)
        result = []
        while True:
            for question in self.find_elements('.q-question'):
                subject = ' - '.join(
                    [
                        e.get_attribute('textContent').strip()
                        for e in self.find_elements(
                            '.q-question-breadcrumb a', element=question
                        )
                    ]
                )
                self.driver.execute_script(
                    'arguments[0].click()',
                    self.find_element('.q-option-item', element=question),
                )
                try:
                    self.driver.execute_script(
                        'arguments[0].click()',
                        self.find_element('.js-answer-btn', element=question),
                    )
                except TimeoutException:
                    continue
                sleep(1)
                feedback = (
                    self.find_element('.q-answer-feedback', element=question)
                    .get_attribute('textContent')
                    .split(':')[-1]
                    .strip()
                )
                if feedback:
                    answer = self.find_element(
                        '.js-question-right-answer', element=question
                    ).get_attribute('textContent')
                else:
                    option = self.find_element(
                        '.q-option-item', element=question
                    ).get_attribute('textContent')
                    answer = (
                        option
                        if option
                        else self.find_element('.q-item-enum').get_attribute(
                            'textContent'
                        )
                    )
                infos = [
                    ':'.join(
                        e.get_attribute('textContent').split(':')[1:]
                    ).strip()
                    for e in self.find_elements(
                        '.q-question-info span', element=question
                    )
                ]
                question_text = (
                    self.find_element(
                        '.q-question-enunciation', element=question
                    )
                    .get_attribute('textContent')
                    .strip()
                )
                alternatives = '\n'
                for e, element in enumerate(
                    self.find_elements(
                        '.js-alternative-content', element=question
                    )
                ):
                    if (
                        e
                        == len(
                            self.find_elements(
                                '.q-option-item', element=question
                            )
                        )
                        - 1
                    ):
                        alternatives += f'({string.ascii_uppercase[e]}) {element.get_attribute("textContent").strip()}'
                    else:
                        alternatives += f'({string.ascii_uppercase[e]}) {element.get_attribute("textContent").strip()}\n'
                result.append(
                    {
                        'Número': self.find_element('.q-id', element=question)
                        .get_attribute('textContent')
                        .strip(),
                        'Questão': re.sub(r'[ ]{2,}', ' ', question_text),
                        'Alternativas': alternatives,
                        'Resposta': answer,
                        'Matéria': re.sub(r'\s+,', '', subject),
                        'Ano': infos[0],
                        'Banca': infos[1],
                        'Órgão': infos[2],
                        'Prova': re.sub(r'\s+\|$', '', infos[3]),
                        'Tem Imagens': bool(
                            question.find_elements(
                                By.CSS_SELECTOR, '.q-question-enunciation img'
                            )
                        )
                        or '(A) \n(B)' in alternatives,
                    }
                )
                print(result[-1])
            try:
                self.driver.execute_script(
                    'arguments[0].click()', self.find_element('.q-next')
                )
                sleep(10)
            except TimeoutException:
                break
        return result

    def find_element(self, selector, element=None, wait=10):
        return WebDriverWait(element or self.driver, wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def find_elements(self, selector, element=None, wait=10):
        return WebDriverWait(element or self.driver, wait).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
        )
