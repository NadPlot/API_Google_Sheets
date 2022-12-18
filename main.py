import os
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
load_dotenv()

# ID гугл таблицы, куда вносим данные
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')


# Создаем Сервис-объект для работы с Google-таблицами
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE') # переменная с именем файла с закрытым ключом, полученый при создании Сервисного аккаунта

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)  # Сервис-объект для работы с Google-таблицами


# Создание нового документа Google-таблицы
spreadsheet = service.spreadsheets().create(body = {
    'properties': {'title': 'Logs', 'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Sheet01',
                               'gridProperties': {'rowCount': 8, 'columnCount': 5}}}]
}).execute()


# Предоставление доступа на чтение к новому документу
driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth)
shareRes = driveService.permissions().create(
    fileId = spreadsheet['spreadsheetId'],
    body = {'type': 'anyone', 'role': 'writer'},  # доступ на редактирование кому угодно
    fields = 'id'
).execute()


# Заполнение таблицы данными
results = service.spreadsheets().values().append(spreadsheetId = '1613BR-ljmLeW82XdQaWo3cu3CuMw59jRA2GIDjISGpo', range = "Sheet1!A5:A5", valueInputOption = "USER_ENTERED", body = {"values": [["Логи кластера №1"]]}).execute()


results = service.spreadsheets().values().batchUpdate(spreadsheetId = spreadsheet['spreadsheetId'], body = {
    "valueInputOption": "USER_ENTERED",
    "data": [
        {"range": "Sheet01!A1:A1",
         "values": [["Логи кластера №1"]]},
    ]
}).execute()

