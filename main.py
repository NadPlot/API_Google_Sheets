import os
import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
load_dotenv()

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')  # ID гугл таблицы, куда вносим данные (для уже существующей)
SHEET_ID = os.getenv('SHEET_ID')  # ID листа таблицы
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')  # переменная с именем файла JSON с закрытым ключом, полученый при создании Сервисного аккаунта
LOG_FILE = os.getenv('LOG_FILE')  # Путь и Имя файла с логами


class NotSetTableID(Exception):
    pass

class Tables:
    def __init__(self, jsonFileName):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(jsonFileName, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('sheets', 'v4', http = self.httpAuth)  # Сервис-объект для работы с Google-таблицами
        self.driveService = discovery.build('drive', 'v3', http = self.httpAuth)  # Предоставление доступа на чтение к google таблице
        self.tableID = None  # для получения ID таблицы


    # Создание новой Google-таблицы и открытие доступа к ней
    def create_table(self, title):
        table = self.service.spreadsheets().create(body = {
            'properties': {'title': title, 'locale': 'ru_RU'},
            'sheets': [{'properties': {'sheetType': 'GRID','sheetId': 0}}]
            }).execute()
        self.tableID = table['spreadsheetId']
        shareRes = self.driveService.permissions().create(
            fileId = table['spreadsheetId'],
            body = {'type': 'anyone', 'role': 'writer'},  # доступ на редактирование кому угодно
            fields = 'id'
        ).execute()


    # Заполнение таблицы данными из файла с логами
    def add_data(self):
        if self.tableID is None:
            self.tableID = SPREADSHEET_ID
        with open(LOG_FILE) as f:
            results = self.service.spreadsheets().values().append(
                    spreadsheetId = self.tableID, range = "Лист1!A1:A1", valueInputOption = "USER_ENTERED", body = {"values": [[f.readline()]]}).execute()

    # Получение URL таблицы
    def get_table_URL(self):
        if self.tableID is None:
            self.tableID = SPREADSHEET_ID
        return 'https://docs.google.com/spreadsheets/d/' + self.tableID + '/edit#gid='


table = Tables(CREDENTIALS_FILE)
if table:
    print('Подключено к google-таблицам')
else:
    print('Что-то пошло не так')
if table.tableID is None:
    q = input('Создать новую таблицу? "Y/N?":')
    if q == 'Y':
        table.create_table(input('Введите имя новой таблицы'))
    else:
        table.add_data()
        print(f'Данные внесены в таблицу, посмотреть таблицу по адресу:', table.get_table_URL())


